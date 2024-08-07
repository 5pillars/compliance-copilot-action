import os
import base64
import json
import requests
from github import Github
import time

# Initialize GitHub client
g = Github(os.getenv('GITHUB_TOKEN'))

# Get repository, pull request ID from environment variables set by GitHub Actions
repo_name = os.getenv('GITHUB_REPOSITORY')
pr_number = int(os.getenv('PULL_REQUEST_NUMBER'))  # GitHub Actions should set this as an environment variable
try:
    print("Repository name: ", repo_name)
    print("PR #: ", pr_number)
    repo = g.get_repo(repo_name)
    pull_request = repo.get_pull(pr_number)
except Exception as error:
    print(str(error))
    raise Exception("Could not find the repository/PR")

SIXPILLARS_API_TOKEN = os.getenv("SIXPILLARS_API_TOKEN")
SIXPILLARS_API_UPLOAD_URL = os.getenv("URL") + "/templatescanner/upload-template"
SIXPILLARS_API_RESULT_URL = os.getenv("URL") + "/templatescanner/result"

def encode_file_content(content: bytes):
    """Encode file contents in Base64."""
    return base64.b64encode(content).decode()

def upload_file(fileName, content):
    """Upload Base64-encoded file content."""
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {SIXPILLARS_API_TOKEN}"
    }
    baseFileName = os.path.basename(fileName)
    data = {
        "fileName": baseFileName,
        "fileString": content,
        "fileAlias": f"Github-Action-Scan - {fileName}"
    }
    response = requests.post(
        SIXPILLARS_API_UPLOAD_URL, 
        headers=headers, 
        data=json.dumps(data)
    )
    if response.status_code == 200:
        print(f"Uploaded {fileName} successfully.")
        return 0 # success
    else:
        raise Exception(f"Failed to upload {fileName}. Status code: {response.status_code}, Response: {response.text}")

def get_file_summary_text(summaryObj):
    """
    Return a summary string based on the dictionary containing the details.

    :param summaryObj: The dictionary for the summary report.
    """
    fileName = summaryObj["filename"]
    summaryId = str(summaryObj["summaryId"])
    passed = str(summaryObj["passed"])
    critical = str(summaryObj["critical"])
    high = str(summaryObj["high"])
    medium = str(summaryObj["medium"])
    low = str(summaryObj["low"])
    failed = str(summaryObj["failed"])
    message = f"""Security report summary from 6pillars.ai for file {fileName}:
        Passed Checks: {passed}
        Failed Checks: {failed}
        Critical Severity: {critical}
        High Severity: {high}
        Medium Severity: {medium}
        Low Severity: {low}
    You can see the full report at https://app.6pillars.ai/template-scanner-results?id={summaryId}
    """
    return message

def get_severity_emoji(severity):
    """
    Get a different coloured emoji based on the severity level.

    :param severity: A string for the severity level.
    """
    emoji = ""
    if severity.lower() == "critical":
        emoji = ":red_circle:"
    elif severity.lower() == "high":
        emoji = ":orange_circle:"
    elif severity.lower() == "medium":
        emoji = ":yellow_circle:"
    elif severity.lower() == "low":
        emoji = ":green_circle:"
    return emoji

def post_review_comments(resultsObj, fileName):
    """
    Post review comments onto the Github PR for each finding.

    :param fileName: A string for the name of the file to get the result for.
    :param resultsObj: The list of results from the API response.
    """
    commentHashMap = {}
    commit_id = pull_request.head.sha # Get the latest commit SHA in the PR
    commit = repo.get_commit(sha=commit_id)  # Get the commit instance using the commit SHA

    for result in resultsObj:
        fileLineRange = result.get("file_line_range")
        description = result.get("description")
        severity = result.get("severity")
        checkId = result.get("id")
        severityEmoji = get_severity_emoji(severity)
        if fileLineRange:
            startLine = int(fileLineRange.split("-")[0])
            if severityEmoji != "":
                comment_body = f"{checkId} - {severity} {severityEmoji} - {description}"
            else:
                comment_body = f"{checkId} - {severity} - {description}"
            if not commentHashMap.get(fileLineRange):
                commentHashMap[fileLineRange] = []
            commentHashMap[fileLineRange].append(comment_body)

    for fileLine in commentHashMap.keys():
        try:
            commentList = commentHashMap[fileLine]
            longComment = "\n".join(f"* {comment}" for comment in commentList)  # Format each comment as a dotpoint
            startLine = int(fileLine.split("-")[0])
            print("PR Review Comment posted to PR #{}, Commit ID: {}".format(pr_number, commit_id))
            pull_request.create_review_comment(longComment, commit, fileName, line=startLine)
        except Exception as error:
            print("Error posting PR comment:", error)

