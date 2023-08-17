import uuid

DOC_BUCKET_NAME = 'cc-asg2-documents'
FRONTEND_URL = "http://cc-asg2.ew.r.appspot.com"

def create_preflight_headers():
	headers = {
		'Access-Control-Allow-Origin': FRONTEND_URL,
		'Access-Control-Allow-Methods': 'GET',
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
		print("handling preflight")
		headers = create_preflight_headers()
		return("", 204, headers)

	# Otherwise send the regular response
	token = str(uuid.uuid4())
	headers = create_cors_headers()
	return (token, 200, headers)
