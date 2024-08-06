# Container image that runs your code
FROM python:3.11

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY . /

RUN pip install -r requirements.txt

RUN export PULL_REQUEST_NUMBER=$1
RUN export GITHUB_REPOSITORY=$2
RUN export SIXPILLARS_API_TOKEN=$3
RUN export TIMEOUT_SECONDS=$4

# Code file to execute when the docker container starts up (`security_scan.py`)
CMD ["python", "./security_scan.py"] 
