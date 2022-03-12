from flask import Flask, redirect, url_for, request
import subprocess
import boto3
import base64
import uuid
import json
from outSqsListener import outSqsLitener, globalMap

app = Flask(__name__)

@app.route("/",methods = ['POST'])
def readImageFile():

    AWS_REGION='us-east-1'
    AWS_ACCESS_KEY="AKIAQXBVY5HVCRFALTEM"
    AWS_SECRET_ACCESS_KEY="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"

    INPUT_QUEUE_NAME="InputQueue"
    OUTPUT_QUEUE_NAME="OutputQueue"
    
    s3 = boto3.client('s3')
    BUCKET_NAME = 'ccinputbucket'

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

        s3.upload_file(uploaded_file.filename, BUCKET_NAME, uploaded_file.filename)

    result=None

    while result is None:
        # with open("globalMap.json", "r") as file:
        #     data = json.load(file)
        #     if msg_uuid in data:
        #         result=data.pop(msg_uuid, None)
        #         file.close()
        #         return "Req received; Msg sent to SQS; ID:" + str(response.get('MessageId')) + ": UID: " + msg_uuid + ": Final Result Label: " + result            
        
        if msg_uuid in globalMap:
            # print(globalMap)
            print("found")
            result = globalMap[msg_uuid]
            globalMap.pop(msg_uuid)
            return "Req received; Msg sent to SQS; ID:" + str(response.get('MessageId')) + ": UID: " + msg_uuid + ": Final Result Label: " + result            
            

    # return "Req received; Msg sent to SQS; ID:" + str(response.get('MessageId')) + ": UID: " + msg_uuid + ": Final Result Label: " + result
        
if __name__ == '__main__':
    outThread = outSqsLitener("outThread")
    IsThreadworking = False
    if not IsThreadworking:
        IsThreadworking = True
        outThread.start()
    
    app.run(host='127.0.0.1', port=5002)
