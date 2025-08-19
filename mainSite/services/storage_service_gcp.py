import os
import dotenv
import json
from google.cloud import storage
from google.oauth2 import service_account

dotenv.load_dotenv()

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
        # Load credentials from the JSON string
        credentials_info = json.loads(gcp_sa_credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        return storage.Client(credentials=credentials, project=project_id)
    elif google_credentials_file_path:
        # The library will automatically use GOOGLE_APPLICATION_CREDENTIALS
        return storage.Client(project=project_id)
    else:
        raise ValueError("No Google Cloud credentials found. Set either GOOGLE_APPLICATION_CREDENTIALS or GCP_SA_CREDENTIALS.")

def upload_file(file_stream, file_name, content_type="image/jpeg")->str:
    client = get_storage_client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_file(file_stream, content_type=content_type)
    return blob.public_url

def generate_signed_url(file_name: str, expiration: int) -> str:
    client = get_storage_client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.generate_signed_url(version="v4", expiration=expiration, method="GET")