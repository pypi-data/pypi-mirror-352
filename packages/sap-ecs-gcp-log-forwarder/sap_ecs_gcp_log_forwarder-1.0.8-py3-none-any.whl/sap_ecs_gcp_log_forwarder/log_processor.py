import os
import requests
import gzip
import logging
from google.cloud import storage
from google.api_core.exceptions import PermissionDenied, Forbidden
from .config import (
    OUTPUT_METHOD,
    HTTP_ENDPOINT,
    TLS_CERT_PATH,
    TLS_KEY_PATH,
    AUTH_METHOD,
    AUTH_TOKEN,
    API_KEY,
    OUTPUT_DIR,
    COMPRESS_OUTPUT_FILE
)

def download_file(bucket_name, file_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        file = bucket.blob(file_name)
        return file.download_as_bytes()
    except (PermissionDenied, Forbidden):
        logging.error(f"Permission denied: Cannot access file gs://{bucket_name}/{file_name}. Ensure the service account has 'storage.objects.get' permission.")
        raise
    except Exception as e:
        logging.error(f"Failed to download file: gs://{bucket_name}/{file_name}, error: {e}")
        raise

def process_log_file(bucket_name, file_name):
    raw_content = download_file(bucket_name, file_name)
    # Try to decompress gzip content; if it fails, assume plain text
    try:
        text_content = gzip.decompress(raw_content).decode('utf-8')
    except Exception:
        text_content = raw_content.decode('utf-8')
    logs = text_content.split('\n')

    if OUTPUT_METHOD == 'files':
        # Strip the leading slash from file_name
        file_name = file_name.lstrip('/')
        # Construct the local path based on the file name
        local_path = os.path.join(OUTPUT_DIR, file_name)
        # Determine output path and opener based on compression setting
        if COMPRESS_OUTPUT_FILE:
            out_path = local_path if local_path.lower().endswith('.gz') else local_path + '.gz'
            logging.info(f"Output path: {out_path}")
            opener = lambda path: gzip.open(path, 'at')
        else:
            out_path = local_path[:-3] if local_path.lower().endswith('.gz') else local_path
            logging.info(f"Output path: {out_path}")
            opener = lambda path: open(path, 'a')
        # Create directories if they do not exist
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with opener(out_path) as file:
            for log in logs:
                if log.strip():
                    write_log_to_file(log, file)
    else:
        for log in logs:
            if log.strip():
                send_log_to_http(log)

def send_log_to_http(log):
    try:
        headers = {'Content-Type': 'application/json'}
        cert = None

        if TLS_CERT_PATH and TLS_KEY_PATH:
            cert = (TLS_CERT_PATH, TLS_KEY_PATH)

        if AUTH_METHOD == 'token' and AUTH_TOKEN:
            headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
        elif AUTH_METHOD == 'api_key' and API_KEY:
            headers['X-API-Key'] = API_KEY

        response = requests.post(HTTP_ENDPOINT, data=log, headers=headers, cert=cert)
        response.raise_for_status()
        logging.debug(f"Log {log} forwarded successfully to HTTP endpoint {HTTP_ENDPOINT}")
    except Exception as e:
        logging.error(f"Failed to forward log {log} to HTTP endpoint {HTTP_ENDPOINT}, error: {e}")

def write_log_to_file(log, file):
    if log.strip():  # Ensure that empty or whitespace-only lines are not written
        try:
            file.write(log + '\n')
            logging.debug(f"Log {log} written successfully to file {file.name}")
        except Exception as e:
            logging.error(f"Failed to write log {log} to file {file.name}, error: {e}")
