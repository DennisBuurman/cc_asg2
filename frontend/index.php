<!DOCTYPE html>
<html>
<body>
    <div>
        Select file to upload:
        <input type="file" name="fileToUpload" id="fileToUpload">
        <!-- <input type="submit"  value="Upload File" name="submit" id="submit-upload"> -->
        <button type="button" id="submit-upload">Upload!</button>
    </div>

    <div>
        <label for="palindrome_progress">Palindrome progress:</label>
        <progress id="palindrome_progress" max="100"></progress>
    </div>
    <div>
        <label for="sort_progress">Sorting progress:</label>
        <progress id="sort_progress" max="100"></progress>
    </div>

    <div id="palindrome_results" hidden>
        Longest palindrome: <span id="palindrome_length"></span><br>
        Palindrome count: <span id="palindrome_count"></span>
    </div>
    <div id="sort_results" hidden>
        sorted file: <a download id="download_sorted" href="">download</a>
        (expires after 1 hour)
    </div>
    <script>
        function get_token() {
            let endpoint = "https://europe-west1-cc-asg2.cloudfunctions.net/token_generator";
            let request = new XMLHttpRequest();
            request.open('GET', endpoint, false);
            request.setRequestHeader('Content-Type', 'application/octet-stream');
            request.send(null);

            var response = request.responseText;
            console.log(response)
            return response;
        }

        function get_signedurl(job_token) {
            let endpoint = "https://europe-west1-cc-asg2.cloudfunctions.net/signedurl_generator";
            let request = new XMLHttpRequest();
            request.open('POST', endpoint, false);
            request.setRequestHeader('Content-Type', 'application/octet-stream');
            console.log(job_token)
            request.send(job_token);

            let response = request.responseText;
            console.log(response);
            return response;
        }

        function upload_document(signed_url) {
            //Get file
            let filefield = document.getElementById("fileToUpload");
            let file = filefield.files[0];

            //Send PUT request
            let request = new XMLHttpRequest();
            request.open('PUT', signed_url, false);
            request.setRequestHeader('Content-Type', 'application/octet-stream');
            request.send(file);
        }

        function report_stats(stats) {
            let palindrome_progress = 100 * stats.palindromed_chunks / stats.chunks_to_process;
            let sort_progress = 100 * stats.sorted_chunks / stats.chunks_to_process;
            let palindrome_progressbar = document.getElementById("palindrome_progress");
            palindrome_progressbar.setAttribute("value", palindrome_progress);
            let sort_progressbar = document.getElementById("sort_progress");
            sort_progressbar.setAttribute("value", sort_progress);
        }

        function progress_check(job_token) {
            let endpoint = "https://europe-west1-cc-asg2.cloudfunctions.net/get_progress";
            let request = new XMLHttpRequest();
            //request.setRequestHeader('Content-Type', 'application/octet-stream');
            let response;
            request.open('POST', endpoint, false);
            request.send(job_token);
            response = JSON.parse(request.responseText);
            report_stats(response);
            if (response.done) {
                //Do something when upload is complete
                console.log("done my dude");
                show_results(job_token);
                clearInterval(progress_check_interval);
            }
        }

        async function show_results(job_token) {
            let endpoint = "https://europe-west1-cc-asg2.cloudfunctions.net/get-results"
            let request = new XMLHttpRequest();
            let response;
            request.open('POST', endpoint, false);
            request.send(job_token);
            response = JSON.parse(request.responseText);
            console.log("showing results");
            console.log(request.responseText)

            palindrome_count_elem = document.getElementById('palindrome_count');
            palindrome_len_elem = document.getElementById('palindrome_length');
            palindrome_count_elem.textContent = response.palindrome_result.count;
            palindrome_len_elem.textContent = response.palindrome_result.longest;
            palindrome_res_div = document.getElementById("palindrome_results");
            palindrome_res_div.removeAttribute("hidden");

            sorted_download_elem = document.getElementById('download_sorted');
            sorted_download_elem.setAttribute("href", response.sort_result);
            sort_res_div = document.getElementById('sort_results');
            sort_res_div.removeAttribute("hidden");
        }

        async function hide_results() {
            palindrome_res_div = document.getElementById("palindrome_results");
            palindrome_res_div.setAttribute("hidden", null);
            sort_res_div = document.getElementById('sort_results');
            sort_res_div.setAttribute("hidden", null)
        }

        // Welcome!
        console.log("I'm alive, hello!");
        let button = document.getElementById("submit-upload");

        // Handle file upload
        let job_token
        let progress_check_interval
        let done = false
        button.addEventListener("click", function(){
            // Results should only be shown on job completion
            hide_results();

            //Submit the job
            job_token = get_token();
            signed_url = get_signedurl(job_token);
            upload_document(signed_url);
            alert('The file has been uploaded successfully.');
            
            // Report progress
            progress_check_interval = window.setInterval(function() {
                progress_check(job_token);
            }, 2000);
        });


    </script>
</body>
</html>