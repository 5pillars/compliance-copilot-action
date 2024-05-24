import os
import base64
import json
import requests
from github import Github
import time
import sys

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
SIXPILLARS_API_UPLOAD_URL = os.getenv("SIXPILLARS_API_UPLOAD_URL")
SIXPILLARS_API_RESULT_URL = os.getenv("SIXPILLARS_API_RESULT_URL")

def encode_file_content(content: bytes):
    """Encode file contents in Base64."""
    return base64.b64encode(content).decode()

def upload_file(fileName, content):
    """Upload Base64-encoded file content to an example API."""
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
    else:
        raise Exception(f"Failed to upload {fileName}. Status code: {response.status_code}, Response: {response.text}")

def get_file_summary_text(summaryObj):
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
    try:
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
        print("Status Code", response.status_code)
        obj = json.loads(response.text)
        summaryMessage = get_file_summary_text(obj["summary"])
        pull_request.create_issue_comment(summaryMessage)
        print("Issue Comment posted to PR #{}".format(pr_number))
        post_review_comments(obj["results"], fileName)
    except Exception as error:
        print(str(error))

def process_pull_request():
    """Process each file in the pull request."""
    for file in pull_request.get_files():
        fileName = file.filename
        if fileName.endswith(('.tf', '.ts', '.json')):  # Add other IaC file extensions as needed
            print(f"Processing file: {fileName}")
            # Fetch the actual file content
            content_file = repo.get_contents(fileName, ref=pull_request.head.ref)
            encoded_content = encode_file_content(content_file.decoded_content)
            upload_file(fileName, encoded_content)
    # Wait for 5 mins
    print("Waiting for templates to be uploaded and scanned....")
    seconds = 60
    for i in range(2):
        time.sleep(seconds)
        print("paused: " + str(seconds * (i + 1)) + " seconds")
    for file in pull_request.get_files():
        fileName = file.filename
        fileAlias = f"Github-Action-Scan - {fileName}"
        if fileName.endswith(('.tf', '.ts', '.json')):
            print(f"Getting file results: {fileName}")
            get_file_results(fileName, fileAlias)

if __name__ == "__main__":
    process_pull_request()
