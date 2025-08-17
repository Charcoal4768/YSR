import os
import dotenv
from google.cloud import storage

dotenv.load_dotenv()

bucket_name = os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET')
google_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def upload_file(file_stream, file_name, content_type="image/jpeg")->str:
    client = storage.Client()   
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_file(file_stream, content_type=content_type)
    blob.make_public()
    return blob.public_url

def generate_signed_url(file_name: str, expiration: int) -> str:
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.generate_signed_url(version="v4", expiration=expiration, method="GET")