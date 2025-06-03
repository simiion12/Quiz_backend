from fastapi import APIRouter, UploadFile, HTTPException, Path, Form
from src.database.aws_s3 import S3Handler
from src.config import s3_client, BUCKET_NAME


router = APIRouter(prefix="/s3", tags=["s3"])
s3_handler = S3Handler(s3_client, bucket_name=BUCKET_NAME)


@router.post("/")
async def upload_image(file: UploadFile):
    file_key = f"quiz_images/{file.filename}"
    try:
        file_url = s3_handler.upload_file(file.file, file_key)
        return {"file_url": file_url[1], "file_key": file_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{file_key}")
async def delete_image(file_key: str):
    try:
        message = s3_handler.delete_file(file_key)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{file_key:path}")
async def update_image(file: UploadFile, file_key: str = Path(...)):
    try:
        success, file_url = s3_handler.upload_file(file.file, file_key)
        if not success:
            raise HTTPException(status_code=500, detail=file_url)  # file_url contains error message when success is False
        return {"file_url": file_url, "file_key": file_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))