def get_file_results(fileName, fileAlias):
    """
    Get the results from the API for this specific file name and alias.

    :param fileName: A string for the name of the file to get the result for.
    :param fileAlias: A string for the alias of the file to get the result for.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SIXPILLARS_API_TOKEN}",
    }
    baseFileName = os.path.basename(fileName)
    data = {
        "fileAlias": fileAlias, 
        "fileName": baseFileName
    }
    response = requests.post(
        SIXPILLARS_API_RESULT_URL, 
        headers=headers, 
        data=json.dumps(data)
    )
    jsonResponse = response.json()
    if jsonResponse.get("msg") == "success":
        summaryMessage = get_file_summary_text(jsonResponse["summary"])
        pull_request.create_issue_comment(summaryMessage)
        print("Issue Comment posted to PR #{}".format(pr_number))
        post_review_comments(jsonResponse["results"], fileName)
        return 0 # success
    else:
        return 1 # error

def check_file_results(file_queue):
    """
    Check the results for each file in the queue and return the list of files still pending results.

    :param file_queue: List of files to check.
    """
    remaining_files = []
    for file_name in file_queue:
        file_alias = f"Github-Action-Scan - {file_name}"
        print(f"Getting file results: {file_name}")
        status_code = get_file_results(file_name, file_alias)
        if status_code != 0:
            remaining_files.append(file_name)
    if remaining_files:
        print(f"Could not get file results for: {remaining_files}")
    return remaining_files

def wait_and_check_results(uploaded_files):
    """
    Periodically check the scan results of uploaded files.

    :param uploaded_files: List of file names that have been uploaded.
    """
    seconds = 60 * 5  # 5 minutes
    file_queue = [*uploaded_files]  # Start with all uploaded files
    for i in range(4):  # Every 5 minutes, try the request up to 20 minutes
        time.sleep(seconds)
        print(f"Paused: {seconds * (i + 1)} seconds")
        file_queue = check_file_results(file_queue)

def process_files(file_names, pull_request, repo):
    """
    Process and upload files, returning a list of successfully uploaded file names.

    :param file_names: List of file names to be processed.
    :param pull_request: An object representing the GitHub pull request.
    :param repo: The repository from which files are fetched.
    """
    uploaded_files = []
    for file_name in file_names:
        try:
            print(f"Processing file: {file_name}")
            content_file = repo.get_contents(file_name, ref=pull_request.head.ref)
            encoded_content = encode_file_content(content_file.decoded_content)
            status_code = upload_file(file_name, encoded_content)
            if status_code == 0:
                uploaded_files.append(file_name)
        except Exception as e:
            print(f"Error processing file {file_name}: {str(e)}")
    return uploaded_files

def process_pull_request(pull_request, repo):
    """
    Process each file in the pull request that matches specific extensions and
    manage the upload and scanning of these files.

    :param pull_request: An object representing the GitHub pull request.
    :param repo: The repository from which files are fetched.
    """
    all_file_names = [
        file.filename for file in pull_request.get_files()
        if file.filename.endswith(('.tf', '.ts', '.json'))
    ]
    uploaded_files = process_files(all_file_names, pull_request, repo)

    # Wait and check the scan results for uploaded files
    wait_and_check_results(uploaded_files)

if __name__ == "__main__":
    process_pull_request(pull_request, repo)
