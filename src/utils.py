import os
from dotenv import load_dotenv
load_dotenv()
import uuid
from .mongo import qr_collection
import boto3

S3_BUCKET = os.getenv('S3_BUCKET')
S3_REGION = os.getenv('S3_REGION')
s3_client = boto3.client('s3', region_name=S3_REGION)

def upload_to_s3(file_stream, file_name):
    """Upload a file object to S3 and return its URL."""
    data = s3_client.upload_fileobj(file_stream, S3_BUCKET, file_name, ExtraArgs={'ContentType': 'image/png', 'ACL': 'public-read'})
    print(data)
    return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_name}"

def generate_unique_token():
    return str(uuid.uuid4())

def store_qr_code(restaurant_id, table_number):
    unique_token = generate_unique_token()

    qr_data = {
        "restaurant_id": restaurant_id,
        "table_number": table_number,
        "qr_token": unique_token,
        "qr_url": "",
        "status": "active",
    }
    
    qr_collection.insert_one(qr_data)
    return unique_token