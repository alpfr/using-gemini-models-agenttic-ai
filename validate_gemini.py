import os
import sys
import argparse
from PIL import Image
from google import genai
from google.genai import types
from google.genai.errors import APIError

def print_banner(text):
    print("\n" + "=" * 60)
    print(f" {text} ".center(60, "="))
    print("=" * 60)

def validate_text_generation(client: genai.Client, model_name: str, prompt: str):
    """Validates basic text generation capabilities using Gemini 3.5 Flash."""
    print_banner("Testing Text Generation")
    print(f"Prompt: {prompt!r}")
    
    config = types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=1024,
        system_instruction="You are a data science assistant validating model connectivity. Respond concisely."
    )
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config
        )
        print("\nResponse:")
        print(response.text)
        print("\n[SUCCESS] Text generation test passed!")
        return True
    except APIError as e:
        print(f"\n[API ERROR] Failed to connect to Gemini via Vertex AI:\n{e}")
        return False
    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}")
        return False

def validate_multimodal_generation(client: genai.Client, model_name: str, image_path: str):
    """Validates multimodal capabilities (Image + Text) using Gemini 3.5 Flash."""
    print_banner("Testing Multimodal Input")
    
    if not os.path.exists(image_path):
        print(f"Image not found at: {image_path}")
        print("Creating a temporary test image...")
        try:
            # Create a simple red block image for testing
            img = Image.new('RGB', (100, 100), color='red')
            img.save(image_path)
            print(f"Temporary image created at {image_path}")
        except Exception as e:
            print(f"Failed to create temporary image: {e}")
            return False
            
    print(f"Loading image from: {image_path}")
    try:
        img = Image.open(image_path)
        prompt = "Describe what is shown in this image, its main color, and explain what color psychology associates with it."
        
        print(f"Prompt: {prompt!r}")
        response = client.models.generate_content(
            model=model_name,
            contents=[img, prompt]
        )
        print("\nResponse:")
        print(response.text)
        print("\n[SUCCESS] Multimodal validation test passed!")
        return True
    except APIError as e:
        print(f"\n[API ERROR] Multimodal request failed:\n{e}")
        return False
    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}")
        return False
    finally:
        # Cleanup temporary image if created
        if os.path.exists(image_path) and "temp_validation_image" in image_path:
            os.remove(image_path)
            print("Cleaned up temporary test image.")

def main():
    parser = argparse.ArgumentParser(description="Validate Gemini 3.5 Flash connection on GCP/Vertex AI.")
    parser.add_argument("--project", type=str, help="GCP Project ID. Defaults to GOOGLE_CLOUD_PROJECT env var.")
    parser.add_argument("--location", type=str, default="us-central1", help="GCP Region/Location (default: us-central1).")
    parser.add_argument("--prompt", type=str, default="Hello Gemini! Confirm you are running on Gemini 3.5 Flash.", help="Prompt for testing text generation.")
    parser.add_argument("--test-multimodal", action="store_true", help="Run multimodal test with a generated image.")
    args = parser.parse_args()

    # Determine GCP Project ID
    project_id = args.project or os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("\n[ERROR] GCP Project ID is required.")
        print("Please set the GOOGLE_CLOUD_PROJECT environment variable or pass the --project argument.")
        print("Example: python validate_gemini.py --project my-gcp-project-id")
        sys.exit(1)

    print_banner("Gemini 3.5 Flash Validation Tool")
    print(f"Project ID: {project_id}")
    print(f"Location:   {args.location}")
    print(f"Model ID:   gemini-3.5-flash")
    
    # Initialize the Unified Google GenAI Client with vertexai=True
    # The client uses Application Default Credentials (ADC) by default.
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

    # Run Text Validation
    text_ok = validate_text_generation(client, 'gemini-3.5-flash', args.prompt)
    
    # Run Multimodal Validation (if requested)
    multimodal_ok = True
    if args.test_multimodal:
        temp_img_path = os.path.join(os.getcwd(), "temp_validation_image.jpg")
        multimodal_ok = validate_multimodal_generation(client, 'gemini-3.5-flash', temp_img_path)

    print_banner("Validation Summary")
    if text_ok and multimodal_ok:
        print("STATUS: ALL TESTS PASSED SUCCESSFULLY!")
        print("Your GCP credentials, Vertex AI APIs, and google-genai SDK are correctly configured.")
    else:
        print("STATUS: VALIDATION FAILED!")
        print("Please check the error logs above and verify your GCP Vertex AI setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
