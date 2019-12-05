from chalice import Chalice
import boto3
import json
from datetime import datetime
app = Chalice(app_name='poc-consumer')
app.debug = True

@app.route('/', methods=['POST', 'PUT', 'GET'])
def index():
    request = app.current_request
    request_time = request.context['requestTime']
    request_id = request.context['identity']
    payload = json.dumps(request.json_body)
    if not payload:
        raise Exception('No payload')
    app.log.info("Payload is: %s", payload)
    sqs = boto3.resource('sqs')
    try:
        queue = sqs.get_queue_by_name(QueueName='output')
    except:
        queue = sqs.create_queue(QueueName='output')
    queue.send_message(MessageBody=payload)
    return {'hello': 'world'}


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
