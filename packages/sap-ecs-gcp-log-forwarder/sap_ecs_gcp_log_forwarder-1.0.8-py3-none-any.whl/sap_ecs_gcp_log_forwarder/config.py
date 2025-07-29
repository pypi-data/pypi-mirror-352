import os
from dotenv import load_dotenv, find_dotenv

# Load .env file if present in the current directory
dotenv_path = find_dotenv(filename=".env", raise_error_if_not_found=False, usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path)
    print(f"Loaded .env from: {dotenv_path}")
else:
    print(f"No .env file found in the current directory.")

def get_env(name, default=None, required=False, cast=None):
    """Retrieve and optionally cast/validate an environment variable."""
    value = os.getenv(name, default)
    # Trim whitespace for string values
    if isinstance(value, str):
        value = value.strip()
    if required and (value is None or str(value) == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")
    if cast and value is not None:
        try:
            value = cast(value)
        except Exception as e:
            raise RuntimeError(f"Error casting env var {name}: {e}")
    return value

# Required settings
GOOGLE_APPLICATION_CREDENTIALS = get_env("GOOGLE_APPLICATION_CREDENTIALS", required=True) # Service account key file
LOGSERV_PROJECT_ID = get_env("LOGSERV_PROJECT_ID", required=True)
LOGSERV_PUBSUB_SUBSCRIPTION_NAME = get_env("LOGSERV_PUBSUB_SUBSCRIPTION_NAME", required=True)
OUTPUT_METHOD = get_env("OUTPUT_METHOD", required=True, cast=lambda v: v.lower()) # Output method: 'http' or 'files'.

# Optional settings
TIMEOUT_DURATION = get_env("TIMEOUT_DURATION", default=None, cast=lambda v: int(v) if v else None)
LOGSERV_LOG_FILTERS = get_env(
    "LOGSERV_LOG_FILTERS",
    default="",
    cast=lambda v: [s.strip().lower() for s in v.split(",") if s.strip()]
)

# For http output method
HTTP_ENDPOINT = get_env("HTTP_ENDPOINT", default=None)
TLS_CERT_PATH = get_env("TLS_CERT_PATH", default=None)
TLS_KEY_PATH = get_env("TLS_KEY_PATH", default=None)
AUTH_METHOD = get_env("AUTH_METHOD", default=None, cast=lambda v: v.lower()) # 'token' or 'api_key'.
AUTH_TOKEN = get_env("AUTH_TOKEN", default=None)
API_KEY = get_env("API_KEY", default=None)

# For files output method
OUTPUT_DIR = get_env(
    "OUTPUT_DIR",
    default=None,
    cast=lambda v: os.path.normpath(v.strip()) + os.path.sep if v.strip() else v # Ensure OUTPUT_DIR ends with a trailing slash
)
COMPRESS_OUTPUT_FILE = get_env(
    "COMPRESS_OUTPUT_FILE",
    default="true",
    cast=lambda v: v.lower() in ("true", "1", "yes")
)
LOG_LEVEL = get_env("LOG_LEVEL", default="INFO", cast=lambda v: v.upper())  # 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

# -------------------------------------------------------
# Extra validations
# -------------------------------------------------------
if OUTPUT_METHOD not in ("http", "files"):
    raise RuntimeError(f"Invalid OUTPUT_METHOD: {OUTPUT_METHOD}. It has to be either 'http' or 'files'.")

if OUTPUT_METHOD == "http":
    # HTTP-specific requirements
    if not HTTP_ENDPOINT:
        raise RuntimeError("HTTP_ENDPOINT is required when OUTPUT_METHOD is 'http'.")
    if AUTH_METHOD not in ("token", "api_key"):
        raise RuntimeError(f"Invalid AUTH_METHOD: {AUTH_METHOD}. It has to be either 'token' or 'api_key'.")
    if AUTH_METHOD == "token" and not AUTH_TOKEN:
        raise RuntimeError("AUTH_TOKEN is required when AUTH_METHOD is 'token'.")
    if AUTH_METHOD == "api_key" and not API_KEY:
        raise RuntimeError("API_KEY is required when AUTH_METHOD is 'api_key'.")
else:  # OUTPUT_METHOD == "files"
    if not OUTPUT_DIR:
        raise RuntimeError("OUTPUT_DIR is required when OUTPUT_METHOD is 'files'.")
    
# Validate log level
if LOG_LEVEL not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
    raise RuntimeError(f"Invalid LOG_LEVEL: {LOG_LEVEL}. It has to be one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.")