# Container image that runs your code
FROM python:3.11

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY . /

RUN pip install -r requirements.txt

# Code file to execute when the docker container starts up (`security_scan.py`)
CMD ["python", "./security_scan.py"] 
