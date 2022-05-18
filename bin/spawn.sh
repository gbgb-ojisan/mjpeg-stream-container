#!/bin/sh
uwsgi --ini /app/mjpeg.ini &
nginx -g "daemon off;"