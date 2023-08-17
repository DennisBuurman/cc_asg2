FROM python:3.8-slim

# Working directory: path to reduce folder in cc-asg2 project
WORKDIR ~/cc-asg2/backend/reduce/ 

# Copies the reduce.py file from WORKDIR to the container
COPY reduce.py ./

# Install packages
RUN pip install google-cloud-pubsub
RUN pip install google-cloud-storage
RUN pip install google-api-core
RUN pip install google-cloud-firestore

# Run the sort.py file
ENTRYPOINT ["python", "-u", "reduce.py"]