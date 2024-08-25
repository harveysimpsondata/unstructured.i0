import os
import json
from dotenv import load_dotenv
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError

# Load environment variables
load_dotenv()

# Initialize the client with API credentials
API_KEY = os.getenv("UNSTRUCTURED_API_KEY")
UNSTRUCTURED_URL = os.getenv("UNSTRUCTURED_API_URL")

client = UnstructuredClient(api_key_auth=API_KEY, server_url=UNSTRUCTURED_URL)

# Define the file path
filename = os.path.join(os.path.dirname(__file__), '..', 'data/pdfs', 'Verifiable_Internet_for_Artificial_Intelligence_whitepaper.pdf')

def extract_pdf_content(filename, chunking_strategy, max_characters=1024, multipage_sections=True, similarity_threshold=0.5):
    """Extracts and processes content from a PDF document using the unstructured.io API."""
    with open(filename, "rb") as file:
        # Read file content for processing
        file_content = file.read()

    # Create a Files object for the API request
    files = shared.Files(
        content=file_content,
        file_name=os.path.basename(filename),
    )

    # Define the parameters for the API request
    req_params = shared.PartitionParameters(
        files=files,
        strategy='hi_res',  # Use high-resolution strategy
        hi_res_model_name='yolox',  # Use the YOLOX model
        unique_element_ids=True,  # Use UUIDs for element IDs
        extract_image_block_types=["Image", "Table"],  # Extract images and tables
        chunking_strategy=chunking_strategy,  # Use chosen chunking strategy
        max_characters=max_characters,  # Max characters per chunk
        languages=["eng"],  # Specify language(s)
        coordinates=True,  # Include OCR bounding boxes if needed
        multipage_sections=multipage_sections,  # Respect page boundaries if needed
    )

    if chunking_strategy == "by_similarity":
        req_params.similarity_threshold = similarity_threshold

    try:
        # Send the request to partition the document
        response = client.general.partition(req_params)
        elements = response.elements  # Extracted elements

        # Clean up metadata
        for element in elements:
            metadata = element.get('metadata', {})
            metadata.pop('filename', None)
            metadata.pop('filetype', None)
            metadata.pop('languages', None)

        # Output the JSON data
        print("Extracted JSON data:")
        print(json.dumps(elements, indent=4))

        # Return the JSON data for further processing
        return elements

    except SDKError as error:
        # Print the error message if an SDK error occurs
        print(f"Error extracting PDF content: {error}")
        return None

def save_json_to_folder(json_data, folder_path, pdf_path):
    """Saves the extracted JSON data to a specified folder."""
    os.makedirs(folder_path, exist_ok=True)
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    file_path = os.path.join(folder_path, f"{base_filename}.json")
    with open(file_path, "w") as json_file:
        json.dump(json_data, json_file, indent=4)

def main():
    # Define chunking strategy and parameters
    chunking_strategy = 'by_title'  # Choose your strategy: 'basic', 'by_title', 'by_page', 'by_similarity'
    max_characters = 1024  # Adjust as needed
    multipage_sections = True  # Set based on document needs
    similarity_threshold = 0.5  # Relevant for 'by_similarity'

    # Extract content from the PDF
    extracted_data = extract_pdf_content(filename, chunking_strategy, max_characters, multipage_sections, similarity_threshold)
    
    if extracted_data is None:
        print("Failed to extract PDF content.")
        return

    # Save the JSON output to a specified folder
    folder_path = os.path.join(os.path.dirname(__file__), '..', 'data/json')
    save_json_to_folder(extracted_data, folder_path, filename)
    print(f"JSON output saved successfully to {folder_path}")

if __name__ == "__main__":
    main()
