from chalice import Chalice
import math
import requests
import boto3
import json
app = Chalice(app_name='poc')
app.debug = True

@app.on_sqs_message(queue='poc', batch_size=1)
def index(event):
    lambda_url = 'https://ff4i7py4k0.execute-api.eu-west-1.amazonaws.com/api/'
    # Extract the number.
    event_body = json.loads(extract_body(event.to_dict()))
    app.log.info("Message body: %s", event_body)
    number = int(event_body['number'])
    
    # Calculate factorial
    result = math.factorial(number)
    
    # Form a payload
    result_payload = {'result': result, 'question': event_body}
    
    app.log.info("Message body: %s", event_body)
    app.log.info("Result: %s", result_payload)
    
    response = requests.post(
        url=lambda_url,
        json=result_payload
    )
    response.raise_for_status()
    return "Done!"


def extract_body(sqs_record):
    return sqs_record['Records'][0]['body']