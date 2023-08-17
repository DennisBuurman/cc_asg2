# Deploy with: gcloud functions deploy chunkify --region europe-west1 --entry-point hello_gcs --runtime python39 --trigger-bucket cc-asg2-documents

from google.cloud import storage
from google.cloud import firestore
from google.cloud import pubsub_v1
import json
import sys

PROJECT_ID = 'cc-asg2'
PROJECT_ID = 'cc-asg2'
PALINDROME_TOPIC_ID = 'cc-asg2-palindrome'
SORT_TOPIC_ID = 'cc-asg2-sort'
TARGET_CHUNK_SIZE = 65536

def process_file(file):

     # Download the file as a byte sequence
     storage_client = storage.Client()
     bucket = storage_client.bucket(file['bucket'])
     blob = bucket.blob(file['name'])
     contents = blob.download_as_bytes()

     # Process list of lines to determine chunk offsets & sizes
     lines = contents.splitlines(True)
     chunk_list = []
     chunk_offset = 0
     chunk_size = 0
     chunk_id = 0
     for line in lines:
          chunk_size += len(line)
          if (chunk_size >= TARGET_CHUNK_SIZE):
               chunk = {
                    "chunk_id": chunk_id,
                    "offset": chunk_offset,
                    "size": chunk_size,
               }
               chunk_list.append(chunk)
               chunk_offset += chunk_size
               chunk_id += 1
               chunk_size = 0
     if chunk_size > 0:
          chunk = {
               "chunk_id": chunk_id,
               "offset": chunk_offset,
               "size": chunk_size,
          }
          chunk_list.append(chunk)
          chunk_id += 1


     # Package into a job
     job = {
          "doc_id": file['name'],
          "num_chunks": chunk_id,
          "done_sort_chunks": 0,
          "done_palindrome_chunks": 0,
          "sort_done": False,
          "palindrome_done": False,
          "chunks": chunk_list,
     }

     return job

def upload_job(job, job_id):
     db = firestore.Client(project=PROJECT_ID)
     print("JOB SIZE: ", sys.getsizeof(job))
     print("JOB LENGTH: ", len(json.dumps(job)))
     print("JOB: ", job)
     print("JOB ID SIZE: ", sys.getsizeof(job_id))
     print("JOB_ID: ", job_id)
     doc_ref = db.collection('jobs').document(job_id)
     doc_ref.set(job)

def publish_job(job):
     publisher = pubsub_v1.PublisherClient()
     palindrome_topic_path = publisher.topic_path(PROJECT_ID, PALINDROME_TOPIC_ID)
     sort_topic_path = publisher.topic_path(PROJECT_ID, SORT_TOPIC_ID)
     doc_id = job['doc_id']
     chunk_list = job['chunks']

     for chunk in chunk_list:
          sort_msg = {
               "doc_id": doc_id,
               "chunk": chunk,
          }
          palin_msg = {
               "doc_id": doc_id,
               "chunk": chunk,
          }
          palin_bytes = json.dumps(palin_msg).encode('utf-8')
          sort_bytes = json.dumps(sort_msg).encode('utf-8')
          publisher.publish(palindrome_topic_path, palin_bytes)
          publisher.publish(sort_topic_path, sort_bytes)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
     

def chunkify(event, context):
    file = event
    print(f"Processing file with extra style: {file['name']}.")
    job = process_file(file)
    upload_job(job, file['name'])
    publish_job(job)
    print("Done!")