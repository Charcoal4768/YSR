import os
import dotenv
import json
import uuid
import io
from google.cloud import storage
from google.oauth2 import service_account
from werkzeug.utils import secure_filename
from PIL import Image
from urllib.parse import urlparse

# Load environment variables from a .env file
dotenv.load_dotenv()

# Global variables from environment settings
bucket_name = os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET')
google_credentials_file_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
gcp_sa_credentials_json = os.getenv('GCP_SA_CREDENTIALS')
project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')

def get_storage_client():
    """
    Returns a Google Cloud Storage client authenticated with credentials
    from either a file path or a JSON string environment variable.
    """
    if gcp_sa_credentials_json:
        credentials_info = json.loads(gcp_sa_credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        return storage.Client(credentials=credentials, project=project_id)
    elif google_credentials_file_path:
        return storage.Client(project=project_id)
    else:
        raise ValueError("No Google Cloud credentials found. Set either GOOGLE_APPLICATION_CREDENTIALS or GCP_SA_CREDENTIALS.")

def upload_file(file_stream, file_name, content_type="application/octet-stream") -> str:
    """
    Uploads a file stream to the Google Cloud Storage bucket.
    """
    client = get_storage_client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(secure_filename(file_name))
    file_stream.seek(0)
    blob.upload_from_file(file_stream, content_type=content_type)
    return blob.public_url

def delete_file_by_url(public_url: str) -> bool:
    """
    Deletes a file from GCS using its public URL.
    """
    if not public_url or not public_url.startswith(f"https://storage.googleapis.com/{bucket_name}/"):
        print(f"Invalid or non-GCS URL provided: {public_url}")
        return False
    
    try:
        client = get_storage_client()
        bucket = client.bucket(bucket_name)
        parsed_url = urlparse(public_url)
        blob_name = parsed_url.path.split('/')[-1]
        
        if not blob_name:
            print(f"Could not extract blob name from URL: {public_url}")
            return False

        blob = bucket.blob(blob_name)
        if blob.exists():
            blob.delete()
            print(f"Successfully deleted {blob_name} from bucket {bucket_name}.")
            return True
        else:
            print(f"Blob {blob_name} does not exist in bucket {bucket_name}.")
            return False
    except Exception as e:
        print(f"Error deleting file from GCS: {e}")
        return False

def generate_signed_url(file_name: str, expiration: int) -> str:
    """
    Generates a signed URL for a file, allowing temporary access.
    """
    client = get_storage_client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.generate_signed_url(version="v4", expiration=expiration, method="GET")

def upload_and_optimize_file(file_stream, original_file_name: str) -> str:
    """
    Optimizes and uploads an image file, converting it to WebP
    and assigning a randomized, unique filename.
    """
    _, file_extension = os.path.splitext(original_file_name)
    file_extension = file_extension.lower()
    unique_name = str(uuid.uuid4())
    
    if file_extension in ['.jpg', '.jpeg', '.png']:
        try:
            img = Image.open(file_stream)
            output_stream = io.BytesIO()
            img.save(output_stream, format="WEBP", quality=85)
            new_file_name = f"{unique_name}.webp"
            new_content_type = "image/webp"
            return upload_file(output_stream, new_file_name, new_content_type)
        except Exception as e:
            print(f"Failed to optimize image: {e}. Uploading original file.")
            new_file_name = f"{unique_name}{file_extension}"
            new_content_type = f"image/{file_extension.strip('.')}"
            return upload_file(file_stream, new_file_name, new_content_type)
    else:
        new_file_name = f"{unique_name}{file_extension}"
        new_content_type = f"application/{file_extension.strip('.')}"
        return upload_file(file_stream, new_file_name, new_content_type)