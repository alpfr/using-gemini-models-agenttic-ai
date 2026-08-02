import os
import sys
import argparse
from google import genai
from google.genai import types
from google.genai.errors import APIError

def print_banner(text):
    print("\n" + "=" * 60)
    print(f" {text} ".center(60, "="))
    print("=" * 60)

def generate_code(client: genai.Client, model_name: str, task: str) -> str:
    """Agent 1: Writes the initial Python code for the request."""
    print(f"\n[Agent 1: Software Engineer] Writing code for: '{task}'...")
    
    config = types.GenerateContentConfig(
        temperature=0.3,
        system_instruction=(
            "You are an expert Python software engineer. Write clean, well-documented, "
            "and efficient Python code for the requested task. Provide ONLY the Python code "
            "inside a markdown code block (```python ... ```) with no conversational intro/outro."
        )
    )
    
    response = client.models.generate_content(
        model=model_name,
        contents=task,
        config=config
    )
    return response.text

def review_code(client: genai.Client, model_name: str, code: str) -> str:
    """Agent 2: Performs QA review and generates unit tests for the code."""
    print("\n[Agent 2: QA Engineer] Reviewing code and generating unit tests...")
    
    config = types.GenerateContentConfig(
        temperature=0.2,
        system_instruction=(
            "You are a QA automation engineer. Review the provided Python code for bugs, edge cases, "
            "and performance. Then, write complete unittest or pytest test cases for the code. "
            "Start your response with a brief bulleted 'Code Review' section, followed by a 'Test Suite' markdown code block."
        )
    )
    
    prompt = f"Please review this code and generate unit tests:\n\n{code}"
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=config
    )
    return response.text

def main():
    parser = argparse.ArgumentParser(description="Run a multi-agent system using Gemini 3.5 Flash on Vertex AI.")
    parser.add_argument("--project", type=str, help="GCP Project ID. Defaults to GOOGLE_CLOUD_PROJECT env var.")
    parser.add_argument("--location", type=str, default="us-central1", help="GCP Region/Location (default: us-central1).")
    parser.add_argument("--task", type=str, default="Implement a function that checks if a string is a valid email address.", help="Programming task to solve.")
    args = parser.parse_args()

    # Determine GCP Project ID
    project_id = args.project or os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("\n[ERROR] GCP Project ID is required.")
        print("Please set the GOOGLE_CLOUD_PROJECT environment variable or pass the --project argument.")
        print("Example: python multi_agent_validation.py --project my-gcp-project-id")
        sys.exit(1)

    print_banner("Gemini 3.5 Flash Multi-Agent Validation")
    print(f"Project ID: {project_id}")
    print(f"Location:   {args.location}")
    print(f"Model ID:   gemini-3.5-flash")
    
    # Initialize the Unified Google GenAI Client
    try:
        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=args.location
        )
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize Google GenAI Client: {e}")
        print("Please run: gcloud auth application-default login")
        sys.exit(1)

    try:
        # Step 1: Run Software Engineer Agent
        code_output = generate_code(client, 'gemini-3.5-flash', args.task)
        print("\n" + "-" * 40)
        print(" Engineer Output ".center(40, "-"))
        print("-" * 40)
        print(code_output.strip())
        print("-" * 40)

        # Step 2: Run QA Reviewer Agent using output from the Engineer Agent
        qa_output = review_code(client, 'gemini-3.5-flash', code_output)
        print("\n" + "-" * 40)
        print(" QA Review & Unit Tests ".center(40, "-"))
        print("-" * 40)
        print(qa_output.strip())
        print("-" * 40)
        
        print("\n[SUCCESS] Multi-Agent predictive workflow validated!")

    except APIError as e:
        print(f"\n[API ERROR] Vertex AI prediction failed:\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
