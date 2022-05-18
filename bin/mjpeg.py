#!/usr/bin/python3
from flask import Flask, jsonify, render_template, Response
from flask_cors import CORS, cross_origin
import os
import sys
import cv2
import time
import base64
from logging import getLogger, StreamHandler, Formatter, FileHandler, DEBUG, INFO

# Const
baseDir = '/data'
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
app = Flask(__name__)
cors = CORS(app)

def setup_logger(log_level='DEBUG', modname=__name__):
    logger = getLogger(modname)
    if log_level == 'DEBUG':
        logger.setLevel(DEBUG)
    elif log_level == 'INFO':
        logger.setLevel(INFO)
    else:
        raise Exception('Invalid logging level!')

    sh = StreamHandler()
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    return logger

logger = setup_logger()

def get_frame(filename):
    fullPath = os.path.join(baseDir, filename)
    isFirstLoop = True
    isEndFrame = False
    try:
        # Open video file and acquire framerate
        cap = cv2.VideoCapture(fullPath)
        if not cap.isOpened:
            logger.error('Error: Cannot open the specified video {}'.format(fullPath))
        framerate = cap.get(cv2.CAP_PROP_FPS)
        interval = 1 / framerate
        logger.info('Framerate: {}'.format(framerate))

        # Stream video frame infinitely.
        while True:
            start_time = time.perf_counter()
            ret, image = cap.read()
            if ret is False:
                if isFirstLoop:
                    logger.error('Error: Cannot read frame.')
                    break
                else:
                    # continue to play from first position
                    logger.debug('Replay.')
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, image = cap.read()
            isFirstLoop = False

            result, encimg = cv2.imencode(".jpg", image, encode_param)
            if result is False:
                logger.error('Error: Cannot encode frame!')

            frame = encimg.tobytes()
            wait_time = interval - (time.perf_counter() - start_time)
            if wait_time > 0:
                time.sleep(wait_time)
            yield (b'--jpgboundary\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()

@app.route("/", methods=['GET'])
@cross_origin()
def hello_world():
    return "Container works."

@app.route("/stream/mjpeg/<filename>", methods=['GET'])
@cross_origin()
def do_stream(filename):
    return Response(get_frame(filename), mimetype='multipart/x-mixed-replace; boundary=jpgboundary')

@app.route("/streams/", methods=['GET'])
@cross_origin()
def get_filenames():
    files = os.listdir(baseDir)
    return jsonify(files)

if __name__ == '__main__':
    app.run()