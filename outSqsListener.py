import boto3
from signal import SIGINT, SIGTERM, signal
import json

def process_message(message):
    #print(dir(message))
    """
    ['Queue', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_queue_url', '_receipt_handle', 'attributes', 'body', 'change_visibility', 'delete', 'get_available_subresources', 'md5_of_body', 'md5_of_message_attributes', 'message_attributes', 'message_id', 'meta', 'queue_url', 'receipt_handle']
    """

    print(f"message body: {message.body}")
    print("----")
    print(f"message id: {message.message_id}")
    
    image_name="default.jpg"
    uid="default"
    label=''.join(filter(str.isalnum, str(message.body)))

    if message.message_attributes is not None:
        image_name = message.message_attributes.get('ImageName').get('StringValue')
        uid = message.message_attributes.get('UID').get('StringValue')
        print("----")
        print("Image Name: ",image_name)
        print("----")
        print("UID: ",uid)

    print("--------------------------")

    #TO DO
    #Store result in global map
    result = {uid: label}

    with open("globalMap.json", "r+") as file:
        data = json.load(file)
        data.update(result)
        file.seek(0)
        json.dump(data, file)


    return result

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

        messages = output_queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=10, MessageAttributeNames=MESSAGE_ATTRIBUTES)
        for message in messages:
            try:
                result=process_message(message)
            except Exception as e:
                print(f"exception while processing message: {repr(e)}")
                continue
            
            try:
                message.delete()
            except Exception as e:
                print(f"exception while deleting message: {repr(e)}")
                continue