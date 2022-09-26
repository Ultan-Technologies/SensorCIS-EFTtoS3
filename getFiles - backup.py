# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 11:45:01 2022

@author: Shruti Agarwal
"""

import logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
#C:\EFT Logs
logging.basicConfig(filename=r'C:\inetpub\wwwroot\EFTtoS3\EFTToS3.log', filemode='a', format='%(asctime)s -%(levelname)s- %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
import boto3
from botocore.exceptions import ClientError
import os
from flask import Flask, request, make_response
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
#from flask.ext.jsonpify import jsonify
from datetime import datetime
import json


s3 = boto3.resource("s3")

app = Flask(__name__)

api = Api(app, default_mediatype='text/plain')

@api.representation('text/plain')
def output_html(data, code, headers=None):
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp


class SensorCISFiles(Resource):

    def get(self):
        logging.info("GET Request Received from: "+ request.environ['REMOTE_ADDR'])
        return 'SUCCESS Get request with no files so nothing saved'

    def post(self):
        logging.info("POST Request Received from: "+ request.environ['REMOTE_ADDR'])
        data=request.get_data()
        filesize= request.headers.get('Content-Length')
        if data != b'':
            logging.info("POST Request with file")
            filename="EFTLog/"+(datetime.now().strftime("%Y/%m/%d/ %H-%M-%S"))+'.'+"txt"
            bucketName="sensorcisfiles"
            try:
                logging.info("Sending file to S3")
                s3.Bucket(bucketName).put_object(Key = filename, Body = data)
                logging.info("File successfully sent to s3 with object path: "+filename+' with Size:'+filesize)
                return 'SUCCESS\r\n'+filesize
            except Exception as e:
                logging.error("Exception occurred ", exc_info=True)
                return 'FAILURE  Error saving file'
        else:
            logging.info("POST request with no data received")
            return 'FAILURE No file found' 
        
try:  
    api.add_resource(SensorCISFiles, '/sensorcisfiles')
except Exception as e:
    logging.error("Exception occurred ", exc_info=True)

if __name__ == '__main__':
    try:
        app.run()
    except Exception as e:
        logging.error("Exception occurred ", exc_info=True)
