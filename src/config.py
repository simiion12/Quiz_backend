import os
import boto3

from dotenv import load_dotenv

load_dotenv()


def get_env_or_raise(key: str) -> str:
    """Get an environment variable or raise an exception."""
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable {key} is not set")
    return value


s3_client = boto3.client(
    's3',
    aws_access_key_id=get_env_or_raise('AWS_ACCESS_KEY'),
    aws_secret_access_key=get_env_or_raise('AWS_ACCESS_SECRET_KEY'),
    region_name=get_env_or_raise('AWS_DEFAULT_REGION')
)
BUCKET_NAME = get_env_or_raise('BUCKET_NAME')

POSTGRES_HOST = get_env_or_raise("POSTGRES_HOST")
POSTGRES_PORT = get_env_or_raise("POSTGRES_PORT")
POSTGRES_USER = get_env_or_raise("POSTGRES_USER")
POSTGRES_PASSWORD = get_env_or_raise("POSTGRES_PASSWORD")
POSTGRES_DB = get_env_or_raise("POSTGRES_DB")
MONGO_USER = get_env_or_raise("MONGO_USER")
MONGO_PASSWORD = get_env_or_raise("MONGO_PASSWORD")