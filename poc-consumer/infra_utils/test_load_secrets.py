from moto import mock_s3
import boto3
import json
from unittest import TestCase
from mock import patch, mock_open
from load_secrets import update_config_file_from_s3_object
from load_secrets import update_conf_with_prod_env_key
from load_secrets import load_secret_file_from_s3


CONFIG_FIXTURE = {"key": "value", "stages": {"dev": {"secret": "Hush"}}}
SECRETS_FIXTURE = {"secret": "I like coke zero."}


class LoadSecretFileFromS3Test(TestCase):
    @staticmethod
    def _setup_s3_file(bucket: str, file_name: str, contents: str) -> None:
        """This function construct a mock s3 bucket and fills it with the data required

        Arguments:
            bucket {str} -- The name of the bucket. Must be AWS naming compatible.
            file_name {str} -- The object name in the bucket. Must be AWS naming compatible.
            contents {str} -- the contents of the file
        """
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket=bucket)
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket, Key=file_name, Body=contents)

    @mock_s3  # type: ignore
    def test_load_secret_file_from_s3(self) -> None:
        FIXTURE_FILE_CONTENTS = json.dumps(SECRETS_FIXTURE)
        BUCKET_FIXTURE = 'ampari'
        FILE_NAME_FIXTURE = 'vesi'
        self._setup_s3_file(
            bucket=BUCKET_FIXTURE,
            file_name=FILE_NAME_FIXTURE,
            contents=FIXTURE_FILE_CONTENTS
        )
        returned_secrets = load_secret_file_from_s3(
            bucket_name=BUCKET_FIXTURE, file_name=FILE_NAME_FIXTURE
        )
        self.assertEqual(returned_secrets, SECRETS_FIXTURE)


class AppendSecretsToProdEnvVars(TestCase):
    def test_append_secretes_to_prod_env_vars(self) -> None:
        config: str = json.dumps(CONFIG_FIXTURE)
        with patch('builtins.open', mock_open(read_data=config)) as mock_open_file:
            update_config_file_from_s3_object(path='not.a.path', secrets=SECRETS_FIXTURE)
        mock_open_file.assert_called_once_with('not.a.path', 'r+')
        expected_written_config = '{"key": "value", "stages": {"dev": {"secret": "Hush"}, "prod": {"environment_variables": {"secret": "I like coke zero."}}}}'
        mock_open_file.return_value.write.assert_called_once_with(expected_written_config)

    def test_with_mocked_updater_logic(self) -> None:
        config: str = json.dumps(CONFIG_FIXTURE)
        fixture_config_return = {"not.a.config": "No configs here"}
        with patch('builtins.open', mock_open(read_data=config)) as mock_open_file:
            with patch('load_secrets.update_conf_with_prod_env_key', autospec=True) as mock_updater:
                mock_updater.return_value = fixture_config_return
                update_config_file_from_s3_object(path='not.a.path', secrets=SECRETS_FIXTURE)
        mock_open_file.assert_called_once_with('not.a.path', 'r+')
        expected_written_config = '{"not.a.config": "No configs here"}'
        mock_open_file.return_value.write.assert_called_once_with(expected_written_config)


class TestAppendToEnvKey(TestCase):
    def test_append_to_env_key(self) -> None:
        updated_stages = update_conf_with_prod_env_key(
            secrets=SECRETS_FIXTURE, config=CONFIG_FIXTURE
        )
        self.assertDictEqual(
            updated_stages,
            {
                "key": "value",
                "stages": {
                    "dev": {"secret": "Hush"},
                    "prod": {
                        "environment_variables": {
                            "secret": "I like coke zero."
                        }
                    }
                }
            }
        )
