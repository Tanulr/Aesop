#!/usr/bin/env bash
set -e

PROJECT_ID="${PROJECT_ID:-gcloud-hackathon-yg26kl42cz7ry}"
REGION="${REGION:-us-central1}"

echo "Building image..."
gcloud builds submit --tag "gcr.io/${PROJECT_ID}/aesop"

echo "Deploying to Cloud Run..."
gcloud run deploy aesop \
  --image "gcr.io/${PROJECT_ID}/aesop" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --set-secrets=/secrets/credentials.json=aesop-credentials:latest \
  --set-env-vars="AESOP_CREDENTIALS_PATH=/secrets/credentials.json"

echo ""
echo "Deployed. Service URL:"
gcloud run services describe aesop --region "${REGION}" --format='value(status.url)'
