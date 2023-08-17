import google
from google.cloud import storage
from google.cloud import pubsub_v1

PROJECT_ID = 'cc-asg2'
WEBSITE_URL = "http://cc-asg2.ew.r.appspot.com"

PALINDROME_TOPIC_ID = 'cc-asg2-palindrome'
SORT_TOPIC_ID = 'cc-asg2-sort'
REDUCE_TOPIC_ID = 'cc-asg2-reduce'

PALINDROME_SUB_ID = 'cc-asg2-palindrome_sub'
SORT_SUB_ID = 'cc-asg2-sort_sub'
REDUCE_SUB_ID = 'cc-asg2-reduce_sub'

DOC_BUCKET_NAME = 'cc-asg2-documents'
PALINDROME_BUCKET_NAME = 'cc-asg2-palindrome_intermediates'
PALINDROME_RESULTS_BUCKET_NAME = 'cc-asg2-palindrome_results'
SORT_BUCKET_NAME = 'cc-asg2-sort_intermediates'
SORT_RESULT_BUCKET_NAME = 'cc-asg2-sort_results'

# Set up buckets
storage_client = storage.Client()
document_bucket = storage_client.bucket(DOC_BUCKET_NAME)
palindrome_bucket = storage_client.bucket(PALINDROME_BUCKET_NAME)
palindrome_result_bucket = storage_client.bucket(PALINDROME_RESULTS_BUCKET_NAME)
sort_bucket = storage_client.bucket(SORT_BUCKET_NAME)
sort_result_bucket = storage_client.bucket(SORT_RESULT_BUCKET_NAME)

try:
	storage_client.create_bucket(document_bucket, location="EUROPE-WEST1")
except google.cloud.exceptions.Conflict:
	print("Bucket {} exists, skipping...".format(DOC_BUCKET_NAME))
try:
	storage_client.create_bucket(palindrome_bucket, location="EUROPE-WEST1")
except google.cloud.exceptions.Conflict:
	print("Bucket {} exists, skipping...".format(PALINDROME_BUCKET_NAME))
try:
	storage_client.create_bucket(palindrome_result_bucket, location="EUROPE-WEST1")
except google.cloud.exceptions.Conflict:
	print("Bucket {} exists, skipping...".format(PALINDROME_RESULTS_BUCKET_NAME))
try:
	storage_client.create_bucket(sort_bucket, location="EUROPE-WEST1")
except google.api_core.exceptions.Conflict:
	print("Bucket {} exists, skipping...".format(SORT_BUCKET_NAME))
try:
	storage_client.create_bucket(sort_result_bucket, location="EUROPE-WEST1")
except google.api_core.exceptions.Conflict:
	print("Bucket {} exists, skipping...".format(SORT_RESULT_BUCKET_NAME))

# Set up CORS on document bucket to allow appengine-to-storage uploads
document_bucket.cors = [
        {
            "origin": [WEBSITE_URL],
            "responseHeader": ["Content-Length", "Content-Type"],
            "method": ['PUT', 'POST'],
            "maxAgeSeconds": 3600
        }
    ]
document_bucket.patch()

# Set up topics
publisher = pubsub_v1.PublisherClient()
palindrome_topic_path = publisher.topic_path(PROJECT_ID, PALINDROME_TOPIC_ID)
sort_topic_path = publisher.topic_path(PROJECT_ID, SORT_TOPIC_ID)
reduce_topic_path = publisher.topic_path(PROJECT_ID, REDUCE_TOPIC_ID)

try:
	publisher.create_topic(request={"name": palindrome_topic_path})
except google.api_core.exceptions.AlreadyExists:
	print("Topic {} exists, skipping...".format(PALINDROME_TOPIC_ID))
try:
	publisher.create_topic(request={"name": sort_topic_path})
except google.api_core.exceptions.AlreadyExists:
	print("Topic {} exists, skipping...".format(SORT_TOPIC_ID))
try:
	publisher.create_topic(request={"name": reduce_topic_path})
except google.api_core.exceptions.AlreadyExists:
	print("Topic {} exists, skipping...".format(REDUCE_TOPIC_ID))

# Set up subscriptions
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
palindrome_topic_path = publisher.topic_path(PROJECT_ID, PALINDROME_TOPIC_ID)
sort_topic_path = publisher.topic_path(PROJECT_ID, SORT_TOPIC_ID)
reduce_topic_path = publisher.topic_path(PROJECT_ID, REDUCE_TOPIC_ID)

palin_sub_path = subscriber.subscription_path(PROJECT_ID, PALINDROME_SUB_ID)
sort_sub_path = subscriber.subscription_path(PROJECT_ID, SORT_SUB_ID)
reduce_sub_path = subscriber.subscription_path(PROJECT_ID, REDUCE_SUB_ID)

with subscriber:
	subscriber.create_subscription(
		request={"name": palin_sub_path, "topic": palindrome_topic_path, "ack_deadline_seconds": 60}
	)
	subscriber.create_subscription(
		request={"name": sort_sub_path, "topic": sort_topic_path, "ack_deadline_seconds": 60}
	)
	subscriber.create_subscription(
		request={"name": reduce_sub_path, "topic": reduce_topic_path, "ack_deadline_seconds": 60}
	)

# Deploy
# TODO
