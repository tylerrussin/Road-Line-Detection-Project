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

def resize(image):
    # Resizing image
    dim = (800, 600)
    image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    return image

def canny(image):
    # Applying Canny edge detection (threshold values will have to be tweaked)
    image = cv2.Canny(image, threshold1=100, threshold2=130)
    return image

def grey(image):
    # Processing to Grayscale (simpiler data)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def blur(image):
    # Adding Gaussian Blur (much more effective when applied after edge detection)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    return image

def region(image):
    vertices = np.array([[1,500], [350,350], [450,350], [800,500]])

    mask = np.zeros_like(image)
    mask = cv2.fillPoly(mask, [vertices], 255)
    mask = cv2.bitwise_and(image, mask)
    
    return mask

def hough_lines(image):
    # Find all lines
    lines = cv2.HoughLinesP(image, 1, np.pi/180, 180, np.array([]), 100, 5)
    return lines

def make_points(image, average):
    slope, y_int = average
    y1 = image.shape[0]
    y2 = int(y1 * (3/5))
    x1 = int((y1 - y_int) // slope)
    x2 = int((y2 - y_int) // slope)
    return np.array([x1, y1, x2, y2])

def average(image, lines):
    # Find average left and right lines
    left = []
    right = []
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        slope = parameters[0]
        y_int = parameters[1]
        # (all images in OpenCV have inversed y-axes)
        if slope < 0:
            left.append((slope, y_int))
        else:
            right.append((slope, y_int))

    # Calculate average points
    right_avg = np.average(right, axis=0)
    left_avg = np.average(left, axis=0)
    left_line = make_points(image, left_avg)
    right_line = make_points(image, right_avg)

    return np.array([left_line, right_line])

def draw_lines(image, lines):
    lines_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line
            cv2.line(lines_image, (x1, y1), (x2, y2), [255,0,0], 10)
    return lines_image

def gen_frames():
    # Importing the video
    video = cv2.VideoCapture('data/1.MOV')

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
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
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

app.layout = html.Div([
   html.H1("Webcam Test"),
   html.Img(src="/video_feed")
])

if __name__ == '__main__':
    app.run_server(debug=True)


