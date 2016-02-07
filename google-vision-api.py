import argparse
import json
import base64
import os
import urllib.request
from urllib.error import HTTPError
from time import sleep


def find_all_images(files_path):
    images = []
    for root, dirs, files in os.walk(files_path):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG"):
                file_path = os.path.join(root, file)#.replace(files_path, "")
                images.append(file_path)
    return images


def generate_vision_api_json(filename):
    requests_json_object = {}
    request_array = []
    file = open(filename, "rb")
    image_json_object = {'features': [{"type": "TEXT_DETECTION", "maxResults": 10},
                                      {"type": "LABEL_DETECTION", "maxResults": 10},
                                      {"type": "FACE_DETECTION", "maxResults": 10},
                                      {"type": "LANDMARK_DETECTION", "maxResults": 10},
                                      {"type": "LOGO_DETECTION", "maxResults": 10},
                                      {"type": "LABEL_DETECTION", "maxResults": 10},
                                      {"type": "SAFE_SEARCH_DETECTION", "maxResults": 10}],
                         'image': {'content': base64.b64encode(file.read()).decode('utf-8')}}
    file.close()
    request_array.append(image_json_object)
    requests_json_object['requests'] = request_array
    return requests_json_object


def process_google_vision_api(file_request_json,key):
    json_data = json.dumps(file_request_json).encode('utf-8')
    req = urllib.request.Request(
        url='https://vision.googleapis.com/v1/images:annotate?key='+key)
    req.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(req, json_data)
    return json.loads(response.read().decode("utf-8"))['responses'][0]


if __name__ == "__main__":
    parser = argparse. ArgumentParser ()
    parser.add_argument('-k', dest='api_key', required=True)
    parser.add_argument('-i', dest='data_path', help='path to images')
    parser.add_argument('-o', dest='output', help='output file path')
    args = parser.parse_args()
    data_path = args.data_path #os.path.join(os.path.dirname(os.path.realpath(__file__)), "datatest//")
    output = args.output
    key = args.api_key
    print(data_path)
    images_to_process = find_all_images(data_path)
    if os.path.isfile(output):
        html_table = ''
    else:
        html_table = '<html><body><table border="1"><td><b>Image</b></td><td><b>Text search</b></td>' \
                 '<td><b>Label detection</b></td><td><b>Face detection</b></td><td><b>Landmark detection</b></td><td><b>Logo detection</b></td><td><b>Safe search</b></td>'
    for i, image_path in enumerate(images_to_process):
        request_json = generate_vision_api_json(os.path.join(data_path, image_path))
        answer_json = {}
        safeText = ''
        ocrText = ''
        labelText = ''
        faceText = ''
        logoText = ''
        landmarkText = ''
        while True:
            try:
                print('Sending image number {}, url "{}"'.format(i, image_path))
                answer_json = process_google_vision_api(request_json,key)
                #print(answer_json)
                break
            except HTTPError as err:
                safeText = 'Error processing Google Vision API request: ' + err.reason
                print(safeText)
                print('Retrying in 1 second...')
                sleep(1)
        if 'textAnnotations' in answer_json:
            ocrText = json.dumps(answer_json['textAnnotations']).encode('utf-8')
            #print('Text search:', answer_json['textAnnotations'])
        if 'labelAnnotations' in answer_json:
            labelText = json.dumps(answer_json['labelAnnotations']).encode('utf-8')
            #print('Label search:', answer_json['labelAnnotations'])
        if 'faceAnnotations' in answer_json:
            faceText = json.dumps(answer_json['faceAnnotations']).encode('utf-8')
            #print('Face search:', answer_json['faceAnnotations'])
        if 'logoAnnotations' in answer_json:
            logoText = json.dumps(answer_json['logoAnnotations']).encode('utf-8')
            #print('Logo search:', answer_json['logoAnnotations'])
        if 'landmarkAnnotations' in answer_json:
            landmarkText = json.dumps(answer_json['landmarkAnnotations']).encode('utf-8')
            #print('Landmark search:', answer_json['landmarkAnnotations'])
        if 'safeSearchAnnotation' in answer_json:
            safeText = 'Adult: {}<br>Violence: {}<br>' \
                       'Medical: {}<br>Spoof: {}<br>'.format(answer_json['safeSearchAnnotation']['adult'],
                                                             answer_json['safeSearchAnnotation']['violence'],
                                                             answer_json['safeSearchAnnotation']['medical'],
                                                             answer_json['safeSearchAnnotation']['spoof'])
            #print('Safe search:', answer_json['safeSearchAnnotation'])

        html_table += '<tr><td><a href="{}"><img src="file:///{}" width="300px" /></a>' \
                      '</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(os.path.join(data_path, image_path),
                                                                           os.path.join(data_path, image_path),
                                                                           ocrText,labelText,faceText,
                                                                           landmarkText,logoText,safeText)
        #final_html = html_table# + '</table></body></html>'
    html_file = open(output, "a+")
    html_file.write(html_table)
    html_file.close()
