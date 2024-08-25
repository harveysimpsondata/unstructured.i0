import os
import json
from datetime import datetime
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


def extract_content(filename, chunking_strategy, partitioning_strategy, multipage_sections=True, similarity_threshold=0.5, hi_res_model_name='layout_v1.1.0', max_characters=500):
    """Extracts and processes content from a document using the unstructured.io API."""
    try:
        api_key, unstructured_url = load_config()
        client = UnstructuredClient(api_key_auth=api_key, server_url=unstructured_url)

        with open(filename, "rb") as file:
            # Read file content for processing
            file_content = file.read()

        # Create a Files object for the API request
        files = shared.Files(
            content=file_content,
            file_name=os.path.basename(filename),
        )

        # Define the parameters for the API request
        req_params = {
            "files": files,
            "strategy": partitioning_strategy,
            "hi_res_model_name": hi_res_model_name,  # High-resolution model for object detection
            "languages": ["eng"],
            "extract_image_block_types": ["Image", "Table"],
            "output_format": "application/json",
            "include_page_breaks": True,
            "chunking_strategy": chunking_strategy,
            "multipage_sections": multipage_sections,
            "max_characters": max_characters  # Limit the number of characters in each chunk
        }

        if chunking_strategy == "by_similarity":
            req_params["similarity_threshold"] = similarity_threshold

        req = shared.PartitionParameters(**req_params)
        response = client.general.partition(req)
        elements = response.elements  # Extracted elements

        # Output the JSON data
        print("Extracted JSON data:")
        print(json.dumps(elements, indent=4))

        # Return the JSON data for further processing
        return elements

    except SDKError as error:
        # Print the error message if an SDK error occurs
        print(f"Error extracting content: {error}")
        return None


def save_json_to_folder(json_data, folder_path, file_path, suffix, hi_res_model_name):
    """Saves the extracted JSON data to a specified folder."""
    os.makedirs(folder_path, exist_ok=True)
    base_filename = os.path.splitext(os.path.basename(file_path))[0]

    # Get current date and time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Include the hi_res_model_name in the file name
    file_path = os.path.join(folder_path, f"{base_filename}_{suffix}_{hi_res_model_name}_{current_time}.json")
    with open(file_path, "w") as json_file:
        json.dump(json_data, json_file, indent=4)


def main():
    # Define the file path
    filename = os.path.join(os.path.dirname(__file__), 'data/pdfs', 'Verifiable_Internet_for_Artificial_Intelligence_whitepaper.pdf')
    folder_path = os.path.join(os.path.dirname(__file__), 'data/jsons')

    # High-resolution model names:
    # 'yolox': Optimized for object detection tasks, including table and image extraction.
    # 'layout_v1.1.0': default high-res model

    # Chunking strategies:
    # 'basic': Combines sequential elements up to specified size limits.
    # 'by_title': Uses semantic chunking, understands the layout of the document, and makes intelligent splits.
    # 'by_page': Splits the document by pages.
    # 'by_similarity': Groups similar content together based on a similarity threshold.

    # Partitioning strategies:
    # auto (default strategy): The "auto" strategy will choose the partitioning strategy based on document characteristics and the function kwargs.
    # fast: The "rule-based" strategy leverages traditional NLP extraction techniques to quickly pull all the text elements. "Fast" strategy is not recommended for image-based file types.
    # hi_res: The "model-based" strategy identifies the layout of the document. The advantage of "hi_res" is that it uses the document layout to gain additional information about document elements. We recommend using this strategy if your use case is highly sensitive to correct classifications for document elements.
    # ocr_only: Another "model-based" strategy that leverages Optical Character Recognition to extract text from the image-based files.

    # Set the high-resolution model name, chunking strategy, and partitioning strategy
    hi_res_model_name = 'layout_v1.1.0'
    chunking_strategy = 'by_similarity'
    partitioning_strategy = 'hi_res'
    similarity_threshold = 0.9  # Relevant for 'by_similarity'
    max_characters = 5_000_000  # Limit the number of characters in each chunk default is 500
    multipage_sections = True  # Set based on document needs

    extracted_data = extract_content(filename, chunking_strategy, partitioning_strategy, multipage_sections, similarity_threshold, hi_res_model_name, max_characters)

    if extracted_data is None:
        print(f"Failed to extract content using {chunking_strategy} chunking.")
    else:
        save_json_to_folder(extracted_data, folder_path, filename, chunking_strategy, hi_res_model_name)
        print(f"JSON output saved successfully to {folder_path} with {chunking_strategy} chunking and {hi_res_model_name} model")


if __name__ == "__main__":
    main()