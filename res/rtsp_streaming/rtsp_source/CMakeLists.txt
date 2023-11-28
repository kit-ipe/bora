cmake_minimum_required(VERSION 3.10)
project(rtsp)

set(CMAKE_C_STANDARD 99)

find_package(PkgConfig REQUIRED)
pkg_check_modules(GSTREAMER REQUIRED gstreamer-1.0>=1.4 gstreamer-base-1.0>=1.4 gstreamer-video-1.0>=1.4)
pkg_check_modules(GST_RTSP_SERVER REQUIRED gstreamer-rtsp-server-1.0)
pkg_check_modules(CAIRO REQUIRED cairo)

add_executable(rtsp rtsp.c)

target_include_directories(rtsp PUBLIC ${GSTREAMER_INCLUDE_DIRS} ${GST_RTSP_SERVER_INCLUDE_DIRS} ${CAIRO_INCLUDE_DIRS})
target_link_libraries(rtsp ${GSTREAMER_LIBRARIES} ${GST_RTSP_SERVER_LIBRARIES} ${CAIRO_LIBRARIES} m)
target_compile_options(rtsp PUBLIC ${GSTREAMER_CFLAGS_OTHER} ${GST_RTSP_SERVER_CFLAGS_OTHER} ${CAIRO_CFLAGS_OTHER})

