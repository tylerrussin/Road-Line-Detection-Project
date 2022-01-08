from functions.Resize import resize
from functions.Canny import canny
from functions.Grey import grey
from functions.Blur import blur
from functions.Region import region
from functions.Hough_Lines import hough_lines
from functions.Average import average
from functions.Draw_Lines import draw_lines

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

from flask import Flask, Response

import cv2
import plotly.express as px
import pandas as pd
import numpy as np

server = Flask(__name__)
app = dash.Dash(__name__, server = server)


def gen_frames():
    # Importing the video
    video = cv2.VideoCapture('../data/scene_1.mp4')

    # Checking if video opened
    if video.isOpened() == False:
        print('Error opening video file')

    while video.isOpened():

        ret, frame = video.read()

        if ret:
            try:
                # Resizing image
                resized = resize(frame)

                # Make copy
                frame_copy = np.copy(resized)
                
                # Greyscale
                greyed = grey(frame_copy)

                # Edge detection
                edges = canny(greyed)

                # Gaussian blur
                blured = blur(edges)

                # Regionize
                isolated = region(blured)

                # Apply HoughLines
                lines = hough_lines(isolated)

                # Averages of lines
                averaged_lines = average(frame_copy, lines)

                # Display lines
                dark_lines = draw_lines(frame_copy, averaged_lines)
                lanes = cv2.addWeighted(frame_copy, 0.8, dark_lines, 1, 1)
       
                # me not understanding how things work :)
                frame = lanes

                # Preparing for export
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
            
        else:
            pass


@server.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @server.route('/video_feed2')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

app.layout = html.Div([
   html.H1("Webcam Test"),
   html.Img(src="/video_feed"),
#    html.Img(src="/video_feed2")
])

if __name__ == '__main__':
    app.run_server(debug=True)


