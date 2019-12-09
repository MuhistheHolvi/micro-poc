from typing import Dict, Any
import boto3
import json
import os


CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DEFAULT_CONF_PATH: str = os.path.join(
    CURRENT_DIR_PATH, ".chalice", "config.json"
)
DEFAULT_BUCKET_NAME: str = 'holvi-lambdas'
DEFAULT_CONF_FILE_NAME: str = 'settings.json'


def load_secret_file_from_s3(
        bucket_name: str, file_name: str) -> Dict[str, Any]:
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name, file_name)
    body: str = obj.get()['Body'].read()
    secrets: Dict[str, Any] = json.loads(body)
    return secrets


def update_config_file_from_s3_object(
        path: str, secrets: Dict[str, Any]) -> None:
    with open(path, 'r+') as file_obj:
        file_contents: str = file_obj.read()
        config: Dict[str, Any] = json.loads(file_contents)
        config = update_conf_with_prod_env_key(
            config=config, secrets=secrets
        )
        file_obj.write(json.dumps(config))


def update_conf_with_prod_env_key(
        config: Dict[str, Any], secrets: Dict[str, str]) -> Dict[str, Any]:
    stages = config['stages']
    stage_production = stages.get('prod', {})
    environment_variables = stage_production.get('environment_variables', {})
    environment_variables.update(secrets)
    stage_production['environment_variables'] = environment_variables
    stages["prod"] = stage_production
    return config
