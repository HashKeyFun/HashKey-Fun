from uuid import uuid4

import boto3
import botocore
from flask import Blueprint, request, flash, redirect, current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
bp = Blueprint('file', __name__, url_prefix='/file')


def s3_connection():
    s3 = boto3.client(
            service_name="s3",
            region_name=current_app.config['S3_REGION'],
            aws_access_key_id=current_app.config['S3_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['S3_SECRET_KEY'],
        )
    return s3


def allowed_file(filename:str):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('image/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if not allowed_file(file.filename):
        flash('File type is not allowed.')
        return redirect(request.url)

    secure_name = secure_filename(file.filename)
    ext = secure_name.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid4()}.{ext}"

    try:
        # Connect to S3
        s3 = s3_connection()
        # Upload file to S3 with proper ContentType
        s3.upload_fileobj(
            Fileobj=file,
            Bucket=current_app.config['S3_BUCKET_NAME'],
            Key=unique_filename,
            ExtraArgs={
                'ContentType': file.content_type
            }
        )
    except botocore.exceptions.ClientError as e:
        current_app.logger.error(f"Error uploading file to S3: {e}")
        return {"message": "Failed to upload file"}, 500

        # Construct the file's URL on S3
    image_url = (
        f"https://{current_app.config['S3_BUCKET_NAME']}.s3."
        f"{current_app.config['S3_REGION']}.amazonaws.com/"
        f"{unique_filename}"
    )

    return {
        "message": "File uploaded successfully",
        "image_url": image_url
    }, 200