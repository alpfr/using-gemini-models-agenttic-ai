# Full Guideline: Deploying Gemini 3.5 Flash & Agentic AI on GCP

This comprehensive guide outlines the end-to-end process of developing, containerizing, validating, and deploying applications powered by **Gemini 3.5 Flash** on Google Cloud Platform (GCP) using Kubernetes, ArgoCD, and GitHub Actions.

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
│   │   └── deployment.yaml
│   ├── overlays/                 # Kustomize Overlays (Env-specific overrides)
│   │   └── dev/
│   │       ├── kustomization.yaml
│   │       └── patches/
│   │           ├── replica-patch.yaml
│   │           └── env-patch.yaml
│   └── helm-chart/               # Helm Chart layout structure
│       ├── Chart.yaml            # Chart metadata descriptor
│       ├── values.yaml           # Value parameter files
│       └── templates/            # Resource templates (deployment.yaml, service.yaml)
├── app.py                        # FastAPI health check and validation server
├── Dockerfile                    # Containerization script
├── validate_gemini.py            # Basic CLI validation script
├── multi_agent_validation.py     # Multi-Agent Python validation script
├── requirements.txt              # Project dependencies
├── gcp_deployment_guide.md       # Comprehensive guide (this file)
└── README.md                     # General setup and execution guide
```

---

## 1. GCP Environment & IAM Setup

To run Gemini models on Vertex AI, you need to enable the services, configure local authentication, and assign IAM roles.

### Step 1.1: Enable Vertex AI API
Enable the required APIs via the gcloud CLI:
```bash
gcloud services enable aiplatform.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    --project="your-gcp-project-id"
```

### Step 1.2: Local Authentication (ADC)
Generate local Application Default Credentials (ADC) for development:
```bash
gcloud auth login
gcloud auth application-default login
```

### Step 1.3: Assign IAM Roles
Grant the **Vertex AI User** (`roles/aiplatform.user`) role to your user or service identity.

**For a User Account:**
```bash
gcloud projects add-iam-policy-binding "your-gcp-project-id" \
    --member="user:your-email@example.com" \
    --role="roles/aiplatform.user"
```

**For a Service Account:**
```bash
gcloud projects add-iam-policy-binding "your-gcp-project-id" \
    --member="serviceAccount:your-service-account@your-gcp-project-id.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

---

## 2. Python Validation Scripts

Google's unified SDK is **`google-genai`**. Do not use legacy libraries like `google-generativeai` or `google-cloud-aiplatform` generative modules.

