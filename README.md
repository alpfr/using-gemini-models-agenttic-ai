# Gemini 3.5 Flash GCP Validation Project

This directory contains a simple Python implementation to validate connection, credentials, and settings for accessing the **Gemini 3.5 Flash** model via Google Cloud's **Vertex AI**.

## Prerequisites

Before running the validation script:

1. **Google Cloud SDK (`gcloud`)**: Install `gcloud` and log in.
2. **Vertex AI API**: Ensure the Vertex AI API (`aiplatform.googleapis.com`) is enabled in your GCP project.
3. **Application Default Credentials (ADC)**: Authenticate your local environment to GCP:
   ```bash
   gcloud auth application-default login
   ```
4. **Permissions**: Make sure your authenticated user account or service account has the **Vertex AI User** role. You can assign it with:
   * **For a User Account:**
     ```bash
     gcloud projects add-iam-policy-binding "your-gcp-project-id" \
         --member="user:your-email@example.com" \
         --role="roles/aiplatform.user"
     ```
   * **For a Service Account:**
     ```bash
     gcloud projects add-iam-policy-binding "your-gcp-project-id" \
         --member="serviceAccount:your-service-account@your-gcp-project-id.iam.gserviceaccount.com" \
         --role="roles/aiplatform.user"
     ```

## Setup Instructions

1. Set up a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your GCP project ID as an environment variable:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
   ```

## Running Validation

Run the script to test text generation:
```bash
python validate_gemini.py
```

Or test both text generation and multimodal capabilities (sends a dynamically generated image to Gemini):
```bash
python validate_gemini.py --test-multimodal
```

You can specify a custom location/region or prompt using command-line arguments:
```bash
python validate_gemini.py --project "your-gcp-project-id" --location "us-central1" --prompt "What is the capital of France?"
```

## Running Multi-Agent Validation

To run the multi-agent orchestration script where a Developer Agent writes code and a QA Agent reviews and generates unit tests:
```bash
python multi_agent_validation.py
```

You can pass a custom task for the agents to collaborate on:
```bash
python multi_agent_validation.py --project "your-gcp-project-id" --task "Create a fast sorting function in Python."
```
