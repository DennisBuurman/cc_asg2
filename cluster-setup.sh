#!/bin/sh

# Deploy cluster and worker containers:
# TODO

# Connect to cluster
gcloud container clusters get-credentials amogus --zone europe-west1-b --project cc-asg2

# Copy credential key to cluster
kubectl create secret generic access-key --from-file=key.json=cc-asg2-dfe60fdc4d66.json

# Apply yaml to workers so they can access the key
kubectl apply -f backend/sort/access-with-secret.yaml
kubectl apply -f backend/palindrome/access-with-secret.yaml
kubectl apply -f backend/reduce/access-with-secret.yaml