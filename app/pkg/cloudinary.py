import cloudinary
import cloudinary.uploader

from config import get_config

config = get_config()

# Init cloudinary config
cloudinary.config(
    cloud_name=config.cloudinary_cloud_name,
    api_key=config.cloudinary_api_key,
    api_secret=config.cloudinary_api_secret,
    secure=True
)


def upload_document(file_path: str, folder: str = "documents") -> dict:
    result = cloudinary.uploader.upload(
        file_path,
        folder=folder,
        resource_type="raw" 
    )
    return result


def delete_document(public_id: str) -> dict:
    result = cloudinary.uploader.destroy(public_id, resource_type="raw")
    return result
