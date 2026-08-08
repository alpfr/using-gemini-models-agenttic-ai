# Gemini 3.5 Flash GCP Validation & GitOps Project

This directory contains a complete framework to validate connection, credentials, and settings for accessing the **Gemini 3.5 Flash** model via Google Cloud's **Vertex AI**. It supports CLI scripts, Google Agent Development Kit (ADK) configurations, a FastAPI health check server wrapper, and automated GitOps Kubernetes deployment pipelines via Kustomize, Helm, and ArgoCD.

---

## Project Directory Structure

```text
using-gemini-models/
├── .github/
│   └── workflows/
│       └── argocd-pipeline.yaml  # GitHub Actions GitOps Pipeline
├── adk_project/
│   ├── __init__.py
│   └── agent.py                  # Google ADK Agent & Tools definition
├── gcp/
│   ├── cloudbuild.yaml           # GCP Cloud Build script
│   └── cloudrun.yaml             # Declarative Knative Cloud Run manifest
├── k8s/
│   ├── argocd-app.yaml           # ArgoCD Application definition
│   ├── base/                     # Kustomize Base manifests (Common configs)
│   │   ├── kustomization.yaml
│   │   ├── namespace.yaml
│   │   ├── serviceaccount.yaml
│   │   ├── service.yaml
│   │   ├── deployment.yaml       # Deployment mounted with PVC & env from ConfigMap
│   │   ├── pvc.yaml              # 10Gi standard PersistentVolumeClaim
│   │   └── configmap.yaml        # ConfigMap holding location/port configuration
│   ├── overlays/                 # Kustomize Overlays (Env-specific overrides)
│   │   └── dev/
│   │       ├── kustomization.yaml
│   │       └── patches/
│   │           ├── replica-patch.yaml
│   │           └── env-patch.yaml
│   └── helm-chart/               # Helm Chart layout structure
│       ├── Chart.yaml            # Chart metadata descriptor
│       ├── values.yaml           # Value parameter files (replica, persistence settings)
│       └── templates/            # Resource templates (deployment, service, pvc, configmap)
├── app.py                        # FastAPI health check and validation server
├── Dockerfile                    # Containerization script
├── validate_gemini.py            # Basic CLI validation script
├── multi_agent_validation.py     # Multi-Agent Python validation script
├── requirements.txt              # Project dependencies
├── gcp_deployment_guide.md       # Comprehensive guide
└── README.md                     # General setup and execution guide (this file)
```

---

## Prerequisites

Before running any script or deployment:

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

---

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

---

## Running Validation Locally

### 1. Basic Text & Multimodal Validation
Run the script to test text generation and multimodal inputs (creates a temporary test image):
```bash
python validate_gemini.py
```

You can specify a custom location/region or prompt using command-line arguments:
```bash
python validate_gemini.py --project "your-gcp-project-id" --location "us-central1" --prompt "What is the capital of France?"
```

### 2. Multi-Agent Python Collaboration
To run the multi-agent orchestration script where a Developer Agent writes code and a QA Agent reviews and generates unit tests:
```bash
python multi_agent_validation.py
```

### 3. Google Agent Development Kit (ADK) Agent
We have created a sample Google ADK project in `adk_project/`.
*   **Run the ADK Agent (CLI Mode)**:
    ```bash
    adk run adk_project
    ```
*   **Launch the ADK Studio (Web UI)**:
    ```bash
    adk web adk_project
    ```

---

## Deploying directly to GCP (Google Cloud Run & Cloud Build)

We have created declarative configurations for GCP inside the `gcp/` directory:

### Option A: Automate build and deploy via Google Cloud Build
```bash
gcloud builds submit --config gcp/cloudbuild.yaml --project="YOUR_GCP_PROJECT_ID"
```

### Option B: Declarative Cloud Run deployment
1. Update `YOUR_GCP_PROJECT_ID` inside `gcp/cloudrun.yaml` with your actual project ID.
2. Deploy the service:
   ```bash
   gcloud run services replace gcp/cloudrun.yaml --project="YOUR_GCP_PROJECT_ID"
   ```

---

## Automated GitOps Deployment Pipeline (ArgoCD + GitHub Actions)

We have configured a complete, environment-aware GitOps layout under `k8s/` and a deployment workflow in `.github/workflows/argocd-pipeline.yaml`.

### 1. GitOps Layout Models
*   **Kustomize Structure (`base` & `overlays`)**:
    *   `base/`: Common manifests for Deployment, Service, ServiceAccount, PVC, and ConfigMap.
    *   `overlays/dev/`: Customizes the base config (e.g. replicas set to 2, dev environment variables).
*   **Helm Chart (`helm-chart`)**:
    *   Packaged resources mapping values parameterization in `values.yaml` (replica counts, persistent volumes, environment configs).

### 2. CI/CD Pipeline Flow
1. **Developer Pushes Code**: You push code modifications (excluding manifests and docs) to the `main` branch.
2. **CI Pipeline Triggers**: GitHub Actions builds the Docker container, pushes it to your GCP Artifact Registry, and tags it with the Git commit SHA.
3. **GitOps Write-back**: The pipeline updates the image tag inside `k8s/overlays/dev/kustomization.yaml` using Kustomize and commits it back to the repository.
4. **ArgoCD Reconciliation**: ArgoCD detects the change in `k8s/overlays/dev/kustomization.yaml` and synchronizes the state to GKE with zero downtime.
