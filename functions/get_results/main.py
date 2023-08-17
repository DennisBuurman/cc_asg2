import datetime
import json
import google.auth
from google.auth.transport import requests
from google.cloud import storage
from google.cloud import firestore

FRONTEND_URL = "http://cc-asg2.ew.r.appspot.com"
PALINDROME_RESULT_BUCKET = 'cc-asg2-palindrome_results'
SORT_RESULT_BUCKET = 'cc-asg2-sort_results'
DOC_BUCKET_NAME = 'cc-asg2-documents'


def create_preflight_headers():
	headers = {
		'Access-Control-Allow-Origin': FRONTEND_URL,
		'Access-Control-Allow-Methods': 'POST',
		'Access-Control-Allow-Headers': 'Content-Type',
		'Access-Control-Max-Age': '3600'
    }
	return headers

def create_cors_headers():
	headers = {
		'Access-Control-Allow-Origin': FRONTEND_URL
	}
	return headers

def main(request):
	job_token = request.data.decode('utf-8')

	# Set up redentials that will be required to sign URL later on
	credentials, project_id = google.auth.default()
	r = requests.Request() # Perform a refresh request to get the access token
	credentials.refresh(r) # of the current credentials (Else, it's None) 

	# If this was a preflight, only send the preflight headers
	if request.method == "OPTIONS":
		print("Handling preflight")
		headers = create_preflight_headers()
		return("", 204, headers)

	# Create signed storage URL to download sort results
	storage_client = storage.Client()
	sort_result_bucket = storage_client.bucket(SORT_RESULT_BUCKET)
	sort_result_blob = sort_result_bucket.blob(job_token)
	sort_result = sort_result_blob.generate_signed_url(
		version="v4",
		# This URL is valid for 15 minutes
		expiration=datetime.timedelta(minutes=15),
		# Allow PUT requests using this URL.
		method="GET",
		service_account_email=credentials.service_account_email,
		access_token=credentials.token
	)

	# Get palindrome results
	palindrome_result_bucket = storage_client.bucket(PALINDROME_RESULT_BUCKET)
	palindrome_blob = palindrome_result_bucket.blob(job_token)
	palindrome_result = json.loads(palindrome_blob.download_as_bytes())

	# Clean up original file and FireStore job
	storage_client = storage.Client()
	document_bucket = storage_client.bucket(DOC_BUCKET_NAME)
	document_blob = document_bucket.blob(job_token)
	document_blob.delete()

	db = firestore.Client()
	db.collection('jobs').document(job_token).delete()

	# Construct response
	response = {
		"palindrome_result": palindrome_result,
		"sort_result": sort_result
	}

	# Configure headers and send response
	headers = create_cors_headers()
	return (response, 200, headers)
