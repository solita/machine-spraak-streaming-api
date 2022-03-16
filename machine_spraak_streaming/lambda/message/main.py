import boto3
import os
import json
import base64
import io
from scipy.io import wavfile
import numpy as np


url = os.environ['websocket_callback_url']
# client = boto3.client('apigatewaymanagementapi', endpoint_url=url)

def lambda_handler(event, context):
    # print(event)

    routeKey = event["requestContext"]["routeKey"]
    print(f'this is routeKey: {routeKey}')

    connectionId = event["requestContext"]["connectionId"]
    print(f'this is connectionId: {connectionId}')


    if routeKey == "message":


        body = json.loads(event['body'])
        str_audio = body['sound']
        sample_rate = body['sampleRate']
        
        array_audio = np.fromstring(str_audio, dtype=np.float64, sep=',')

        audio = wavfile.write('/tmp/test.wav', sample_rate, array_audio)

        
        responseMessage = "executed succesfully"
        # response = client.post_to_connection(ConnectionId=connectionId, Data=json.dumps(responseMessage).encode('utf-8'))
        
        print(f'sent response: {responseMessage}')



    return { 
        'statusCode' : 200
    }
