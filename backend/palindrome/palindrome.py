"""
Palindrome worker program created by Jochem Ram (s2040328) and Dennis Buurman (s2027100) for
the Cloud Computing course (2022) at Leiden university.
"""
from google.api_core import retry
from google.cloud import pubsub_v1
from google.cloud import storage
from google.cloud import firestore
import json


def publish(filename):
    project_id = "cc-asg2"
    topic_id = "cc-asg2-reduce"
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    msg = {
        "work_type": "palindrome",
        "doc_id": filename.split("/")[0]
    }
    msg_byte_string = json.dumps(msg).encode("utf-8")

    publisher.publish(topic_path, msg_byte_string)
    print(f"Published message to {topic_path}.")


def update_job(filename):
    db = firestore.Client()
    doc_id = filename.split("/")[0]

    db.collection(u'jobs').document(doc_id).update({"done_palindrome_chunks": firestore.Increment(1)})

    doc_ref = db.collection(u'jobs').document(doc_id)
    if doc_ref.get().to_dict()["num_chunks"] == doc_ref.get().to_dict()["done_palindrome_chunks"]:
        print("Ready to reduce: {}".format(filename.split("/")[0]))
        publish(filename)


def download_byte_range(source_blob_name, start_byte, end_byte):
    """Downloads a blob from the bucket."""
    # Cloud Storage client
    storage_client = storage.Client()
    bucket_name = "cc-asg2-documents"
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(source_blob_name)
    content = blob.download_as_bytes(start=start_byte, end=end_byte)

    return content


def upload_blob_from_memory(contents, destination_blob_name):
    """Uploads a file to the bucket."""
    # Cloud Storage client
    storage_client = storage.Client()
    bucket_name = "cc-asg2-palindrome_intermediates"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    upload = False
    if not blob.exists(storage_client):
        blob.upload_from_string(contents)
        upload = True

    return upload


def download(response):
    source_blob_name = response["doc_id"]
    start_byte = response["chunk"]["offset"]
    end_byte = start_byte + response["chunk"]["size"]
    result_file_name = "{}/{}".format(response["doc_id"], response["chunk"]["chunk_id"])
    content = download_byte_range(source_blob_name, start_byte, end_byte)
    
    return content, result_file_name


def palindromes(content):
    longest = 0
    count = 0

    for word in content.replace("\n", "").split():
        if word == word[::-1]:
            count += 1
            if len(word) > longest:
                longest = len(word)

    return "{},{}".format(longest, count)


def main():
    # Pub/Sub client 'subscriber'
    project_id = "cc-asg2"
    subscription_id = "cc-asg2-palindrome_sub"
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    NUM_MESSAGES = 1

    with subscriber:
        print("Listening...")
        # Try to receive a message
        response = subscriber.pull(
            request={"subscription": subscription_path, "max_messages": NUM_MESSAGES},
            retry=retry.Retry(deadline=300),
        )

        # Check if message received, else return
        if len(response.received_messages) == 0:
            return None

        print("Got a message!")

        # Perform the palindrome work
        json_msg = json.loads(response.received_messages[0].message.data)
        content, filename = download(json_msg) # Download object part
        result = palindromes(content.decode("utf-8"))

        # Store intermediate result in cloud storage database
        if upload_blob_from_memory(result, filename):
            # Update job progress and maybe publish message for reduce workers
            update_job(filename)

        # Collect ids of messages to acknowledge
        ack_ids = []
        for received_message in response.received_messages:
            #print(f"Received: {received_message.message.data}.")
            ack_ids.append(received_message.ack_id)

        # Acknowledges the received messages so they will not be sent again.
        subscriber.acknowledge(request={"subscription": subscription_path, "ack_ids": ack_ids})
        print(f"Received and acknowledged {len(response.received_messages)} messages from {subscription_path}.")


if __name__ == "__main__":
    # Keep on listening and processing
    while True:
        main()