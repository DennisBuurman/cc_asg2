FROM python:3.8-slim

# Working directory: path to palindrome folder in cc-asg2 project
WORKDIR ~/cc-asg2/backend/palindrome/ 

# Copies the palindrome.py file from WORKDIR to the container
COPY palindrome.py ./

# Install packages
RUN pip install google-cloud-pubsub
RUN pip install google-cloud-storage
RUN pip install google-api-core
RUN pip install google-cloud-firestore

# Run the sort.py file
ENTRYPOINT ["python", "-u", "palindrome.py"]