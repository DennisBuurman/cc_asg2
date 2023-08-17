from google.cloud import firestore

FRONTEND_URL = "http://cc-asg2.ew.r.appspot.com"
NUM_REDUCE_STEPS = 1
PROJECT_ID = 'cc-asg2'

def create_preflight_headers():
	headers = {
		'Access-Control-Allow-Origin': FRONTEND_URL,
		'Access-Control-Allow-Methods': 'POST',
		'Access-Control-Max-Age': '3600'
    }
	return headers

def create_cors_headers():
	headers = {
		'Access-Control-Allow-Origin': FRONTEND_URL
	}
	return headers

def get_job_status(job_token):
	db = firestore.Client(project=PROJECT_ID)
	doc_ref = db.collection('jobs').document(job_token)
	doc = doc_ref.get()

	# Sometimes the document is not processed yet, so we make a dummy
	if not doc.exists:
		status = {
			"num_chunks": 1,
			"sorted_chunks": 0,
			"palindromed_chunks": 0,
			"done": False
		}
		return status

	# Usually the document will be present and we can try to obtain the status
	doc_dict = doc.to_dict()
	chunks_to_process = doc_dict['num_chunks'] + NUM_REDUCE_STEPS
	sorted_chunks = doc_dict['done_sort_chunks']
	palindromed_chunks = doc_dict['done_palindrome_chunks']
	sort_done = doc_dict['sort_done']
	palindrome_done = doc_dict['palindrome_done']
	done = False
	if sort_done:
		sorted_chunks = chunks_to_process
	if palindrome_done:
		palindromed_chunks = chunks_to_process
	if sort_done and palindrome_done:
		done = True
	status = {
		"chunks_to_process": chunks_to_process,
		"sorted_chunks": sorted_chunks,
		"palindromed_chunks": palindromed_chunks,
		"done": done
	}

	return status

def main(request):
	print("request: ", request)
	# If this was a preflight, only send the preflight headers
	if request.method == "OPTIONS":
		print("handling preflight")
		headers = create_preflight_headers()
		return("", 204, headers)

	# Otherwise send the regular response
	job_token = request.data.decode('utf-8')
	print("Job token: ", job_token)
	print("Job token type: ", type(job_token))
	status = get_job_status(job_token)
	headers = create_cors_headers()
	return (status, 200, headers)
