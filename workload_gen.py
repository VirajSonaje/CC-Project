import sys
import requests
import os
import argparse
import time

parser = argparse.ArgumentParser(description='Upload images')
parser.add_argument('--num_request', type=int, help='one image per request')
# parser.add_argument('--url', type=str, help='URL of your backend server, e.g. http://3.86.108.221/xxxx.php')
# parser.add_argument('--image_folder', type=str, help='the path of the folder where images are saved on your local machine')
args = parser.parse_args()

def send_one_request(url, image_path):
    # Define http payload, "myfile" is the key of the http payload
    file = {"image_file": open(image_path,'rb')} 
    r = requests.post(url, files=file)
    # Print error message if failed
    if r.status_code != 200:
        print('sendErr: '+r.url)
    else :
        image_msg = image_path.split('/')[1] + ' uploaded!'
        msg = image_msg + '\n' + 'Classification result: ' + r.text
        print(msg)

num_request = args.num_request
# url = "http://54.166.3.222:5000/"
# url = 'http://127.0.0.1:5000/'
url = 'http://192.168.0.70:5000/'

image_folder = "face_images_100/"
# Iterate through all the images in your local folder
print("Start... ",time.time() * 1000)
start=time.time() * 1000
for i, name in enumerate(os.listdir(image_folder)):
    if i == num_request:
        break
    image_path = image_folder + name
    print(image_path)
    send_one_request(url, image_path)

print("End... ",time.time() * 1000)
end=time.time() * 1000
print(end-start)