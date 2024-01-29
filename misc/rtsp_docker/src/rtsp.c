#include <stdio.h>

#include <glib.h>
#include <gst/gst.h>
#include <gst/rtsp-server/rtsp-server.h>
#include <gst/video/video-info.h>
#include <gst/video/video.h>
#include <cairo.h>
#include <math.h>

#define IPV4_ADDRESS "0.0.0.0"
#define RTSP_PORT "5617"
#define RTSP_UDP_PORT_MIN 5000
#define RTSP_UDP_PORT_MAX 5010
#define RTSP_TRANSPORTS (GST_RTSP_LOWER_TRANS_TCP | GST_RTSP_LOWER_TRANS_UDP)
//#define RTSP_TRANSPORTS (GST_RTSP_LOWER_TRANS_UDP)

GHashTable *clients;
int connected = 0;
int keyframe = 0;

static void
draw_bubble(cairo_t *cr, double x, double y, double radius)
{
  cairo_arc(cr, x, y, radius, 0, 2 * M_PI);
//  printf("%lf %lf %lf\h", x, y, radius);
  cairo_set_source_rgba(cr, 0, 0, 0, 1);
  cairo_fill(cr);
}

static void
draw_bubbles(cairo_t *cr, guint64 elapsed_time)
{
  guint num_bubbles = 1;
  double speed = 0.001;

  for (guint i = 0; i < num_bubbles; i++) {
    double x = 320 + 200 * sin(speed * (i + 1) * elapsed_time);
    double y = 240 + 200 * cos(speed * (i + 1) * elapsed_time);
    double radius = 20 + 10 * sin(speed * (i + 1) * elapsed_time);
    draw_bubble(cr, x, y, radius);
  }
  cairo_move_to(cr, 100, 100);
  cairo_show_text(cr, "LOL"); 
}

size_t timestamp = 0;

GMutex mutex;

static void
start_feed(GstElement *appsrc, guint user_size, gpointer user_data)
//static gboolean
//push_frame(GstElement *appsrc, guint64 elapsed_time)
{
  GstFlowReturn ret;
  GstBuffer *buffer;
  guint width = 640;
  guint height = 480;
  gint size = width * height;
//  GstVideoInfo vinfo;

//  g_print("feed %p %p\n", appsrc, user_data);
  g_mutex_lock(&mutex);

  buffer = gst_buffer_new_allocate(NULL, size, NULL);
  gst_buffer_memset (buffer, 0, 0x0, size);

//  GST_BUFFER_TIMESTAMP(buffer) = elapsed_time * GST_MSECOND;
//  GST_BUFFER_PTS (buffer) = elapsed_time * GST_MSECOND;
//  GST_BUFFER_DURATION (buffer) = gst_util_uint64_scale_int (30, GST_MSECOND, 1);
  GST_BUFFER_PTS (buffer) = timestamp;
  GST_BUFFER_DURATION (buffer) = gst_util_uint64_scale_int (1, GST_SECOND, 10);
  timestamp += GST_BUFFER_DURATION (buffer);

//  printf("%lu %lu %lu\n", timestamp, gst_util_uint64_scale_int (30, GST_MSECOND, 1), GST_MSECOND);
//  gst_video_info_set_format(&vinfo, GST_VIDEO_FORMAT_GRAY8, width, height);


  GstMapInfo map;
  gst_buffer_map(buffer, &map, GST_MAP_WRITE);
  cairo_surface_t *surface = cairo_image_surface_create_for_data(map.data, CAIRO_FORMAT_A8, width, height, width);
  cairo_t *cr = cairo_create(surface);

  if (cr) {
//    cairo_set_operator(cr, CAIRO_OPERATOR_OVER);
//    cairo_set_source_rgba(cr, 0, 0, 0, 0);
//    cairo_paint(cr);

    draw_bubbles(cr, timestamp/10000000);//elapsed_time);
    cairo_surface_flush(surface); 
    cairo_destroy(cr);
  }

  cairo_surface_destroy(surface);
  gst_buffer_unmap(buffer, &map);

	// try force key-frame
  if (keyframe) {
    static guint count = 0;
    GstPad *srcpad = gst_element_get_static_pad ((GstElement *)appsrc, "src");
    if (srcpad != NULL) {
        g_print("forcing key-frame (timestamp: %.3lf)\n", 1.f* timestamp / GST_SECOND);
        GstEvent *event = gst_video_event_new_downstream_force_key_unit (timestamp, timestamp, timestamp, TRUE, count++);
        gst_pad_push_event (srcpad, event);
        gst_object_unref (srcpad);
	keyframe = 0;
    }
  }

  g_print("a new buffer delivered (timestamp: %.3lf, clients: %u)\n", 1.f* timestamp / GST_SECOND, g_hash_table_size(clients));
  g_signal_emit_by_name(appsrc, "push-buffer", buffer, &ret);
  gst_buffer_unref(buffer);

  g_mutex_unlock(&mutex);


//  return (ret == GST_FLOW_OK);
}

