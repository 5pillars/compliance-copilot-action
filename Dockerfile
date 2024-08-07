# Container image that runs your code
FROM python:3.11

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY security_scan.py /security_scan.py
COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

# Code file to execute when the docker container starts up (`security_scan.py`)
ENTRYPOINT ["python", "/security_scan.py"] 
