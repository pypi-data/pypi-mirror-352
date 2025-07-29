import warnings
warnings.filterwarnings("ignore")

import os
import json
from pathlib import Path
import click
import keyring
import requests
from typing import List
import mimetypes
from tqdm import tqdm
import math

CONFIG_DIR = Path.home() / '.magicode'
CONFIG_FILE = CONFIG_DIR / 'config.json'
SERVICE_NAME = 'magicode'

URL_BASE = "https://www.magicode.ai/api"
# URL_BASE = "http://localhost:3000/api"

# File size constants
MULTIPART_THRESHOLD = 3 * 1024 * 1024 * 1024  # 3GB
CHUNK_SIZE = 50 * 1024 * 1024  # 50MB

def load_credentials():
    """Load credentials from config file if they exist"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def save_credentials(email, token):
    """Save credentials to config file"""
    CONFIG_DIR.mkdir(exist_ok=True)
    credentials = {
        'email': email,
        'token': token
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(credentials, f)

def get_credentials():
    """Get credentials from system keyring"""
    email = keyring.get_password(SERVICE_NAME, 'email')
    token = keyring.get_password(SERVICE_NAME, 'token')
    return email, token

def save_credentials_system(email, token):
    """Save credentials to system keyring"""
    keyring.set_password(SERVICE_NAME, 'email', email)
    keyring.set_password(SERVICE_NAME, 'token', token)

@click.group()
def cli():
    """MagiCode CLI tool"""
    pass

@cli.command()
def auth():
    """Authenticate with MagiCode"""
    # Check if credentials already exist
    existing_email, existing_token = get_credentials()
    if existing_email and existing_token:
        if not click.confirm('Credentials already exist. Do you want to overwrite them?'):
            click.echo('Authentication cancelled.')
            return

    email = click.prompt('Please enter your email')
    token = click.prompt('Please enter your secret token', hide_input=True)
    
    # Verify credentials before saving
    click.echo('Verifying credentials...')
    try:
        # Test credentials by requesting a presigned URL for a test file
        bucket_name = "magicode-user-data-store"
        verify_response = requests.post(
            f'{URL_BASE}/s3-cli',
            params={'bucket': bucket_name},
            json={
                'email': email,
                'secretKey': token,
                'fileName': 'test-verification.txt',
            }
        )
        
        if verify_response.status_code != 200:
            click.echo(f'Invalid credentials. Authentication failed.', err=True)
            return
            
        click.echo('Credentials verified successfully.')
        save_credentials(email, token)
        save_credentials_system(email, token)
        click.echo('Credentials saved.')
    except Exception as e:
        click.echo(f'Error verifying credentials: {str(e)}', err=True)

@cli.command()
def logout():
    """Clear stored credentials"""
    try:
        keyring.delete_password(SERVICE_NAME, 'email')
        keyring.delete_password(SERVICE_NAME, 'token')
        click.echo('Logged out successfully.')
    except keyring.errors.PasswordDeleteError:
        click.echo('No credentials found.')

@cli.command()
@click.argument('source')
@click.option('--destination', default='', help='Destination path to prepend to uploaded files (should end with /)')
def upload(source: str, destination: str):
    """Upload a file or folder to MagiCode
    
    SOURCE: Path to the file or folder to upload
    """
    # Get credentials
    email, token = get_credentials()
    if not email or not token:
        click.echo('Please authenticate first using the auth command.', err=True)
        return

    # Validate destination format if provided
    if destination and not destination.endswith('/'):
        click.echo('Destination path must end with a forward slash (/)', err=True)
        return

    path = Path(source)
    if not path.exists():
        click.echo(f'Path does not exist: {path}', err=True)
        return

    files_to_upload: List[Path] = []
    folders_to_upload: List[Path] = []
    
    # Collect all files and folders
    if path.is_file():
        files_to_upload.append(path)
    else:
        # Add the root folder if it's a directory
        folders_to_upload.append(path)
        # Collect all subdirectories and files
        for item in path.rglob('*'):
            if item.is_file():
                files_to_upload.append(item)
            elif item.is_dir():
                folders_to_upload.append(item)

    total_items = len(files_to_upload) + len(folders_to_upload)
    error = False 
    errored_items = []
    current_index = 0

    # Upload empty content for folders first
    for folder_path in folders_to_upload:
        current_index += 1
        try:
            click.echo(f'Creating folder {current_index}/{total_items}: {folder_path}/')
            
            # Get relative path for the folder and prepend destination if provided
            relative_path = folder_path.relative_to(path.parent)
            folder_key = str(relative_path) + '/' if not str(relative_path).endswith('/') else str(relative_path)
            if destination:
                folder_key = destination + folder_key

            # bucket name depends on the destination 
            bucket_name = "magicode-user-data-store"
            
            # Get presigned URL
            presigned_response = requests.post(
                'https://www.magicode.ai/api/s3-cli',
                params={'bucket': bucket_name},
                json={
                    'email': email,
                    'secretKey': token,
                    'fileName': folder_key,
                }
            )

            if presigned_response.status_code != 200:
                error = True
                errored_items.append(folder_path)
                continue

            presigned_data = presigned_response.json()
            presigned_url = presigned_data['presignedUrl']

            # Upload empty content for folder
            upload_response = requests.put(
                presigned_url,
                data=b'',
                headers={
                    'Content-Type': 'application/x-directory',
                    'Content-Length': '0'
                }
            )

            if upload_response.status_code not in (200, 204):
                error = True
                errored_items.append(folder_path)
                continue

        except Exception as e:
            error = True
            errored_items.append(folder_path)
            continue

    # Upload files
    for file_path in files_to_upload:
        current_index += 1
        try:
            click.echo(f'Uploading file {current_index}/{total_items}: {file_path}')
            
            # Get relative path for the file and prepend destination if provided
            relative_path = file_path.relative_to(path.parent)
            file_key = str(relative_path)
            if destination:
                file_key = destination + file_key

            # bucket name depends on the destination 
            bucket_name = "magicode-user-data-store"
            
            # Get file size
            file_size = os.path.getsize(file_path)
            content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            
            # Check if file is large enough for multipart upload
            if file_size > MULTIPART_THRESHOLD:
                # Use multipart upload for large files
                if not upload_large_file(file_path, file_key, bucket_name, email, token, content_type, file_size):
                    error = True
                    errored_items.append(file_path)
            else:
                # Use regular upload for smaller files
                # Get presigned URL
                presigned_response = requests.post(
                    'https://www.magicode.ai/api/s3-cli',
                    params={'bucket': bucket_name},
                    json={
                        'email': email,
                        'secretKey': token,
                        'fileName': file_key,
                    }
                )

                if presigned_response.status_code != 200:
                    error = True
                    errored_items.append(file_path)
                    continue

                presigned_data = presigned_response.json()
                presigned_url = presigned_data['presignedUrl']

                # Upload file using presigned URL with progress bar
                with open(file_path, 'rb') as f:
                    with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                        file_data = f.read()
                        
                        upload_response = requests.put(
                            presigned_url,
                            data=file_data,
                            headers={
                                'Content-Type': content_type,
                                'Content-Length': str(file_size)
                            }
                        )
                        pbar.update(file_size)  # Ensure bar reaches 100%

                if upload_response.status_code not in (200, 204):
                    error = True
                    errored_items.append(file_path)
                    continue

        except Exception as e:
            click.echo(f'Error uploading {file_path}: {str(e)}', err=True)
            error = True
            errored_items.append(file_path)
            continue

    if error:
        click.echo(f'Upload has completed with errors.') 
        click.echo(f'The following items were not uploaded:') 
        for item in errored_items: 
            click.echo(f'  - {item}') 
        click.echo(f'Please check your credentials and try again.')
    else: 
        click.echo('Upload completed successfully.')

def upload_large_file(file_path, file_key, bucket_name, email, token, content_type, file_size):
    """Upload a large file using multipart upload"""
    click.echo(f'File size is {file_size/1024/1024/1024:.2f} GB. Using multipart upload...')
    
    # Calculate number of parts
    num_parts = math.ceil(file_size / CHUNK_SIZE)
    
    try:
        # 1. Initiate multipart upload
        initiate_response = requests.post(
            f'{URL_BASE}/s3-cli-multipart',
            params={'bucket': bucket_name, 'action': 'initiate'},
            json={
                'email': email,
                'secretKey': token,
                'fileName': file_key,
                'contentType': content_type
            }
        )
        
        if initiate_response.status_code != 200:
            click.echo(f'Failed to initiate multipart upload: {initiate_response.text}', err=True)
            return False
            
        initiate_data = initiate_response.json()
        upload_id = initiate_data['uploadId']
        s3_key = initiate_data['key']
        
        click.echo(f'Initiated multipart upload with ID: {upload_id}')
        
        # 2. Upload parts
        part_info = []
        
        with tqdm(total=num_parts, desc="Uploading parts", unit="part") as pbar:
            for part_number in range(1, num_parts + 1):
                # Get presigned URLs for this part
                urls_response = requests.post(
                    f'{URL_BASE}/s3-cli-multipart',
                    params={'bucket': bucket_name, 'action': 'getUrls'},
                    json={
                        'email': email,
                        'secretKey': token,
                        'key': s3_key,
                        'uploadId': upload_id,
                        'partNumbers': [part_number]
                    }
                )
                
                if urls_response.status_code != 200:
                    click.echo(f'Failed to get presigned URL for part {part_number}: {urls_response.text}', err=True)
                    # Abort the multipart upload
                    requests.post(
                        f'{URL_BASE}/s3-cli-multipart',
                        params={'bucket': bucket_name, 'action': 'abort'},
                        json={
                            'email': email,
                            'secretKey': token,
                            'key': s3_key,
                            'uploadId': upload_id
                        }
                    )
                    return False
                
                urls_data = urls_response.json()
                part_url = urls_data['presignedUrls'][0]['presignedUrl']
                
                # Calculate byte range for this part
                start_byte = (part_number - 1) * CHUNK_SIZE
                end_byte = min(start_byte + CHUNK_SIZE, file_size)
                part_size = end_byte - start_byte
                
                # Read the chunk from the file
                with open(file_path, 'rb') as f:
                    f.seek(start_byte)
                    part_data = f.read(part_size)
                
                # Upload the part
                part_response = requests.put(
                    part_url,
                    data=part_data,
                    headers={'Content-Length': str(part_size)}
                )
                
                if part_response.status_code not in (200, 204):
                    click.echo(f'Failed to upload part {part_number}: {part_response.text}', err=True)
                    # Abort the multipart upload
                    requests.post(
                        'https://www.magicode.ai/api/s3-cli-multipart',
                        params={'bucket': bucket_name, 'action': 'abort'},
                        json={
                            'email': email,
                            'secretKey': token,
                            'key': s3_key,
                            'uploadId': upload_id
                        }
                    )
                    return False
                
                # Get the ETag from the response headers
                etag = part_response.headers.get('ETag')
                part_info.append({
                    'PartNumber': part_number,
                    'ETag': etag
                })
                
                pbar.update(1)
        
        # 3. Complete multipart upload
        click.echo('Finalizing multipart upload...')
        complete_response = requests.post(
            f'{URL_BASE}/s3-cli-multipart',
            params={'bucket': bucket_name, 'action': 'complete'},
            json={
                'email': email,
                'secretKey': token,
                'key': s3_key,
                'uploadId': upload_id,
                'parts': part_info
            }
        )
        
        if complete_response.status_code != 200:
            click.echo(f'Failed to complete multipart upload: {complete_response.text}', err=True)
            return False
            
        click.echo('Multipart upload completed successfully.')
        return True
        
    except Exception as e:
        click.echo(f'Error during multipart upload: {str(e)}', err=True)
        # Try to abort the upload if possible
        try:
            if 'upload_id' in locals() and 's3_key' in locals():
                requests.post(
                    f'{URL_BASE}/s3-cli-multipart',
                    params={'bucket': bucket_name, 'action': 'abort'},
                    json={
                        'email': email,
                        'secretKey': token,
                        'key': s3_key,
                        'uploadId': upload_id
                    }
                )
        except:
            pass
        return False

if __name__ == '__main__':
    cli()
