"""This will update chalice configuration in this project with secrets
loaded from an S3 bucket.
"""
from typing import Dict, Any
from infra_utils.load_secrets import update_config_file_with_secrets, load_secret_file_from_s3
import os

CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
CONF_PATH: str = os.path.join(
    CURRENT_DIR_PATH, ".chalice", "config.json"
)
BUCKET_NAME: str = 'holvi-lambdas'
CONF_FILE_NAME: str = 'settings.json'

if __name__ == "__main__":
    secrets: Dict[str, Any] = load_secret_file_from_s3(
        bucket_name=BUCKET_NAME,
        file_name=CONF_FILE_NAME,
    )
    update_config_file_with_secrets(
        path=CONF_PATH,
        secrets=secrets,
    )
