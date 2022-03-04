import boto3
import os
import json
import base64
import io
from scipy.io.wavfile import read, write


url = os.environ['websocket_callback_url']
# client = boto3.client('apigatewaymanagementapi', endpoint_url=url)

def lambda_handler(event, context):
    # print(event)

    routeKey = event["requestContext"]["routeKey"]
    print(f'this is routeKey: {routeKey}')

    connectionId = event["requestContext"]["connectionId"]
    print(f'this is connectionId: {connectionId}')


    if routeKey == "message":

        # print(event['body'])
        body = json.loads(event['body'])
        base64_coded_audio = body['base64']
        byte_audio = base64.b64decode(base64_coded_audio)

        print(type(byte_audio))
        rate, data = read(io.BytesIO(byte_audio))
        print(data)



        # data, samplerate = sf.read(io.BytesIO(byte_audio))

        # print(type(data))

        
        responseMessage = "executed succesfully"
        # response = client.post_to_connection(ConnectionId=connectionId, Data=json.dumps(responseMessage).encode('utf-8'))
        
        print(f'sent response: {responseMessage}')



    return { 
        'statusCode' : 200
    }
