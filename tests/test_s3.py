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


@pytest.mark.asyncio
async def test_upload_file():
    async with S3Client(AWS_ACCESS_KEY_ID, 
                         AWS_SECRET_ACCESS_KEY, 
                         AWS_REGION, 
                         AWS_ENDPOINT) as s3_client:
        file_path = os.path.join(os.path.dirname(__file__), 'test-file.txt')
        file_key = 'test-file.txt'
        await s3_client.upload_file(AWS_BUCKET_NAME, file_path, file_key)
        assert await s3_client.bucket_exists(AWS_BUCKET_NAME)
        assert await s3_client.delete_file(AWS_BUCKET_NAME, file_key)

@pytest.mark.asyncio
async def test_upload_multiple_files():
    async with S3Client(AWS_ACCESS_KEY_ID, 
                         AWS_SECRET_ACCESS_KEY, 
                         AWS_REGION, 
                         AWS_ENDPOINT) as s3_client:
        file_paths = [os.path.join(os.path.dirname(__file__), 'test-file1.txt'), 
                      os.path.join(os.path.dirname(__file__), 'test-file2.txt')]
        file_keys = ['test-file1.txt', 'test-file2.txt']
        await s3_client.upload_multiple_files(AWS_BUCKET_NAME, file_paths, file_keys)
        assert await s3_client.bucket_exists(AWS_BUCKET_NAME)
        assert await s3_client.delete_file(AWS_BUCKET_NAME, file_keys[0])
        assert await s3_client.delete_file(AWS_BUCKET_NAME, file_keys[1])

@pytest.mark.asyncio
async def test_download_file():
    async with S3Client(AWS_ACCESS_KEY_ID, 
                         AWS_SECRET_ACCESS_KEY, 
                         AWS_REGION, 
                         AWS_ENDPOINT) as s3_client:
        file_key = 'test-file.txt'
        file_path = os.path.join(os.path.dirname(__file__), 'test-file.txt')
        await s3_client.upload_file(AWS_BUCKET_NAME, file_path, file_key)
        await s3_client.download_file(AWS_BUCKET_NAME, file_key, file_path)
        assert os.path.exists(file_path)
        assert await s3_client.delete_file(AWS_BUCKET_NAME, file_key)

@pytest.mark.asyncio
async def test_download_multiple_files():
    async with S3Client(AWS_ACCESS_KEY_ID, 
                         AWS_SECRET_ACCESS_KEY, 
                         AWS_REGION, 
                         AWS_ENDPOINT) as s3_client:
        file_keys = ['test-file1.txt', 'test-file2.txt']
        file_paths = [os.path.join(os.path.dirname(__file__), 'test-file1.txt'),
                      os.path.join(os.path.dirname(__file__), 'test-file2.txt')]
        await s3_client.upload_multiple_files(AWS_BUCKET_NAME, file_paths, file_keys)
        await s3_client.download_multiple_files(AWS_BUCKET_NAME, file_keys, file_paths)
        assert os.path.exists(file_paths[0])
        assert os.path.exists(file_paths[1])
        assert await s3_client.delete_file(AWS_BUCKET_NAME, file_keys[0])
        assert await s3_client.delete_file(AWS_BUCKET_NAME, file_keys[1])

@pytest.mark.asyncio
async def test_delete_file():
    async with S3Client(AWS_ACCESS_KEY_ID, 
                         AWS_SECRET_ACCESS_KEY, 
                         AWS_REGION, 
                         AWS_ENDPOINT) as s3_client:
        file_key = 'test-file.txt'
        file_path = os.path.join(os.path.dirname(__file__), 'test-file.txt')
        await s3_client.upload_file(AWS_BUCKET_NAME, file_path, file_key)
        assert await s3_client.delete_file(AWS_BUCKET_NAME, file_key)