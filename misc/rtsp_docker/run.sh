#! /bin/bash

podman image build --runtime /usr/bin/crun  -t rtsp_docker .
podman stop $(podman ps | grep rtsp_docker | awk '{ print $1 }')
podman run  --runtime /usr/bin/crun --net=host -v ./src:/usr/src/app/src -d rtsp_docker
