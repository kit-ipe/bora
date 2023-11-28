const express = require('express');
const app = express();

const { proxy, scriptUrl } = require('rtsp-relay')(app);

const handler = proxy({
  url: `rtsp://localhost:8554/test`,
  // if your RTSP stream need credentials, include them in the URL as above
  verbose: false,
});

// the endpoint our RTSP uses
app.ws('/api/stream', handler);

// this is an example html page to view the stream
app.get('/', (req, res) =>
  res.send(`
<canvas id='canvas'></canvas>

  <script src='https://cdn.jsdelivr.net/npm/rtsp-relay@1.7.0/browser/index.js'></script>
  <script>
    window.addEventListener("load", (event) => {
        loadPlayer({
	        url: 'ws://localhost:2000/api/stream',
            canvas: document.getElementById('canvas'),
            audio: false
        });
    });
  </script>
`),
);

app.listen(2000);
