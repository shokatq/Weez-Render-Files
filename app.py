from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient
import os
import json

app = Flask(__name__)

# 🔹 Azure Blob Storage Configuration
CONTAINER_NAME = "weez-files-metadata"
# 🔹 Initialize Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_METADATA_STORAGE_CONNECTION_STRING"))
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

@app.route('/metadata/<username>/<file_name>', methods=['GET'])
def get_metadata(username, file_name):
    try:
        # 🔹 Construct the metadata blob name
        metadata_blob_name = f"{username}/{file_name}.json"

        # 🔹 Check if the blob exists
        blob_client = container_client.get_blob_client(metadata_blob_name)
        if not blob_client.exists():
            return jsonify({"error": "Metadata not found"}), 404

        # 🔹 Download and parse the JSON metadata
        blob_data = blob_client.download_blob().readall()
        metadata = json.loads(blob_data)

        # 🔹 Extract relevant fields
        response_data = {
            "file_name": file_name,
            "document_title": metadata.get("document_title", "N/A"),
            "text_summary": metadata.get("data_summary", "No summary available."),
            "importance":metadata.get("importance", "N/A"),
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
