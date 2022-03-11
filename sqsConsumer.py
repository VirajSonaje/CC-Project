import os
import boto3
#from common import SignalHandler, process_message, send_queue_metrics
from signal import SIGINT, SIGTERM, signal
from PIL import Image
from io import BytesIO
import base64
import subprocess


#queueUrl = "https://sqs.us-east-1.amazonaws.com/763815825458/AlekhyaFirstQueue"
#dlq = sqs.get_queue_by_name(QueueName=os.environ["SQS_DEAD_LETTER_QUEUE_NAME"])

def process_message(message):
    #print(dir(message))
    """
    ['Queue', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_queue_url', '_receipt_handle', 'attributes', 'body', 'change_visibility', 'delete', 'get_available_subresources', 'md5_of_body', 'md5_of_message_attributes', 'message_attributes', 'message_id', 'meta', 'queue_url', 'receipt_handle']
    """

    #print(f"processing message: {message}")
    print(f"message body: {message.body}")
    print("----")
    print(f"message id: {message.message_id}")
    
    image_name="default.jpg"
    uid="default"

    if message.message_attributes is not None:
        image_name = message.message_attributes.get('ImageName').get('StringValue')
        uid = message.message_attributes.get('UID').get('StringValue')
        print("----")
        print("Image Name: ",image_name)
        print("----")
        print("UID: ",uid)

    print("--------------------------")

    #TO DO
    #Call face_recognition.py for result and store in 'name'
    im = Image.open(BytesIO(base64.b64decode(message.body)))
    im.save("face_images_100/" + image_name)
    output = subprocess.run(["python3", "face_recognition.py", "face_images_100/" + image_name], capture_output=True)
    #label = output.stdout.decode("utf-8").rstrip("\n")
    #name = label if label else 'Paul' #Default - NEED TO CHANGE
    name='Paul'

    #TO DO
    #Store images in S3 Input and Output Buckets

    result = {
        'ImageName' : image_name,
        'Name' : name,
        'UID': uid
    }

    return result

def send_message(result,output_queue):
    response = output_queue.send_message(MessageBody=result['Name'], MessageAttributes={
        'ImageName': {
            'StringValue': result['ImageName'],
            'DataType': 'String'
        },
        'UID': {
            'StringValue': result['UID'],
            'DataType': 'String'
        }
    })
    print("----")
    print("Msg sent to output queue, ID: ",response.get('MessageId'))

    pass

class SignalHandler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        print(f"handling signal {signal}, exiting gracefully")
        self.received_signal = True

if __name__ == "__main__":

    AWS_REGION='us-east-1'
    AWS_ACCESS_KEY="AKIA3DVXYSAZCAPOFO4E"
    AWS_SECRET_ACCESS_KEY="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"

    INPUT_QUEUE_NAME="AlekhyaFirstQueue"
    OUTPUT_QUEUE_NAME="AlekhyaSecondQueue"

    MESSAGE_ATTRIBUTES=['ImageName','UID']

    sqs = boto3.resource("sqs",region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    input_queue = sqs.get_queue_by_name(QueueName=INPUT_QUEUE_NAME)
    output_queue = sqs.get_queue_by_name(QueueName=OUTPUT_QUEUE_NAME)

    signal_handler = SignalHandler()
    while not signal_handler.received_signal:
        #send_queue_metrics(queue)
        #send_queue_metrics(dlq)
        #

        messages = input_queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=10, MessageAttributeNames=MESSAGE_ATTRIBUTES)
        for message in messages:
            try:
                result=process_message(message)
            except Exception as e:
                print(f"exception while processing message: {repr(e)}")
                continue

            try:
                send_message(result,output_queue)
            except Exception as e:
                print(f"exception while sending message: {repr(e)}")
                continue
            
            try:
                message.delete()
            except Exception as e:
                print(f"exception while deleting message: {repr(e)}")
                continue