

def lambda_handler(event, context):
    routeKey = event["requestContext"]["routeKey"]
    print(f'this is routeKey: {routeKey}')

    return { 
        'statusCode' : 200
    }
