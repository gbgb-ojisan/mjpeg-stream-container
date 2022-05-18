#!/bin/bash
docker run -dit --name mjpeg-container -p 60000:80 \
-v "$PWD/data":/data/ \
mjpeg