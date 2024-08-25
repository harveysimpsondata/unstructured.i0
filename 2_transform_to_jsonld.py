import os
import json
import openai
from dotenv import load_dotenv
from datetime import datetime

def load_config():
    """Load environment variables for API configuration."""
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    openai_project_id = os.getenv('OPENAI_PROJECT_ID')
    return openai_api_key, openai_project_id


def convert_to_jsonld_with_llm(json_data):
    """Converts JSON data to JSON-LD format using an LLM."""
    openai_api_key, openai_project_id = load_config()
    openai.api_key = openai_api_key

    prompt = f"""
    Convert the following JSON data to JSON-LD format. Ensure that the JSON-LD follows the schema.org vocabulary and includes appropriate context and type definitions.

    JSON data:
    {json.dumps(json_data, indent=4)}

    JSON-LD:
    """

    response = openai.Completion.create(
        model=f"ft-{openai_project_id}",  # Specify the fine-tuned model
        prompt=prompt,
        max_tokens=1500,
        temperature=0.5
    )

    jsonld_data = response.choices[0].text.strip()
    return json.loads(jsonld_data)


def save_jsonld_to_folder(jsonld_data, folder_path, file_path, suffix):
    """Saves the JSON-LD data to a specified folder."""
    os.makedirs(folder_path, exist_ok=True)
    base_filename = os.path.splitext(os.path.basename(file_path))[0]

    # Get current date and time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_path = os.path.join(folder_path, f"{base_filename}_{suffix}_{current_time}.jsonld")
    with open(file_path, "w") as jsonld_file:
        json.dump(jsonld_data, jsonld_file, indent=4)


def main():
    # Load the extracted JSON data
    folder_path = os.path.join(os.path.dirname(__file__), 'data/json')
    filename = os.path.join(folder_path, 'example_document_title_chunking.json')
    with open(filename, "r") as json_file:
        json_data = json.load(json_file)

    # Convert JSON to JSON-LD using LLM
    jsonld_data = convert_to_jsonld_with_llm(json_data)

    # Save JSON-LD to folder
    save_jsonld_to_folder(jsonld_data, folder_path, filename, 'jsonld')
    print(f"JSON-LD output saved successfully to {folder_path}")

if __name__ == "__main__":
    main()