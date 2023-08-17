"""
Reduce worker program created by Jochem Ram (s2040328) and Dennis Buurman (s2027100) for
the Cloud Computing course (2022) at Leiden university.
"""
from heapq import merge
from google.api_core import retry
from google.cloud import pubsub_v1
from google.cloud import storage
from google.cloud import firestore
import json


def update_job(doc_id, work_type):
    db = firestore.Client()

    field = "sort_done" if work_type == "sort" else "palindrome_done"

    db.collection(u'jobs').document(doc_id).update({"done_sort_chunks": firestore.Increment(1)})
    doc_ref = db.collection(u'jobs').document(doc_id)
    doc_ref.update({field: True})


def clean(doc_id, bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=doc_id+"/")
    
    for blob in blobs:
        blob.delete()


def download_all(doc_id, bucket_name):
    data = []
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=doc_id+"/")
    
    for blob in blobs:
        data.append(blob.download_as_bytes().decode("utf-8"))

    return data    


def upload_blob_from_memory(contents, destination_blob_name, bucket_name):
    """Uploads a file to the bucket."""
    # Cloud Storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    upload = False
    if not blob.exists(storage_client):
        blob.upload_from_string(contents)
        upload = True

    return upload


# Palindrome reduce contents of results from list results
# results: ["longest,count",...] where longest and count are integers
def palindrome_reduce(results):
    longest = 0
    count = 0
    for x in results:
        parts = x.split(",")
        longest = max(longest, int(parts[0]))
        count += int(parts[1])
    return json.dumps({"longest": longest, "count": count})


# Sort reduce the contents of strings in list results
# results: [<string>,...] with lines in <string> separated by '\n'
def sort_reduce(results):
    units = [x.split("\n") for x in results]
    sorted_content = list(merge(*units))
    return "\n".join(sorted_content)


# Listen for reduce messages and perform the correct work
def main():
    print("Listening...")
    # Pub/Sub client 'subscriber'
    project_id = "cc-asg2"
    subscription_id = "cc-asg2-reduce_sub"
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    NUM_MESSAGES = 1

    with subscriber:
        # Try to receive a message
        response = subscriber.pull(
            request={"subscription": subscription_path, "max_messages": NUM_MESSAGES},
            retry=retry.Retry(deadline=300),
        )

        # Check if message received, else return
        if len(response.received_messages) == 0:
            return None

        # Perform the reduce work
        json_msg = json.loads(response.received_messages[0].message.data)
        work_type = json_msg["work_type"]
        doc_id = json_msg["doc_id"]

        if work_type == "sort":
            bucket_name = "cc-asg2-sort_intermediates"
            data = download_all(doc_id, bucket_name)
            result = sort_reduce(data)
            upload_blob_from_memory(result, doc_id, "cc-asg2-sort_results")
        elif work_type == "palindrome":
            bucket_name = "cc-asg2-palindrome_intermediates"
            data = download_all(doc_id, bucket_name)
            result = palindrome_reduce(data)
            upload_blob_from_memory(result, doc_id, "cc-asg2-palindrome_results")
        
        clean(doc_id, bucket_name)
        update_job(doc_id, work_type)

        # Collect ids of messages to acknowledge
        ack_ids = []
        for received_message in response.received_messages:
            print(f"Received: {received_message.message.data}.")
            ack_ids.append(received_message.ack_id)

        # Acknowledges the received messages so they will not be sent again.
        subscriber.acknowledge(request={"subscription": subscription_path, "ack_ids": ack_ids})
        print(f"Received and acknowledged {len(response.received_messages)} messages from {subscription_path}.")


if __name__ == "__main__":
    # Keep on listening and processing
    while True:
        main()