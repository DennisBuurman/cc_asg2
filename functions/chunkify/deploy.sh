#!/bin/sh

gcloud functions deploy chunkify \
	--region europe-west1 \
	--entry-point chunkify \
	--runtime python39 \
	--trigger-bucket cc-asg2-documents \
	--memory 4096