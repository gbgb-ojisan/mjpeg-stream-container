FROM nginx:1.21.6 AS Base
RUN mkdir /data
WORKDIR /app
RUN apt update \
&& apt install -y python3 python3-pip libgl1-mesa-dev libglib2.0-0 libsm6 libxrender1 libxext6 \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*
COPY conf/nginx.conf /etc/nginx/conf.d/default.conf
COPY conf/requirements.txt /app
RUN pip3 install -r requirements.txt

FROM Base AS Build
COPY bin/* /app/
CMD ["sh", "spawn.sh"]