/* this timeout is periodically run to clean up the expired sessions from the
 * pool. This needs to be run explicitly currently but might be done
 * automatically as part of the mainloop. */
static gboolean
timeout (GstRTSPServer * server)
{
  GstRTSPSessionPool *pool;

  pool = gst_rtsp_server_get_session_pool (server);
  gst_rtsp_session_pool_cleanup (pool);
  g_object_unref (pool);

  return TRUE;
}

static void media_configure (GstRTSPMediaFactory * factory, GstRTSPMedia * media, gpointer user_data)
//static gboolean media_configure(GstRTSPSessionPool *pool, GstRTSPSession *session, GstRTSPMedia *media, GstRTSPMediaPrivate *configure)
{
  GstElement *element, *appsrc;
//  MyContext *ctx;


  static int configured = 0;
/*
  if (configured) {
    puts("media-config skipping");
    return;
  }
*/

//  const gchar *clientIP = gst_rtsp_session_get_client_ip(session);
//  gint clientID = gst_rtsp_session_get_session_id(session);
//  g_print("media-config --- Client IP: %s, Session ID: %d\n", clientIP, clientID);
  g_print("media-configure\n");
//  gst_rtsp_media_prepare (media, NULL);

/*
  GstRTSPStream *stream = gst_rtsp_media_get_stream (media, 0); // this reflects number after pay0, also we can use gst_rtsp_media_n_streams
  GstRTSPAddressPool *pool = gst_rtsp_address_pool_new ();    
  gst_rtsp_address_pool_add_range(pool, "0.0.0.0", "0.0.0.0", 5000, 5050, 0);
*/


    // Something breaks here if we set reusable to TRUE (probably some server bug). FALSE seems to work with multiple clients.
//  gst_rtsp_media_set_reusable (media, TRUE);
  gst_rtsp_media_set_reusable (media, FALSE);

  /* get the element used for providing the streams of the media */
  element = gst_rtsp_media_get_element (media);

  /* get our appsrc, we named it 'mysrc' with the name property */
  appsrc = gst_bin_get_by_name_recurse_up (GST_BIN (element), "mysrc");

  /* this instructs appsrc that we will be dealing with timed buffer */
  gst_util_set_object_arg (G_OBJECT (appsrc), "format", "time");


  GstCaps *caps = gst_caps_new_simple(
      "video/x-raw",
      "format", G_TYPE_STRING, "GRAY8",
      "width", G_TYPE_INT, 640,
      "height", G_TYPE_INT, 480,
      "framerate", GST_TYPE_FRACTION, 10, 1,
      NULL);
  g_object_set(G_OBJECT(appsrc), "caps", caps, NULL);

  //GstRTSPStream *stream = gst_rtsp_media_get_stream(media, 0);/* 0 corresponds to pay0 */



/*
  ctx = g_new0 (MyContext, 1);
  ctx->white = FALSE;
  ctx->timestamp = 0;
    // make sure ther datais freed when the media is gone
  g_object_set_data_full (G_OBJECT (media), "my-extra-data", ctx,
      (GDestroyNotify) g_free);
*/

    // install the callback that will be called when a buffer is needed
    // we need to reset timestamp here
  timestamp = 0;
  g_signal_connect (appsrc, "need-data", (GCallback) start_feed, NULL); //ctx);
  gst_object_unref (appsrc);
  gst_object_unref (element);

  configured = 1;
}


/* callback function for the client-disconnected signal */
static void client_disconnected(GstRTSPClient *client, gchar *client_id) {
	// We need ref-counting here
    g_mutex_lock(&mutex);
    g_hash_table_remove(clients, client_id);
    g_mutex_unlock(&mutex);

    g_print("Disconnect: %s (remaining: %u) \n", client_id, g_hash_table_size(clients));

    g_free(client_id);

    if (g_hash_table_size(clients) == 0) {
	connected = 0;
//	timestamp = 0;
    }
    
}

