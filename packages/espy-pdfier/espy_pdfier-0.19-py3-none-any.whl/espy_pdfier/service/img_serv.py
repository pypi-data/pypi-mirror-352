import logging
import boto3
from PIL import Image
from typing import Tuple
from espy_pdfier.util import CONSTANTS
import os
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_greater_than_allowed_size(image_path):
    if not CONSTANTS.IMAGE_SIZE_MB:
        return False
    return os.path.getsize(image_path) > int(CONSTANTS.IMAGE_SIZE_MB) * 1024 * 1024


def is_image_size_valid(file):
    max_size_mb = float(CONSTANTS.IMAGE_SIZE_MB) * 1024 * 1024
    file_size_mb = file.file.seek(0, 2) / (1024 * 1024)  # Get file size in MB
    file.file.seek(0)  # Reset file pointer to the beginning
    return file_size_mb <= max_size_mb


def resize_image(image_bytes, max_size):
    """
    Resizes an image to the specified max size.

    Args:
        image_bytes: The image data as bytes.
        max_size: The maximum size (width, height) of the resized image.

    Returns:
        A BytesIO object containing the resized image data.
    """
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail(max_size)
    resized_image_buffer = io.BytesIO()
    image.save(resized_image_buffer, format=image.format)
    resized_image_buffer.seek(0)
    return resized_image_buffer


def store_image_in_s3(image_buffer, bucket_name, key) -> str:
    """Can be called directly to store image in S3.
    args:
    image_buffer: file.file from FastAPI file upload.
    returns:
    filename: name or key of the image in s3
    """
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )
        s3.upload_fileobj(image_buffer, bucket_name, key)
        return f"https://{bucket_name}.s3.amazonaws.com/{key}"
    except Exception as e:
        logging.error(f"An error occured uploadig to s3: {str(e)}")
        raise Exception(f"An error occured: {str(e)}.")


def store_video_in_s3(image_buffer, bucket_name, key) -> str:
    """Can be called directly to store image in S3.
    args:
    image_buffer: file.file from FastAPI file upload.
    returns:
    filename: name or key of the image in s3
    """
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )
        s3.upload_fileobj(image_buffer, bucket_name, key)
        return f"https://essl.b-cdn.net/{key}"
    except Exception as e:
        logging.error(f"An error occured uploadig to s3: {str(e)}")
        raise Exception(f"An error occured: {str(e)}.")


def store_zip_s3(zip_bytes, bucket_name, key) -> str:
    """Stores a zip directory of static content in s3."""
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )
        s3.upload_fileobj(
            zip_bytes, bucket_name, key, ExtraArgs={"ACL": "private"}
        )  # read only zip
        return f"https://essl.b-cdn.net/{key}"
    except Exception as e:
        logging.error(f"An error occured uploadig to s3: {str(e)}")
        raise Exception(f"An error occured: {str(e)}.")


def resize_and_store_images(
    image,
    bucket_name: str,
    thumbnail_size: Tuple[int, int] = (100, 100),
    display_size: Tuple[int, int] = (512, 512),
) -> dict[str, str]:
    """Resizes image (only) to thumbnail and display image while still keeping raw."""
    try:
        if not is_image_size_valid(image):
            raise ValueError("Image size exceeds the allowed limit.")
        name = image.filename
        raw_name = f"raw_{image.filename}"

        store_image_in_s3(image.file, bucket_name, raw_name)

        thumbnail_image = resize_image(image, thumbnail_size)
        display_image = resize_image(image, display_size)

        filename_thumb = f"thumb_{name}"
        store_image_in_s3(thumbnail_image, bucket_name, filename_thumb)

        filename_dp = f"dp_{name}"
        store_image_in_s3(display_image, bucket_name, filename_dp)
        return {
            "thumbnail": f"https://{bucket_name}.s3.amazonaws.com/{filename_thumb}",
            "dp": f"https://{bucket_name}.s3.amazonaws.com/{filename_dp}",
            "raw": f"https://{bucket_name}.s3.amazonaws.com/{raw_name}",
        }

    except Exception as e:
        logging.error(f"An error occurred resizing and storing: {str(e)}")
        raise Exception(f"An error occurred: {str(e)}.")
