from flask import Flask, render_template, make_response, request, flash, redirect, url_for
import os
import pydicom as dicom
import cv2
import numpy as np
import urllib
from keras.models import load_model
from google.cloud import storage
import random
import io
import certifi
import ssl

#initialize Flask app
app = Flask(__name__)

#default app route
@app.route('/')
def index():
    index_template = render_template('index.html')
    response = make_response(index_template)
    response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
    return response


#upload route to upload selected file and display it
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    #receeive uploaded file
    uploaded_file = request.files['file']

    #convert dicom file to png and store it
    dicom_img = dicom.dcmread(uploaded_file)
    global pixel_array
    pixel_array = dicom_img.pixel_array
    img = cv2.imencode('.png', pixel_array*128)[1]
    tmpFile = io.BytesIO(img)

    blob_id = random.randint(10000, 99999)

    storage_client = storage.Client.from_service_account_json('jss-bcd-ba9db8704878.json')
    bucket = storage_client.get_bucket('bcd-scans')
    blob = bucket.blob(f"{str(blob_id)}.png")
    blob.content_type = "image/png"
    blob.upload_from_file(tmpFile)

    img_url = blob.public_url

    #render the HTML file
    index_template = render_template('display_uploads.html', url=img_url)
    response = make_response(index_template)
    response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'

    return response


#predict route to generate prediction and display it
@app.route('/predict', methods=['POST', 'GET'])
def predict():
    img_url = request.args.get('img_url')

    resp = urllib.request.urlopen(img_url, context=ssl.create_default_context(cafile=certifi.where()))
    image = np.asarray(bytearray(resp.read()), dtype='uint8')
    png_img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    resized = cv2.resize(png_img, (512, 512), interpolation=cv2.INTER_AREA)
    rightsize = resized.reshape(-1, 512, 512, 3)

    #generate prediction from model
    model = load_model('static/model.h5')
    prediction = model.predict(rightsize)

    #render the HTML file
    index_template = render_template('prediction.html', data=prediction, url=img_url)
    response = make_response(index_template)
    response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600' 

    return response


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))