### Step 2.1: Basic Text & Multimodal Validation
The script [validate_gemini.py](file:///Users/alpfr/Downloads/scripts/using-gemini-models/validate_gemini.py) validates single-prompt responses and image input capabilities using Gemini 3.5 Flash on Vertex AI.

Run validation:
```bash
python validate_gemini.py --project "your-gcp-project-id" --test-multimodal
```

### Step 2.2: Multi-Agent Collaboration
The script [multi_agent_validation.py](file:///Users/alpfr/Downloads/scripts/using-gemini-models/multi_agent_validation.py) demonstrates a sequential pipeline where a **Software Engineer Agent** writes code and a **QA Engineer Agent** reviews it.

Run collaborative pipeline:
```bash
python multi_agent_validation.py --project "your-gcp-project-id"
```

---

## 3. Google Agent Development Kit (ADK) Setup

For advanced agentic architectures, use Google's **Agent Development Kit (ADK)**. We created a project in [adk_project/](file:///Users/alpfr/Downloads/scripts/using-gemini-models/adk_project/agent.py).

### Step 3.1: Define Agents and Tools
In `adk_project/agent.py`, the agent is defined declaratively:
```python
from google.adk.agents.llm_agent import Agent

# Tool function with typed annotations and docstrings
def solve_math_expression(expression: str) -> dict:
    """Evaluates a mathematical expression and returns the result."""
    result = str(eval(expression, {"__builtins__": None}, {}))
    return {"status": "success", "result": result}

root_agent = Agent(
    model='gemini-3.5-flash',
    name='calc_agent',
    description="Calculations assistant.",
    instruction="Solve equations step-by-step using the solve_math_expression tool.",
    tools=[solve_math_expression]
)
```

### Step 3.2: Run and Debug
1. **Interactive CLI chat**:
   ```bash
   adk run adk_project
   ```
2. **ADK Studio (Web UI)** to step through agent reasoning paths and tool outputs:
   ```bash
   adk web adk_project
   ```

---

## 4. Kubernetes Service Wrapper & Containerization

To run securely inside Kubernetes, we wrapped the scripts in an HTTP API to support liveness and readiness health checks.

### Step 4.1: FastAPI Service Wrapper
The [app.py](file:///Users/alpfr/Downloads/scripts/using-gemini-models/app.py) server hosts:
*   `/healthz`: Liveness/readiness probe target.
*   `/validate-single`: Performs single text validation.
*   `/validate-multi`: Evaluates multi-agent coding tasks.

### Step 4.2: Docker Containerization
The [Dockerfile](file:///Users/alpfr/Downloads/scripts/using-gemini-models/Dockerfile) builds a secure, lightweight container:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
```

---

## 5. Kubernetes & ArgoCD GitOps Deployment

We deploy the application declaratively using a GitOps pull-model via ArgoCD.

### Step 5.1: Apply manifests
The Kubernetes specifications are structured under `k8s/base/` and configured via `k8s/overlays/`:
*   `Namespace`: Declared in `k8s/base/namespace.yaml` for isolating resources.
*   `ServiceAccount`: Declared in `k8s/base/serviceaccount.yaml` with GCP Workload Identity annotations.
*   `Deployment`: Declared in `k8s/base/deployment.yaml` with port `8080` exposed and health checks active. Replicas are overridden dynamically in overlays.
*   `Service`: Declared in `k8s/base/service.yaml` exposing port `80`.

### Step 5.2: Bind GKE Workload Identity
Link GKE's ServiceAccount to your GCP Service Account to authorize pods to contact Vertex AI:
```bash
gcloud iam service-accounts add-iam-policy-binding \
    gemini-validator@your-gcp-project-id.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="serviceAccount:your-gcp-project-id.svc.id.goog[gemini-apps/gemini-validator-sa]"
```

### Step 5.3: Register Application in ArgoCD
Deploy the [argocd-app.yaml](file:///Users/alpfr/Downloads/scripts/using-gemini-models/k8s/argocd-app.yaml) manifest inside your ArgoCD namespace:
```bash
kubectl apply -f k8s/argocd-app.yaml -n argocd
```

---

## 6. Automated GitOps CI/CD Pipeline

The GitHub Actions workflow [.github/workflows/argocd-pipeline.yaml](file:///Users/alpfr/Downloads/scripts/using-gemini-models/.github/workflows/argocd-pipeline.yaml) automates GKE deployments:

1. **Trigger**: Code changes push to the `main` branch.
2. **Build**: Authenticates with GCP via Workload Identity, builds the Docker container, and pushes it to your GCP Artifact Registry.
3. **Commit Back**: The runner updates the image tag in `k8s/overlays/dev/kustomization.yaml` using Kustomize and pushes the updated manifest back to the repository.
4. **ArgoCD Sync**: ArgoCD detects the manifest edit in Git and rolls out the updated container automatically.

---

## 7. Rust Integration Guidelines

If you want to implement your project in **Rust**, you have two main options:

### Option A: Official Google Cloud SDK for Rust
Use `google-cloud-aiplatform-v1` to send predictions directly via gRPC or REST.
```rust
use google_cloud_aiplatform_v1::client::PredictionClient;
use google_cloud_auth::project::Config;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = Config::default().await?;
    let client = PredictionClient::new(config).await?;
    // Target endpoint: projects/{project}/locations/{location}/publishers/google/models/gemini-3.5-flash
    Ok(())
}
```

### Option B: The Rig Agentic Framework
For multi-agent systems in Rust, use **Rig**:
```rust
use rig::providers::vertexai;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let provider = vertexai::Client::new("your-gcp-project-id", "us-central1");
    let model = provider.completion_model("gemini-3.5-flash");
    let response = model.prompt("Hello Gemini!").await?;
    println!("Response: {}", response);
    Ok(())
}
```
