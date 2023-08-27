const express = require('express');

const app = express();

const { proxy, scriptUrl } = require('rtsp-relay')(app);

//** BORA START **//
//** BORA END **//

app.listen(2000);
