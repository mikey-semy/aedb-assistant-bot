import os
from typing import List
import asyncio
from aioboto3 import Session
import aiofiles
from botocore.exceptions import ClientError
from functools import wraps
#===============================================================================

import dotenv
dotenv.load_dotenv(".env.test")

AWS_ENDPOINT=os.getenv('AWS_ENDPOINT')
AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION=os.getenv('AWS_REGION')
AWS_BUCKET_NAME=os.getenv('AWS_BUCKET_NAME')
#===============================================================================
class S3Client:
    """
    Класс для работы с S3
    args:
        aws_access_key_id: str - AWS access key id
        aws_secret_access_key: str - AWS secret access key
        region_name: str - AWS region name
        endpoint_url: str - AWS endpoint url
    
    usage:
    @s3_client_decorator(
        aws_access_key_id='YOUR_ACCESS_KEY',
        aws_secret_access_key='YOUR_SECRET_KEY',
        region_name='YOUR_REGION',
        endpoint_url='YOUR_ENDPOINT_URL'
    )
    async def upload_file_to_s3(s3_client: S3Client, bucket_name: str, file_path: str, file_key: str):
        await s3_client.upload_file(bucket_name, file_path, file_key)

    async def main():
        await upload_file_to_s3('your-bucket-name', 'path/to/your/file', 'file-key-in-s3')

    if __name__ == "__main__":
        import asyncio
        asyncio.run(main())
    """
    def __init__(self, 
                 aws_access_key_id: str,
                 aws_secret_access_key: str,
                 region_name: str,
                 endpoint_url: str) -> None:
        self.s3=None
        self.service_name='s3'
        self.region_name=region_name
        self.endpoint_url=endpoint_url
        self.aws_access_key_id=aws_access_key_id
        self.aws_secret_access_key=aws_secret_access_key

    async def create_client(self):
        session = Session()
        self.s3 = await session.client(
            service_name=self.service_name,
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        ).__aenter__()
    
    async def close_client(self):
        """Закрытие клиента S3."""
        if self.s3:
            await self.s3.__aexit__(None, None, None)
    
    async def __aenter__(self):
        """Вход в контекстный менеджер."""
        await self.create_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекстного менеджера."""
        await self.close_client()
        
    async def bucket_exists(self, bucket_name: str) -> bool:
        """
        Проверка существования бакета.
        args:
            bucket_name: str - имя бакета
        return: bool
        """
        try:
            await self.s3.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
        raise ValueError(f'Ошибка при проверке наличия бакета: {e}') from e
    
    async def upload_file(self, bucket_name: str, file_path: str, file_key: str) -> None:
        """
        Загрузка файл-подобного объекта в S3.
        Файл должен быть открыт в бинарном режиме.
        args:
            bucket_name: str - имя бакета для загрузки файла
            file_path: str - путь к файлу для загрузки
            file_key: str - ключ файла в S3
        return: None
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Файл {file_path} не найден')
        try:
            async with aiofiles.open(file=file_path, mode='rb') as file:
                await self.s3.upload_fileobj(
                    Fileobj=file, 
                    Bucket=bucket_name, 
                    Key=file_key,
                )
        except ClientError as e:
            raise ValueError(f'Ошибка при загрузке файла: {e}') from e
        except IOError as e:
            raise ValueError(f'Ошибка при открытии файла: {e}') from e
        except Exception as e:
            raise RuntimeError(f'Ошибка при загрузке файла: {e}') from e
    
    async def download_file(self, bucket_name: str, file_key: str, file_path: str) -> None:
        """
        Скачивание файл-подобного объекта из S3.
        args:
            bucket_name: str - имя бакета для скачивания файла
            file_key: str - ключ файла в S3
            file_path: str - путь к файлу для скачивания
        return: None
        """
        try:
            async with aiofiles.open(file=file_path, mode='wb') as file:
                await self.s3.download_fileobj(
                    Bucket=bucket_name,
                    Key=file_key,
                    Fileobj=file
                )
        except ClientError as e:
            raise ValueError(f'Ошибка при скачивании файла: {e}') from e
        except IOError as e:
            raise ValueError(f'Ошибка при открытии файла для записи: {e}') from e
        except Exception as e:
            raise RuntimeError(f'Ошибка при скачивании файла: {e}') from e
    
    async def upload_multiple_files(self,
                                     bucket_name: str, 
                                     file_paths: List[str], 
                                     file_keys: List[str]
    ) -> List[str]:
        """
        Загрузка нескольких файлов в S3.
        args:
            bucket_name: str - имя бакета для загрузки файлов
            file_paths: List[str] - список путей к файлам для загрузки
            file_keys: List[str] - список ключей файлов в S3
        return: List[str] - список ключей загруженных файлов
        """
        uploaded_files = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f'Файл {file_path} не найден')
        try:
            for file_path, file_key in zip(file_paths, file_keys):
                await self.upload_file(bucket_name, file_path, file_key)
                uploaded_files.append(file_key)
            return uploaded_files
        except ClientError as e:
            raise ValueError(f'Ошибка при загрузке файлов: {e}') from e
        except IOError as e:
            raise ValueError(f'Ошибка при открытии файлов: {e}') from e
        except Exception as e:
            raise RuntimeError(f'Ошибка при загрузке файлов: {e}') from e
     
    async def download_multiple_files(self,
                                      bucket_name: str, 
                                      file_keys: List[str], 
                                      file_paths: List[str]
    ) -> List[str]:
        """
        Скачивание нескольких файлов из S3.
        args:
            bucket_name: str - имя бакета для скачивания файлов
            file_keys: List[str] - список ключей файлов в S3
            file_paths: List[str] - список путей к файлам для скачивания
        return: List[str] - список ключей скаченных файлов
        """
        downloaded_files = []
        try:
            for file_key, file_path in zip(file_keys, file_paths):
                await self.download_file(bucket_name, file_key, file_path)
                downloaded_files.append(file_key)
            return downloaded_files
        except ClientError as e:
            raise ValueError(f'Ошибка при скачивании файлов: {e}') from e
        except IOError as e:
            raise ValueError(f'Ошибка при открытии файлов для записи: {e}') from e
        except Exception as e:
            raise RuntimeError(f'Ошибка при скачивании файлов: {e}') from e
    
    async def get_list_files(self, bucket_name: str, prefix: str = '') -> List[str]:
        """
        Получение списка файлов в бакете.
        args:
            bucket_name: str - имя бакета для скачивания файлов
            prefix: str - префикс для фильтрации файлов
        return: List[str] - список ключей файлов в S3
        """
        try:
            response = await self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            files = []
            for obj in response.get('Contents', []):
                files.append(obj['Key'])
            return files
        except ClientError as e:
            raise ValueError(f'Ошибка при получении списка файлов: {e}') from e
        except Exception as e:
            raise RuntimeError(f'Ошибка при получении списка файлов: {e}') from e
 
    async def download_all_files(self, bucket_name: str, folder_path: str, prefix: str) -> None:
        """
        Скачивание всех файлов из бакета.
        args:
            bucket_name: str - имя бакета для скачивания файлов
            folder_path: str - путь к папке для скачивания файлов
            prefix: str - префикс для фильтрации файлов
        return: None
        """
        downloaded_files = []
        try:
            file_keys = await self.get_list_files(bucket_name, prefix)
            file_paths = [os.path.join(folder_path, file_key) for file_key in file_keys]
            downloaded_files = await self.download_multiple_files(bucket_name, file_keys, file_paths)
            return downloaded_files
        except ClientError as e:
            raise ValueError(f'Ошибка при скачивании файлов: {e}') from e
        except IOError as e:
            raise ValueError(f'Ошибка при открытии файлов для записи: {e}') from e
        except Exception as e:
            raise RuntimeError(f'Ошибка при скачивании файлов: {e}') from e

    async def delete_file(self, bucket_name: str,file_key: str) -> bool:
        """
        Удаление файла из бакета. 
        args:
            bucket_name: str - имя бакета для удаления файла
            file_key: str - ключ файла для удаления
        return: None
        """
        try:
            await self.s3.delete_object(
                    Bucket=bucket_name,
                    Key=file_key
                )
            return True
        except ClientError as e:
            raise ValueError(f'Ошибка при удалении файла из бакета: {e}') from e
        except Exception as e:
            raise RuntimeError(f'Ошибка при удалении файла из бакета: {e}') from e

    async def create_bucket(self, 
                             bucket_name: str) -> None:
        """
        Создание бакета в S3.
        args:
        bucket_name: str - имя бакета для создания
        return: None
        """
        try:
            await self.s3.create_bucket(Bucket=bucket_name)
        except ClientError as e:
            raise ValueError(f'Ошибка при создании бакета: {e}') from e
        except Exception as e:
            raise RuntimeError(f'Ошибка при создании бакета: {e}') from e
    
    def s3_client_decorator(self, aws_access_key_id, aws_secret_access_key, region_name, endpoint_url):
        """Декоратор для автоматического создания и закрытия S3Client."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                async with S3Client(aws_access_key_id, aws_secret_access_key, region_name, endpoint_url) as s3_client:
                    return await func(s3_client, *args, **kwargs)
            return wrapper
        return decorator
            
     
#===============================================================================       


async def main():
    file_path = os.path.join(os.path.dirname(__file__), 'test-file.txt')
    file_key = os.path.basename(file_path)
    #await s3.create_bucket('test-bucket')
    async with S3Client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_ENDPOINT) as s3:
        await s3.upload_file(
            bucket_name='drivers.data',
            file_path=file_path,
            file_key=file_key
        )
    # await s3.download_file('test-bucket', 'test-key', 'test-file')
    # await s3.delete_file('test-bucket', 'test-key')
    
if __name__ == '__main__':
    asyncio.run(main())
#===============================================================================