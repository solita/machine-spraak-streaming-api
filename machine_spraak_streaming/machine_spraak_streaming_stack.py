from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigatewayv2_alpha as apiGateway,
    aws_apigatewayv2_integrations_alpha as integrations
)
from constructs import Construct
from os import path


dirname = path.dirname(__file__)

class MachineSpraakStreamingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # for each API route, we define its own lambda function to handle
        # the incoming data.
        # This could also be done with one larger lambda function that has if/else flows
        # depending on the route.
        connect_handler = lambda_.Function(self, "connectApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_7,
            handler="main.lambda_handler",
            code=lambda_.Code.from_asset(path.join(dirname, "lambda/connect"))
        )

        disconnect_handler = lambda_.Function(self, "disconnectApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_7,
            handler="main.lambda_handler",
            code=lambda_.Code.from_asset(path.join(dirname, "lambda/disconnect"))
        )

        default_handler = lambda_.Function(self, "defaultApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_7,
            handler="main.lambda_handler",
            code=lambda_.Code.from_asset(path.join(dirname, "lambda/default"))
        )

        # creates websocket API with the default routes that it should have
        web_socket_api = apiGateway.WebSocketApi(self, "machine-spraak-websocket-api",
            connect_route_options = apiGateway.WebSocketRouteOptions(integration=integrations.WebSocketLambdaIntegration("ConnectIntegration", connect_handler)),
            disconnect_route_options=apiGateway.WebSocketRouteOptions(integration=integrations.WebSocketLambdaIntegration("DisconnectIntegration", disconnect_handler)),
            default_route_options=apiGateway.WebSocketRouteOptions(integration=integrations.WebSocketLambdaIntegration("DefaultIntegration", default_handler)),
        )

        web_socket_stage = apiGateway.WebSocketStage(self, "dev",
        web_socket_api=web_socket_api,
        stage_name="dev",
        auto_deploy=True
        )

        scipy_layer = lambda_.LayerVersion.from_layer_version_arn(self,
        "AWSLambda-Python37-SciPy1x	",
        "arn:aws:lambda:eu-west-1:399891621064:layer:AWSLambda-Python37-SciPy1x:115"
        )

        message_handler = lambda_.Function(self, "messageApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_7,
            handler="main.lambda_handler",
            code=lambda_.Code.from_asset(path.join(dirname, "lambda/message")),
            layers = [scipy_layer],
            environment={"websocket_callback_url" : web_socket_stage.callback_url},
        )
        

        # adds the custome route for sending audiodata
        web_socket_api.add_route("message",
            integration=integrations.WebSocketLambdaIntegration("MessageIntegration", message_handler)
        )
        
        # gives the lambda function permission to send data back to the client
        # NOTE: this gives permission at all stages, can be specified to only be part of specific stage
        web_socket_api.grant_manage_connections(message_handler)

        # This exports the websocket callback url which we need in the lambda functions
        # CfnOutput(self, "WebSocketCallbackUrl:", value=web_socket_stage.callback_url)
