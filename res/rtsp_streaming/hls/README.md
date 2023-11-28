## Procedure

1. Produce RTSP source
```
./rtsp`
```

2. Transcode RTSP source to HLS 
```
ffmpeg -i "rtsp://127.0.0.1:8554/test" -hls_time 3 -hls_wrap 10 "stream/streaming.m3u8"
```
or
```
ffmpeg -rtsp_transport tcp -i "rtsp://127.0.0.1:8554/test" -c:v libx264 -crf 21 -preset ultrafast -maxrate 3M -bufsize 300k -r 10 -g 20 -movflags +faststart -tune zerolatency -sc_threshold 0 -hls_time 1 -hls_list_size 4 -hls_wrap 4 -start_number 1 -hls_allow_cache 0 -threads 1 -loglevel warning -y "stream/streaming.m3u8"
```


3. Start local server
```
python3 -m http.server
```

4. Open browser `http://localhost:8000`

