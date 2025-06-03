from typing import BinaryIO
from botocore.exceptions import ClientError


class S3Handler:
    def __init__(self, s3_client, bucket_name: str):
        self.s3_client = s3_client
        self.bucket_name = bucket_name


    def upload_file(self, file: BinaryIO, file_key: str) -> tuple[bool, str]:
        """
        Upload a file to S3 bucket
        Returns: Tuple of (success, url or error message)
        """
        try:
            self.s3_client.upload_fileobj(file, self.bucket_name, file_key)
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"
            return True, url
        except ClientError as e:
            return False, str(e)


    def delete_file(self, file_key: str) -> tuple[bool, str]:
        """
        Delete a file from S3 bucket
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True, "File deleted successfully"
        except ClientError as e:
            return False, str(e)


    def update_s3_image(self, file: BinaryIO, file_key: str) -> tuple[bool, str]:
        """
        Update an existing file in S3 bucket by uploading a new one with the same key
        Returns: Tuple of (success, url or error message)
        """
        try:
            self.s3_client.upload_fileobj(file, self.bucket_name, file_key)
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"
            return True, url
        except ClientError as e:
            return False, str(e)
