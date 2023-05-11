from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from array import array
import os
from PIL import Image
import sys
import time
import os
import openai

subscription_key = "c2fd498a7ecb4472a892bbdc6f1afe3e"
endpoint = "https://scan-gpt.cognitiveservices.azure.com/"

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

def ocr_txt(image_path):
    read_image_path = os.path.join (image_path)
    # Open image
    read_image = open(read_image_path, "rb")

    read_response = computervision_client.read_in_stream(read_image, raw=True)
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]


    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status.lower () not in ['notstarted', 'running']:
            break
        time.sleep(10)


    # string = ""
    test_dict = {}
    text_block = ""
    # f = open("text.txt",'w')
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                test_dict[line.text] = line.bounding_box
                text_block += line.text

    print(text_block)
    return text_block
    


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        inputText = request.form.get('inputText')
         openai.api_key = 'YOUR-KEY'
       if not inputText:
            upload_dir = 'uploads'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            file_path = os.path.join(upload_dir, file.filename)
            file.save(file_path)
            text = ocr_txt(file_path)
            completion=openai.Completion.create(engine="text-davinci-003",prompt=text,max_tokens=1000)
        else:
            text=inputText
            completion=openai.Completion.create(engine="text-davinci-003",prompt=text,max_tokens=1000)
        # completion=openai.Completion.create(engine="text-davinci-003",prompt=text,max_tokens=1000)
        


        # return render_template('output.html',PrintText=['PrintText'])       
        return render_template('output.html', text=completion.choices[0]['text'],PrintText=text)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
