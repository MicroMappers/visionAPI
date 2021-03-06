#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuki Furuta <furushchev@jsk.imi.i.u-tokyo.ac.jp>

import os
from argparse import ArgumentParser
import base64
import httplib2
#import cv2
import json
import pprint

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

API_DISCOVERY_FILE=os.path.join(os.getcwd(), 'vision_discovery_v1alpha1.json')

class GoogleCloudVisionClient(object):
    def __init__(self, api_key, image_path):
        with open(API_DISCOVERY_FILE, 'r') as f:
            doc = f.read()
        self.service = discovery.build_from_document(doc,
                                                     developerKey=api_key,
                                                     http=httplib2.Http())
        self.types = ["FACE_DETECTION",
                      "LABEL_DETECTION",
                      "LANDMARK_DETECTION",
                      "LOGO_DETECTION",
                      "TEXT_DETECTION"]
        print("use image %s" % image_path)
        self.image = image_path#cv2.imread(image_path)

    def sendRequest(self, img_bin, max_results=10):
        req = self.service.images().annotate(
            body={
                'requests': [{
                    'image': {'content': img_bin},
                    'features': [{'type': t, 'maxResults': max_results} for t in self.types]
                }]
            })
        res = req.execute()
        return res["responses"][0]

    def resize(self, src):
        h,w,_ = src.shape
        if h > w:
            ref = (480, 640)
        else:
            ref = (640, 480)
        if float(w) / ref[0] > float(h) / ref[1]:
            factor = ref[0] / float(w)
        else:
            factor = ref[1] / float(h)
        resized = cv2.resize(src, (int(h * factor), int(w * factor)))
        print("resized to", resized.shape)
        return resized

    def run(self):
        result = self.onImage(self.image)
        self.onDetection(result)
        if "error" in result:
            return False
        #else:
        #    print(True)

    def encodeImage(self, img):
        #_, jpg = cv2.imencode('.jpg', img)
        file = open(img, "rb")
        return base64.b64encode(file.read()).decode('utf-8')
        #return base64.b64encode(jpg)

    def onImage(self, img):
        #resized = self.resize(img)
        result = self.sendRequest(self.encodeImage(img))
        return result

    def onDetection(self, result):
        pprint.pprint(result)
        #try:
        #    print(result["textAnnotations"][0]["description"])
        #except:
        #    pass

if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument("-k", dest="api_key", required=True)
    p.add_argument("-i", dest="image_path", default=None, required=True,
                   help="path to image")

    a = p.parse_args()
    if a.image_path is None:
        p.error("image_path is necessary")
        p.print_help()
        exit(1)

    c = GoogleCloudVisionClient(a.api_key,
                                a.image_path)
    if c.run():
        exit(0)
    else:
        exit(1)

