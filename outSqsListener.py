import threading
import boto3
from signal import SIGINT, SIGTERM, signal
import json

globalMap = {}

class outSqsLitener(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    
    def run(self):
        AWS_REGION='us-east-1'
        AWS_ACCESS_KEY="AKIAQXBVY5HVCRFALTEM"
        AWS_SECRET_ACCESS_KEY="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"

        INPUT_QUEUE_NAME="InputQueue"
        OUTPUT_QUEUE_NAME="OutputQueue"

        MESSAGE_ATTRIBUTES=['ImageName','UID']

        sqs = boto3.resource("sqs",region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        input_queue = sqs.get_queue_by_name(QueueName=INPUT_QUEUE_NAME)
        output_queue = sqs.get_queue_by_name(QueueName=OUTPUT_QUEUE_NAME)

        while True:
            messages = output_queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=10, MessageAttributeNames=MESSAGE_ATTRIBUTES)
            for message in messages:
                try:
                    result=process_message(message)
                except Exception as e:
                    print(f"exception while processing message: {repr(e)}")
                    continue
            
                try:
                    message.delete()
                    print("Deleted message")
                except Exception as e:
                    print(f"exception while deleting message: {repr(e)}")
                    continue


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
    globalMap[uid] = label
    print(globalMap)

    # with open("globalMap.json", "r+") as file:
    #     data = json.load(file)
    #     data.update(result)
    #     file.seek(0)
    #     json.dump(data, file)


    return result

class SignalHandler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        print(f"handling signal {signal}, exiting gracefully")
        self.received_signal = True

# if __name__ == "__main__":

#     AWS_REGION='us-east-1'
#     AWS_ACCESS_KEY="AKIAQXBVY5HVCRFALTEM"
#     AWS_SECRET_ACCESS_KEY="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"

#     INPUT_QUEUE_NAME="InputQueue"
#     OUTPUT_QUEUE_NAME="OutputQueue"

#     MESSAGE_ATTRIBUTES=['ImageName','UID']

#     sqs = boto3.resource("sqs",region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
#     input_queue = sqs.get_queue_by_name(QueueName=INPUT_QUEUE_NAME)
#     output_queue = sqs.get_queue_by_name(QueueName=OUTPUT_QUEUE_NAME)

#     signal_handler = SignalHandler()
#     while not signal_handler.received_signal:

#         messages = output_queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=10, MessageAttributeNames=MESSAGE_ATTRIBUTES)
#         for message in messages:
#             try:
#                 result=process_message(message)
#             except Exception as e:
#                 print(f"exception while processing message: {repr(e)}")
#                 continue
            
#             try:
#                 message.delete()
#             except Exception as e:
#                 print(f"exception while deleting message: {repr(e)}")
#                 continue