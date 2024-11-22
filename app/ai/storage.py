import boto3
from botocore.client import Config

s3 = boto3.client(
    's3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id='твой_ключ',
    aws_secret_access_key='твой_секрет',
    config=Config(signature_version='s3v4')
)

def get_instruction_file(bucket_name: str, file_key: str):
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    return response['Body'].read().decode('utf-8')

def list_files_recursive(bucket: str, prefix: str = '') -> list:
    paginator = s3.get_paginator('list_objects_v2')
    files = []
    
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if 'Contents' in page:
            for obj in page['Contents']:
                if not obj['Key'].endswith('/'): # пропускаем сами папки
                    files.append(obj['Key'])
    return files

def get_files_by_category(bucket: str, category: str) -> list:
    return list_files_recursive(bucket, f'{category}/')

# # Получаем список файлов из бакета
# files = s3.list_objects_v2(Bucket='твой_бакет')

# for obj in files['Contents']:
#     content = get_instruction_file('твой_бакет', obj['Key'])
#     # Дальше работаем с контентом

# # Получаем файлы по категориям
# dev_docs = get_files_by_category('твой_бакет', 'development')
# api_docs = get_files_by_category('твой_бакет', 'api')
# user_docs = get_files_by_category('твой_бакет', 'user-guides')

# # И даже метки можно добавлять при индексации
# for file_key in dev_docs:
#     content = get_instruction_file('твой_бакет', file_key)
#     # При создании индекса добавляем метку категории
#     # Потом можно будет искать только в определенной категории