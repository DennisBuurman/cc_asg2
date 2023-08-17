from google.cloud import storage
import datetime
import google.auth
from google.auth.transport import requests

DOC_BUCKET_NAME = 'cc-asg2-documents'
FRONTEND_URL = "http://cc-asg2.ew.r.appspot.com"

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
	print("request: ", request)
	# If this was a preflight, only send the preflight headers
	if request.method == "OPTIONS":
		print("Handling preflight")
		headers = create_preflight_headers()
		return("", 204, headers)

	# Otherwise send the regular response
	token = request.data

	storage_client = storage.Client()
	bucket = storage_client.bucket(DOC_BUCKET_NAME)
	blob = bucket.blob(token)

	credentials, project_id = google.auth.default()

	# Perform a refresh request to get the access token of the current credentials (Else, it's None)
	r = requests.Request()
	credentials.refresh(r)

	url = blob.generate_signed_url(
		version="v4",
		# This URL is valid for 15 minutes
		expiration=datetime.timedelta(minutes=15),
		# Allow PUT requests using this URL.
		method="PUT",
		content_type="application/octet-stream",
		service_account_email=credentials.service_account_email,
		access_token=credentials.token
	)

	headers = create_cors_headers()
	return (url, 200, headers)
