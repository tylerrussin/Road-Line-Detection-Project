from functions.Resize import resize
from functions.Canny import canny
from functions.Grey import grey
from functions.Blur import blur
from functions.Region import region
from functions.Hough_Lines import hough_lines
from functions.Average import average
from functions.Draw_Lines import draw_lines

from pages import process
from layout_structures.Navbar import navbar
from layout_structures.Footer import footer
from layout_structures.External_Stylesheets import external_stylesheets
from layout_structures.Meta_Tags import meta_tags

import configparser

import cv2
import pandas as pd
import numpy as np

import plotly.express as px

import boto3

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from flask import Flask, Response


# Acessing Credentials
config = configparser.ConfigParser()
config.read('../credentials/credentials.ini')
ACCESS_KEY_ID = config['Amazon S3 Bucket tyler9937']['ACCESS_KEY_ID']
SECRET_ACCESS_KEY = config['Amazon S3 Bucket tyler9937']['SECRET_ACCESS_KEY']

# Connecting to Amazon S3 Bucket
S3_CLIENT = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)
BUCKET_NAME = 'road-line-detection-scenes'      
TEMP_KEY = 'scene_1.mp4' 


# Creating Flask and Dash servers
server = Flask(__name__)
app = dash.Dash(__name__, server = server, external_stylesheets=external_stylesheets, meta_tags=meta_tags)
app.config.suppress_callback_exceptions = True # see https://dash.plot.ly/urls
app.title = 'Tanzanian Ministry of Water Data Analysis' # appears in browser title bar


def process_stream(mask_type, width, height):
    # Fetching URL stream from amazon s3 bucket
    url = S3_CLIENT.generate_presigned_url('get_object', 
                                           Params = {'Bucket': BUCKET_NAME, 'Key': TEMP_KEY}, 
                                           ExpiresIn = 30) #this url will be available for 600 seconds

    # Importing the video
    video = cv2.VideoCapture(url)

    # Checking if video opened
    if video.isOpened() == False:
        print('Error opening video file')

    while video.isOpened():

        ret, frame = video.read()

        if ret:
            try:
                # Resizing image
                resized = resize(frame, width, height)

                if mask_type == 'original':
                    frame = resized
                    
                    # Preparing for export
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                # Make copy
                frame_copy = np.copy(resized)
                
                # Greyscale
                greyed = grey(frame_copy)

                # Edge detection
                edges = canny(greyed)

                if mask_type == 'edge_detection':
                    frame = edges

                    # Preparing for export
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
       
                if mask_type == 'predict_lines':
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


@server.route('/video_stream_predict_lines')
def video_stream_predict_lines():
    return Response(process_stream('predict_lines', 800, 600), mimetype='multipart/x-mixed-replace; boundary=frame')

@server.route('/video_stream_edge_detection')
def video_stream_edge_detection():
    return Response(process_stream('edge_detection', 400, 300), mimetype='multipart/x-mixed-replace; boundary=frame')

@server.route('/video_stream_original')
def video_stream_original():
    return Response(process_stream('original', 400, 300), mimetype='multipart/x-mixed-replace; boundary=frame')

quantity_dropdown = html.Div(
    [
        
        dcc.Dropdown(
            id='quantity_dropdown',
            options=[
                {'label': 'dry', 'value': 0},
                {'label': 'enough', 'value': 1},
                {'label': 'insufficient', 'value': 2},
                {'label': 'seasonal', 'value': 3}
            ],
            value=1
        ),
    ]
)

column1 = dbc.Col(
    [
        dcc.Markdown(
            """
        
            ## Looking into Classification
            In this web application, we explore the key concepts of Data Wrangling and Classification. Scoring metrics such as Precision/Recall and ROC AUC scores are utilized. Pipeline building techniques associated with Data Preprocessing, Hyperparameter Tuning, and Cross-Validation are implemented.
            This application describes the competition that was entered, the process for  how modeling was done, and has an interactive model demo
            """
        ),

    ],
)

column2 = dbc.Col(
    [
       html.Div(html.Img(src="/video_stream_predict_lines")),
       html.Div(html.Img(src="/video_stream_edge_detection"),style={'float': 'left'}),
       html.Div(html.Img(src="/video_stream_original", style={'float': 'right'})),
    ]
)

layout = dbc.Row([column1, column2])

# Rendering the webpage
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    dbc.Container(id='page-content', className='mt-4'),
    footer               
])

# URL routing
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return layout
    elif pathname == '/process':
        return process.layout
    else:
        return dcc.Markdown('## Page not found')


if __name__ == '__main__':
    app.run_server(debug=True)