#!/bin/sh

gcloud functions deploy get_progress \
	--region europe-west1 \
	--entry-point main \
	--runtime python39 \
	--trigger-http  \
	--allow-unauthenticated \
	--memory 128 \
	--security-level secure-optional
