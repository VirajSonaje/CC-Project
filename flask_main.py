from flask import Flask, redirect, url_for, request
import subprocess
import boto3
import base64
import uuid
import json

app = Flask(__name__)

@app.route("/",methods = ['POST'])
def readImageFile():

    AWS_REGION='us-east-1'
    AWS_ACCESS_KEY="AKIA3DVXYSAZCAPOFO4E"
    AWS_SECRET_ACCESS_KEY="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"

    INPUT_QUEUE_NAME="AlekhyaFirstQueue"
    OUTPUT_QUEUE_NAME="AlekhyaSecondQueue"

    MESSAGE_ATTRIBUTES=['ImageName','UID']

    sqs = boto3.resource("sqs",region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    input_queue = sqs.get_queue_by_name(QueueName=INPUT_QUEUE_NAME)
    output_queue = sqs.get_queue_by_name(QueueName=OUTPUT_QUEUE_NAME)
    
    uploaded_file = request.files['image_file']

    if uploaded_file.filename != '':

        encoded_string = base64.b64encode(uploaded_file.read()).decode('utf-8')
        msg_uuid=str(uuid.uuid4())

        response = input_queue.send_message(MessageBody=encoded_string, MessageAttributes={
            'ImageName': {
                'StringValue': uploaded_file.filename,
                'DataType': 'String'
            },
            'UID': {
                'StringValue': msg_uuid,
                'DataType': 'String'
            }
        })
    result=None
    while result is None:
        with open("globalMap.json", "r+") as file:
            data = json.load(file)
            file.close()

        if msg_uuid in data:
            result=data.pop(msg_uuid, None)
            with open("globalMap.json", "w") as file:
                json.dump(data, file)
                file.close()


    return "Req received; Msg sent to SQS; ID:" + str(response.get('MessageId')) + ": UID: " + msg_uuid + ": Final Result Label: " + result


    """
        #send_client = boto3.client("sqs",region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

        #queue = send_client.get_queue_by_name(QueueName=OUTPUT_QUEUE_NAME)
        #QueueUrl = "https://sqs.us-east-1.amazonaws.com/763815825458/AlekhyaFirstQueue"

        response = send_client.send_message(Entries=[
            {
                'Id': msg_uuid,
                'MessageBody': encoded_string,
                'MessageAttributes': {
                    'ImageName': {
                        'StringValue': uploaded_file.filename,
                        'DataType': 'String'
                    },
                    'UID': {
                        'StringValue': msg_uuid,
                        'DataType': 'String'
                    }
                }
            }
        ])
        
        response = send_client.send_message(
            QueueUrl=QueueUrl,
            DelaySeconds=10,
            MessageAttributes={
                'ImageName': {
                    'StringValue': uploaded_file.filename,
                    'DataType': 'String'
                },
                'UID': {
                    'StringValue': msg_uuid,
                    'DataType': 'String'
                }
            },
            MessageBody=encoded_string
        )
        """
        

