# Container image that runs your code
FROM python:3.11

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY security_scan.py /security_scan.py
COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

RUN ls
RUN export PULL_REQUEST_NUMBER=$1
RUN export GITHUB_REPOSITORY=$2
RUN export SIXPILLARS_API_TOKEN=$3
RUN export TIMEOUT_SECONDS=$4
RUN export URL=$5

# Code file to execute when the docker container starts up (`security_scan.py`)
ENTRYPOINT ["python", "/security_scan.py"] 
