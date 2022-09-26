# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 11:45:01 2022

@author: Shruti Agarwal
"""

import logging
import boto3
from flask import Flask, request, make_response
from flask_restful import Resource, Api
from datetime import datetime

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(filename=r'C:\inetpub\wwwroot\EFTtoS3\EFTToS3.log', filemode='a',
                    format='%(asctime)s -%(levelname)s- %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO)


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
        logging.info("GET Request Received from: " + request.environ['REMOTE_ADDR'])
        return 'SUCCESS Get request with no files so nothing saved'

    def post(self):
        logging.info("POST Request Received from: " + request.environ['REMOTE_ADDR'])
        data = request.get_data()
        # filesize= request.headers.get('Content-Length')
        if data != b'':
            logging.info("POST Request with file")
            # Get Modbus and serial number from the data for response
            body_str = str(data, 'ISO-8859–1')
            find_data = body_str.partition('text/plain\r\n\r\n')[2].partition("\r\n----")[0]
            filesize = str(len(find_data))
            find_serial_number = body_str.partition('name="SERIALNUMBER"\r\n\r\n')[2].partition("\r\n--")[0]
            find_mod_bus_device = body_str.partition('name="MODBUSDEVICE"\r\n\r\n')[2].partition("\r\n--")[0]
            # print(find_serial_number, find_mod_bus_device)
            find_mode = body_str.partition('name="MODE"\r\n\r\n')[2].partition("\r\n--")[0]
            print(find_mode)
            if find_mode == 'CONFIGFILEMANIFEST':
                filename = "EFTLog/"+(datetime.now().strftime("%Y/%m/%d/"))+find_serial_number+'/' +\
                           (datetime.now().strftime("%H-%M-%S"))+'.'+"txt"
            else:
                filename = "EFTLog/"+(datetime.now().strftime("%Y/%m/%d/"))+find_serial_number+'/data_' +\
                           (datetime.now().strftime("%H-%M-%S"))+'.'+"txt"
            bucket_name = "sensorcisfiles"
            try:
                logging.info("Sending file to S3")
                s3.Bucket(bucket_name).put_object(Key=filename, Body=data)
                logging.info("File successfully sent to s3 with object path: "+filename+' with Size:'+filesize)
                ok_post_response = f"SERIALNUMBER={find_serial_number}\r\nMODBUSDEVICE={find_mod_bus_device}\r\n" \
                                   f"LOGFILE.Length={filesize}\r\nSUCCESS\r\n"

                response = make_response(ok_post_response, 200)
                response.mimetype = "text/plain"
                # logging.info("Response Sent:\n"+ response)
                return response
                # return ok_post_response
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
