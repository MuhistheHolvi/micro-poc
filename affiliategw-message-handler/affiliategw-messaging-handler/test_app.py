from typing import Any, Dict
from unittest import TestCase

from chalice.app import SQSEvent
from mock import patch
from requests.exceptions import HTTPError
from requests_mock import Mocker

from app import handler


class FakeLambdaContextIdentity(object):
    def __init__(self, cognito_identity_id: str, cognito_identity_pool_id: str) -> None:
        self.cognito_identity_id = cognito_identity_id
        self.cognito_identity_pool_id = cognito_identity_pool_id


class FakeLambdaContext(object):
    def __init__(self) -> None:
        self.function_name = 'test_name'
        self.function_version = 'version'
        self.invoked_function_arn = 'arn'
        self.memory_limit_in_mb = 256
        self.aws_request_id = 'id'
        self.log_group_name = 'log_group_name'
        self.log_stream_name = 'log_stream_name'
        self.identity = FakeLambdaContextIdentity('id', 'id_pool')
        # client_context is set by the mobile SDK and wont be set for chalice
        self.client_context = None

    def get_remaining_time_in_millis(self) -> int:
        return 500

    def serialize(self) -> Dict['str', Any]:
        serialized: Dict['str', Any] = {}
        serialized.update(vars(self))
        serialized['identity'] = vars(self.identity)
        return serialized


sqs_event_fixture = {
    'Records': [{
        'attributes': {
            'ApproximateFirstReceiveTimestamp': '1530576251596',
            'ApproximateReceiveCount': '1',
            'SenderId': 'sender-id',
            'SentTimestamp': '1530576251595'
        },
        'awsRegion': 'us-west-2',
        'body': '{"test": "payload"}',
        'eventSource': 'aws:sqs',
        'eventSourceARN': 'arn:aws:sqs:us-west-2:12345:queue-name',
        'md5OfBody': '754ac2f7a12df38320e0c5eafd060145',
        'messageAttributes': {},
        'messageId': 'message-id',
        'receiptHandle': 'receipt-handle'
    }]}
lambda_context = FakeLambdaContext()
SQSEvent = SQSEvent(event_dict=sqs_event_fixture, context=lambda_context)

not_a_website = 'https://not-a-website.fi'


class IndexTest(TestCase):
    @Mocker()  # type: ignore
    def test_index(self, mocker: Mocker) -> None:
        mocker.register_uri(
            'POST', not_a_website, json={"success": "result"}, status_code=200
        )
        with patch('app.TARGET_URL', not_a_website):
            handler(sqs_event=SQSEvent)
        expected_request_payload: Dict[str, str] = {"test": "payload"}
        self.assertDictEqual(
            mocker.last_request.json(), expected_request_payload
        )

    @Mocker()  # type: ignore
    def test_index_on_fail(self, mocker: Mocker) -> None:
        mocker.register_uri(
            'POST', not_a_website, json={"fail": "result"}, status_code=404
        )
        with patch('app.TARGET_URL', not_a_website):
            with self.assertRaises(HTTPError):
                handler(sqs_event=SQSEvent)
