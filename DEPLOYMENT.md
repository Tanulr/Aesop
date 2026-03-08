# Deploying Aesop to Google Cloud Run

## Prerequisites

- Google Cloud project with billing enabled
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed and authenticated

## 1. Enable APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable slides.googleapis.com
gcloud services enable drive.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## 2. Credentials Setup

You have two options for authentication:

### Option A: Service Account with Key File (recommended for Cloud Run)

Use a service account JSON key. Presentations are created in the service account's Drive; you access them via the returned link.

1. **Create a service account** in [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts):
   - IAM & Admin → Service Accounts → Create Service Account
   - Name it (e.g. `aesop-slides`)
   - Grant role: **Editor** (or at minimum custom roles for Slides + Drive)
   - Create key → JSON → Download

2. **Store the key in Secret Manager** (keeps it out of your image):

   ```bash
   gcloud secrets create aesop-credentials --data-file=/path/to/your-service-account-key.json
   ```

   Or if the secret already exists:

   ```bash
   gcloud secrets versions add aesop-credentials --data-file=/path/to/your-service-account-key.json
   ```

3. **Where to put the file locally** (for development):
   - Save as `credentials.json` in the **project root** (same folder as `api.py`)
   - Add `credentials.json` to `.gitignore` (already done) so it's never committed

### Option B: Cloud Run Service Account (Workload Identity)

Use the default Cloud Run service account. No key file needed—credentials come from the GCP metadata server.

1. Enable the APIs (step 1 above)
2. Grant the Cloud Run service account access to Slides + Drive:
   - Find the service account: `PROJECT_NUMBER-compute@developer.gserviceaccount.com`
   - IAM → Add principal → this SA → Role: **Editor** (or custom)
3. Do **not** set `AESOP_CREDENTIALS_PATH` when deploying—the app will use Application Default Credentials.

**Note:** With Option B, presentations are created in the *Cloud Run* service account's Drive, not a custom account. Option A gives you a dedicated account and more control.

## 3. Build and Deploy

### Using Secret Manager (Option A)

```bash
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1

# Build the image
gcloud builds submit --tag gcr.io/${PROJECT_ID}/aesop

# Deploy with the credentials secret mounted
gcloud run deploy aesop \
  --image gcr.io/${PROJECT_ID}/aesop \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-secrets=/secrets/credentials.json=aesop-credentials:latest \
  --set-env-vars="AESOP_CREDENTIALS_PATH=/secrets/credentials.json"
```

### Using Workload Identity only (Option B)

```bash
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1

gcloud builds submit --tag gcr.io/${PROJECT_ID}/aesop

gcloud run deploy aesop \
  --image gcr.io/${PROJECT_ID}/aesop \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated
```

## 4. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AESOP_CREDENTIALS_PATH` | `credentials.json` | Path to service account JSON or OAuth client secrets. On Cloud Run, point to mounted secret (e.g. `/secrets/credentials.json`). |
| `AESOP_TOKEN_PATH` | `token.json` | For OAuth flow only; not used with service accounts. |
| `AESOP_GCS_BUCKET` | *(unset)* | If set, generated images are uploaded to this GCS bucket instead of Drive. Use for reliable Slides API image URLs. |
| `PORT` | `8080` | Set automatically by Cloud Run. |

## 5. Verify

```bash
# Get the service URL
gcloud run services describe aesop --region ${REGION} --format='value(status.url)'

# Test the prompt endpoint
curl -X POST https://YOUR_SERVICE_URL/presentations/from-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A B2B SaaS company"}'

# Test the StoryBrand endpoint
curl -X POST https://YOUR_SERVICE_URL/presentations/storybrand \
  -H "Content-Type: application/json" \
  -d '{"1_Test": {"title": "Test", "description": "Description", "image_url": ""}}'
```

## Local development with service account

1. Save your service account JSON as `credentials.json` in the project root
2. Run the API: `uvicorn api:app --reload`
3. The `/presentations/storybrand` endpoint will create real presentations

**Do not commit `credentials.json`**—it contains secrets. It's listed in `.gitignore`.
