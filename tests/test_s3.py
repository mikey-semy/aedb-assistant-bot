import os
import pytest
import dotenv
from tests.s3_client import S3Client

dotenv.load_dotenv()

AWS_ENDPOINT=os.getenv('AWS_ENDPOINT')
AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION=os.getenv('AWS_REGION')
AWS_BUCKET_NAME=os.getenv('AWS_BUCKET_NAME')

@pytest.fixture
def s3_client():
    return S3Client(AWS_ACCESS_KEY_ID, 
                    AWS_SECRET_ACCESS_KEY, 
                    AWS_REGION, 
                    AWS_ENDPOINT)

async def test_upload_file(s3_client):
    file_path = os.path.join(os.path.dirname(__file__), 'test_file.txt')
    file_key = 'test_file.txt'
    await s3_client.upload_file(AWS_BUCKET_NAME, file_path, file_key)
    assert await s3_client.bucket_exists(AWS_BUCKET_NAME)
    assert await s3_client.delete_file(AWS_BUCKET_NAME, file_key)

async def test_upload_multiple_files(s3_client):
    file_paths = [os.path.join(os.path.dirname(__file__), 'test_file1.txt'), 
                  os.path.join(os.path.dirname(__file__), 'test_file2.txt')]
    file_keys = ['test_file1.txt', 'test_file2.txt']
    await s3_client.upload_multiple_files(AWS_BUCKET_NAME, file_paths, file_keys)
    assert await s3_client.bucket_exists(AWS_BUCKET_NAME)
    assert await s3_client.delete_file(AWS_BUCKET_NAME, file_keys[0])
    assert await s3_client.delete_file(AWS_BUCKET_NAME, file_keys[1])

async def test_download_file(s3_client):
    file_key = 'test_file.txt'
    file_path = os.path.join(os.path.dirname(__file__), 'test_file.txt')
    await s3_client.upload_file(AWS_BUCKET_NAME, file_path, file_key)
    await s3_client.download_file(AWS_BUCKET_NAME, file_key, file_path)
    assert os.path.exists(file_path)
    assert await s3_client.delete_file(AWS_BUCKET_NAME, file_key)

async def test_download_multiple_files(s3_client):
    file_keys = ['test_file1.txt', 'test_file2.txt']
    file_paths = [os.path.join(os.path.dirname(__file__), 'test_file1.txt'),
                  os.path.join(os.path.dirname(__file__), 'test_file2.txt')]
    await s3_client.upload_multiple_files(AWS_BUCKET_NAME, file_paths, file_keys)
    await s3_client.download_multiple_files(AWS_BUCKET_NAME, file_keys, file_paths)
    assert os.path.exists(file_paths[0])
    assert os.path.exists(file_paths[1])
    assert await s3_client.delete_file(AWS_BUCKET_NAME, file_keys[0])
    assert await s3_client.delete_file(AWS_BUCKET_NAME, file_keys[1])

async def test_delete_file(s3_client):
    file_key = 'test_file.txt'
    file_path = os.path.join(os.path.dirname(__file__), 'test_file.txt')
    await s3_client.upload_file(AWS_BUCKET_NAME, file_path, file_key)
    assert await s3_client.delete_file(AWS_BUCKET_NAME, file_key)