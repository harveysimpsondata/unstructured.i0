import os
import json
from dotenv import load_dotenv
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError

def load_config():
    """Load environment variables for API configuration."""
    load_dotenv()
    api_key = os.getenv('UNSTRUCTURED_API')
    unstructured_url = os.getenv('UNSTRUCTURED_URL')
    return api_key, unstructured_url

def parse_pdf_to_json(pdf_path, api_key, unstructured_url, chunking_strategy=None, max_characters=500, similarity_threshold=0.5, multipage_sections=True, combine_text_under_n_chars=500):
    """Parse PDF and convert it to JSON format, with optional chunking."""
    try:
        client = UnstructuredClient(api_key_auth=api_key, server_url=unstructured_url)
        
        with open(pdf_path, "rb") as f:
            files = shared.Files(
                content=f.read(),
                file_name=pdf_path,
            )
        
        req_params = {
            "files": files,
            "strategy": 'hi_res',
            "hi_res_model_name": 'yolox',
            "languages": ["eng"],
            "extract_image_block_types": ["Image", "Table"],
            "unique_element_ids": True,
            "output_format": "application/json",
            "include_page_breaks": True
        }

        # Add chunking parameters if chunking strategy is provided
        if chunking_strategy:
            req_params["chunking_strategy"] = chunking_strategy
            if chunking_strategy == "by_similarity":
                req_params["similarity_threshold"] = similarity_threshold
            elif chunking_strategy == "by_title":
                req_params["multipage_sections"] = multipage_sections
                req_params["combine_under_n_chars"] = combine_text_under_n_chars
            req_params["max_characters"] = max_characters

        req = shared.PartitionParameters(**req_params)
        resp = client.general.partition(req)
        normalized_elements = resp.elements

        # Remove unwanted metadata
        for element in normalized_elements:
            if 'metadata' in element:
                element['metadata'].pop('filename', None)
                element['metadata'].pop('filetype', None)
                element['metadata'].pop('languages', None)

        # Return JSON string
        return json.dumps(normalized_elements, indent=4)
    
    except SDKError as e:
        return json.dumps({'error': str(e)})

def save_json_to_folder(json_data, pdf_path, folder_path, suffix):
    """Save JSON data to a specified folder."""
    os.makedirs(folder_path, exist_ok=True)
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    file_path = os.path.join(folder_path, f"{base_filename}_{suffix}.json")
    with open(file_path, "w") as json_file:
        json_file.write(json_data)

def main(pdf_path, folder_path):
    """Main function to execute PDF parsing and saving with both chunking strategies."""
    api_key, unstructured_url = load_config()

    # Extract using title-based chunking
    title_json_output = parse_pdf_to_json(pdf_path, api_key, unstructured_url, chunking_strategy='by_title')
    save_json_to_folder(title_json_output, pdf_path, folder_path, 'title_chunking')

    # Extract using similarity-based chunking
    similarity_json_output = parse_pdf_to_json(pdf_path, api_key, unstructured_url, chunking_strategy='by_similarity')
    save_json_to_folder(similarity_json_output, pdf_path, folder_path, 'similarity_chunking')

    print(f"JSON outputs saved successfully to {folder_path}")

# Example usage
pdf_path = 'path/to/your/pdf/Verifiable_Internet_for_Artificial_Intelligence_whitepaper.pdf'
folder_path = 'path/to/save/json'
main(pdf_path, folder_path)