static void client_connected(GstRTSPServer* server, GstRTSPClient *client, gpointer user_data) {
    gchar *client_id = g_strdup_printf("%p", client);

    g_mutex_lock(&mutex);
    g_hash_table_insert(clients, client_id, client);
    g_mutex_unlock(&mutex);

    g_print("Connect: %s (total: %u) \n", client_id, g_hash_table_size(clients));

    connected = 1;
    keyframe = 1;

    g_signal_connect(client, "closed", G_CALLBACK(client_disconnected), client_id);
}



int main(int argc, char *argv[]) {
  GError *error = NULL;
  GMainLoop *loop;
  GstRTSPServer *server;
  GstRTSPMountPoints *mounts;
  GstRTSPMediaFactory *factory;

  clients = g_hash_table_new(NULL, NULL);

  gst_init(&argc, &argv);

  loop = g_main_loop_new(NULL, FALSE);



  server = gst_rtsp_server_new();
  gst_rtsp_server_set_address(server, IPV4_ADDRESS);
  gst_rtsp_server_set_service(server, RTSP_PORT);

  factory = gst_rtsp_media_factory_new();

  /* store up to 0.4 seconds of retransmission data */
  //gst_rtsp_media_factory_set_retransmission_time (factory, 400 * GST_MSECOND);
  //gst_rtsp_media_set_buffer_size (media, size);
  gst_rtsp_media_factory_set_shared (factory, TRUE);
  gst_rtsp_media_factory_set_eos_shutdown(factory, TRUE);

    // Not sure following 2 lines are needed
//  gst_rtsp_media_factory_set_suspend_mode(factory, GST_RTSP_SUSPEND_MODE_PAUSE);
//  gst_rtsp_media_factory_set_stop_on_disconnect(factory, TRUE);

  // make a new address pool
  GstRTSPAddressPool *pool = gst_rtsp_address_pool_new ();
  gst_rtsp_address_pool_add_range (pool,
      IPV4_ADDRESS, IPV4_ADDRESS, RTSP_UDP_PORT_MIN, RTSP_UDP_PORT_MAX, 0);
//  gst_rtsp_address_pool_add_range (pool,
//      "224.3.0.0", "224.3.0.10", 5000, 5010, 16);
  gst_rtsp_media_factory_set_address_pool (factory, pool);
  g_object_unref (pool);

  gst_rtsp_media_factory_set_profiles(factory, GST_RTSP_PROFILE_AVP);
  gst_rtsp_media_factory_set_protocols (factory, RTSP_TRANSPORTS);
  gst_rtsp_media_factory_set_transport_mode (factory, GST_RTSP_TRANSPORT_MODE_PLAY);

  //gst_rtsp_media_factory_set_protocols (factory, GST_RTSP_LOWER_TRANS_UDP | GST_RTSP_LOWER_TRANS_UDP_MCAST | GST_RTSP_LOWER_TRANS_TCP | GST_RTSP_LOWER_TRANS_HTTP | GST_RTSP_LOWER_TRANS_TLS  );
  //gst_rtsp_media_factory_set_transport_mode

  /// only allow multicast
//  gst_rtsp_media_factory_set_protocols (factory,
//      GST_RTSP_LOWER_TRANS_UDP_MCAST);
//      GST_RTSP_LOWER_TRANS_UDP);
//      GST_RTSP_LOWER_TRANS_TCP | GST_RTSP_LOWER_TRANS_UDP);


/*
  gst_rtsp_media_factory_set_launch(
      factory,
      "( "
      "videotestsrc ! video/x-raw,width=640,height=480,framerate=30/1 ! "
      "x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay name=pay0 pt=96 "
      ")");
*/

    // vp8 - works, vp9enc seems to work in mplayer (VP9 on RTP is not supported by VLC as it seams)
    // WebRTC? https://docs.dolby.io/streaming-apis/docs/using-whip-with-gstreamer

  gst_rtsp_media_factory_set_launch(
      factory,
//      "( appsrc name=mysrc ! videoconvert ! video/x-raw,format=YV12 ! videoconvert ! x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay name=pay0 pt=96 )"); 	// This converts it to format supported by x264enc without complaining in mplayer/vlc, still problems.
//      "( appsrc name=mysrc ! videoconvert ! vp8enc sped=6 ! rtpvp8pay name=pay0 )"); 
//      "( appsrc name=mysrc ! videoconvert ! vp8enc speed=6 keyframe-max-dist=500 name=vp8enc ! rtpvp8pay name=pay0 )"); 
      "( appsrc name=mysrc ! videoconvert ! vp8enc speed=6 keyframe-max-dist=500 name=vp8enc ! rtpvp8pay name=pay0 )"); 
//       "( appsrc name=mysrc ! videoconvert ! vp9enc speed=6 keyframe-max-dist=500 name=vp9enc ! rtpvp9pay name=pay0 )"); 
//      "( appsrc name=mysrc ! videoconvert ! x264enc speed-preset=ultrafast tune=zerolatency ! video/x-h264,stream-format=byte-stream ! rtph264pay name=pay0 pt=96 )");

//      "( appsrc name=mysrc ! video/x-raw,format=GRAY8,width=640,height=480,framerate=0.1 ! videoconvert ! vp8enc speed=6 ! rtpvp8pay name=pay0 )"); 	// Doesn't work
//      "( appsrc name=mysrc ! videoconvert ! vp9enc speed=6 ! rtpvp9pay name=pay0 )"); 
//      "( appsrc name=mysrc ! videoconvert ! x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay name=pay0 pt=96 )");
//      "( appsrc name=mysrc ! videoconvert ! x264enc speed-preset=ultrafast tune=zerolatency ! video/x-h264,stream-format=byte-stream ! rtph264pay name=pay0 pt=96 )");
//      "( appsrc name=mysrc ! videoconvert ! jpegenc ! queue ! rtpjpegpay name=pay0 pt=96 )");
//      "( appsrc name=mysrc ! videoconvert ! x264enc speed-preset=ultrafast tune=zerolatency ! video/x-h264,stream-format=byte-stream ! rtph264pay name=pay0 pt=96 )");
//      "( appsrc name=mysrc ! videoconvert ! avenc_h264 pix_fmt=gray tune=zerolatency  ! rtph264pay name=pay0 pt=96 )");
//      "( appsrc name=mysrc ! videoconvert ! avenc_h264_omx ! video/x-h264,stream-format=byte-stream ! rtph264pay name=pay0 pt=96 )");


/*
      "( "
      "appsrc name=mysrc is-live=true format=time ! videoconvert ! "
      "x264enc speed-preset=ultrafast tune=zerolatency ! rtph264pay name=pay0 pt=96 "
      ")");
*/


/*
  GstElement *pipeline = gst_parse_launch(gst_rtsp_media_factory_get_launch(factory), NULL);
  GstElement *appsrc = gst_bin_get_by_name(GST_BIN(pipeline), "mysrc");

  GstCaps *caps = gst_caps_new_simple(
      "video/x-raw",
      "format", G_TYPE_STRING, "GRAY8",
      "width", G_TYPE_INT, 640,
      "height", G_TYPE_INT, 480,
      "framerate", GST_TYPE_FRACTION, 10, 1,
      NULL);
  g_object_set(G_OBJECT(appsrc), "caps", caps, NULL);
  gst_caps_unref(caps);
*/

//  GstRTSPSessionPool *pool = gst_rtsp_server_get_session_pool(server);
//  g_signal_connect (pool, "media-configure", (GCallback) media_configure, NULL);
  g_signal_connect (factory, "media-configure", (GCallback) media_configure, NULL);


// g_object_set(G_OBJECT(appsrc), "is-live", TRUE, NULL);
//  g_signal_connect(appsrc, "need-data", G_CALLBACK(start_feed), NULL);
//  g_signal_connect (appsrc, "need-data", (GCallback) start_feed, NULL); //ctx);
//  gst_object_unref(appsrc);


// gst_element_set_state(pipeline, GST_STATE_PLAYING);
/*
  GstState state;
  gst_element_get_state(pipeline, &state, NULL, GST_CLOCK_TIME_NONE);
  if (state != GST_STATE_PLAYING) {
    g_printerr("Unable to set pipeline to playing state.\n");
    return -1;
  }
*/

  mounts = gst_rtsp_server_get_mount_points(server);
  gst_rtsp_mount_points_add_factory(mounts, "/test", factory);
  g_object_unref(mounts);

  gst_rtsp_server_attach(server, NULL);

  g_signal_connect(server, "client-connected", G_CALLBACK(client_connected), NULL);
  //g_signal_connect (app->videosrc, "need-data", G_CALLBACK (start_feed), app);
  //g_signal_connect (app->videosrc, "enough-data", G_CALLBACK (stop_feed),app);


  g_print("RTSP server is running at rtsp://127.0.0.1:%s/test\n", RTSP_PORT);
  g_main_loop_run(loop);

  g_hash_table_unref(clients);
  
    return 0;
}
