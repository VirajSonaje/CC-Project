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
    AWS_ACCESS_KEY=""
    AWS_SECRET_ACCESS_KEY=""

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
        

