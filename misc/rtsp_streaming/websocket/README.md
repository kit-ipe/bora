```sh
$ npm install -S rtsp-relay express
$ npm i @ffmpeg-installer/ffmpeg
$ podman image build -t rtsp_docker .
$ podman run --net=host -d rtsp_docker
```

