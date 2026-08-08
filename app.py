import os
import uvicorn
from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types

app = FastAPI(title="Gemini 3.5 Flash Kubernetes Validator")

def get_client() -> genai.Client:
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_CLOUD_PROJECT environment variable is not set."
        )
    try:
        # Initialize standard Vertex AI Client
        return genai.Client(
            vertexai=True,
            project=project_id,
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize GenAI Client: {e}"
        )

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/validate-single")
async def validate_single(prompt: str = "Hello Gemini! Confirm you are running on Gemini 3.5 Flash."):
    client = get_client()
    config = types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=500,
        system_instruction="You are a system verifier."
    )
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=config
        )
        return {
            "status": "success",
            "model": "gemini-3.5-flash",
            "prompt": prompt,
            "response": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/validate-multi")
async def validate_multi(task: str = "Write a Python palindrome check function."):
    client = get_client()
    try:
        # Agent 1: Software Engineer
        engineer_config = types.GenerateContentConfig(
            temperature=0.3,
            system_instruction="You are an expert developer. Output ONLY clean Python code."
        )
        code_response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=task,
            config=engineer_config
        )
        
        # Agent 2: QA Engineer
        qa_config = types.GenerateContentConfig(
            temperature=0.2,
            system_instruction="You are a QA engineer. Review this code and write pytest cases."
        )
        qa_response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=f"Review this code and write unit tests:\n\n{code_response.text}",
            config=qa_config
        )
        
        return {
            "status": "success",
            "task": task,
            "engineer_code": code_response.text,
            "qa_review_and_tests": qa_response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
