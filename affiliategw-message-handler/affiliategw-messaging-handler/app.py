import json
import os
from typing import Any, Dict

import requests
from chalice import Chalice
from chalice.app import SQSEvent
from requests.models import Response

app = Chalice(app_name='affiliategw-messaging-handler')


sentry_dsn = os.environ.get('affiliategw_messaging_handler_sentry_dsn')
if sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[AwsLambdaIntegration()]
    )


QUEUE: str = 'affiliategw-tune-queue'
TARGET_URL: str = 'https://ncotflvio7.execute-api.eu-west-1.amazonaws.com/api/'


@app.on_sqs_message(queue=QUEUE, batch_size=1)  # type: ignore
def index(sqs_event: SQSEvent) -> None:
    """
    Receives an SQS message and send it as an https payload.
    """
    handler(sqs_event)


def handler(sqs_event: SQSEvent) -> None:
    event: Dict[str, Any] = sqs_event.to_dict()
    event_body: str = event['Records'][0]['body']
    usable_body: Dict[str, Any] = json.loads(event_body)
    response: Response = requests.post(url=TARGET_URL, json=usable_body)
    response.raise_for_status()
