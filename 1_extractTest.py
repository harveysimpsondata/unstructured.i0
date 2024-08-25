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

    # Print the API key and URL to verify they are loaded correctly
    print(f"UNSTRUCTURED_API: {api_key}")
    print(f"UNSTRUCTURED_URL: {unstructured_url}")

    return api_key, unstructured_url



def test_extract_pdf_content(filename):
    """Test extraction of content from a PDF document using the unstructured.io API."""
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
            "strategy": 'fast',  # Use the 'fast' strategy for a quick test
            "output_format": "application/json"
        }

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
        print(f"Error extracting PDF content: {error}")
        return None



def save_json_to_folder(json_data, pdf_filename):

    """Saves the extracted JSON data to the specified folder with the desired naming convention."""
    # Define the output folder
    output_folder = os.path.join(os.path.dirname(__file__), 'data/jsons')
    os.makedirs(output_folder, exist_ok=True)

    # Create the output file name
    base_filename = os.path.splitext(os.path.basename(pdf_filename))[0]
    output_filename = f"{base_filename}_TEST.json"
    output_path = os.path.join(output_folder, output_filename)

    # Save the JSON data to the file
    with open(output_path, "w") as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"JSON data saved to {output_path}")



def main():
    # Define the file path
    filename = os.path.join(os.path.dirname(__file__), 'data/pdfs', 'Verifiable_Internet_for_Artificial_Intelligence_whitepaper.pdf')

    # Test extraction of content from the PDF
    extracted_data = test_extract_pdf_content(filename)

    if extracted_data is None:
        print("Failed to extract PDF content.")
    else:
        print("PDF content extracted successfully.")
        # Save the extracted JSON data to the specified folder
        save_json_to_folder(extracted_data, filename)


if __name__ == "__main__":
    main()