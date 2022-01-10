# Image Processing functions
from functions.Resize import resize
from functions.Canny import canny
from functions.Grey import grey
from functions.Blur import blur
from functions.Region import region
from functions.Hough_Lines import hough_lines
from functions.Average import average
from functions.Draw_Lines import draw_lines

# Web app structures
from layout_structures.Navbar import navbar
from layout_structures.Footer import footer
from layout_structures.External_Stylesheets import external_stylesheets
from layout_structures.Meta_Tags import meta_tags

# Database connection functions
from database_functions.Connect import connect

# Addtional web pages for app
from pages import process

# For parsing credentials
import configparser

# Accessing s3 bucket
import boto3

# Standard imports
import os
import cv2
import numpy as np

# Dash app
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Backend flask import for video stream
from flask import Flask, Response

# For Use when working locally

# Acessing Credentials
# config = configparser.ConfigParser()
# config.read('credentials/credentials.ini')

# S3 Bucket Credentials
# ACCESS_KEY_ID = config['Amazon S3 Bucket tyler9937']['ACCESS_KEY_ID']
# SECRET_ACCESS_KEY = config['Amazon S3 Bucket tyler9937']['SECRET_ACCESS_KEY']

# ElephantSql Credentials
# USERNAME = config['ElephantSql Road Lane Detection Instance']['USERNAME']
# PASSWORD = config['ElephantSql Road Lane Detection Instance']['PASSWORD']
# DATABASE = config['ElephantSql Road Lane Detection Instance']['DATABASE']
# HOST = config['ElephantSql Road Lane Detection Instance']['HOST']

# Using Heroku Config varibles
# S3 Bucket Credentials
ACCESS_KEY_ID = os.environ['ACCESS_KEY_ID']
SECRET_ACCESS_KEY = os.environ['SECRET_ACCESS_KEY']

# ElephantSql Credentials
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
DATABASE = os.environ['DATABASE']
HOST = os.environ['HOST']

# Connecting to Amazon S3 Bucket
S3_CLIENT = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)
BUCKET_NAME = 'road-line-detection-scenes' 


# Creating Flask and Dash servers
server = Flask(__name__)
app = dash.Dash(__name__, server = server, external_stylesheets=external_stylesheets, meta_tags=meta_tags)
app.config.suppress_callback_exceptions = True
app.title = 'Road Lane Detection App' # Browser Title


# PostgresSQL Data Base call for bringing in video data
def get_scene_names():
    # Creating the connection to database
    elephantsql_client = connect(DATABASE, USERNAME, PASSWORD, HOST)

    # A "cursor", a structure to iterate over db records to perform queries
    cur = elephantsql_client.cursor()

    command = '''
    SELECT scene FROM road_data_table
    '''

    # Execute commands in order
    cur.execute(command)

    scene_names = []
    scene_list = cur.fetchall()
    for tup in scene_list:
        scene_names.append({'label': tup[0], 'value': tup[0]})

    # Close communication with the PostgreSQL database server
    cur.close()

    # Commit the changes
    elephantsql_client.commit()

    # Close the connection
    elephantsql_client.close()
    print('Connection is closed.')
    return scene_names

# Amazon S3 Bucket video streaming and OpenCV Video Processing
def process_stream(mask_type, width, height, test):
    # Fetching URL stream from amazon s3 bucket
    url = S3_CLIENT.generate_presigned_url('get_object', 
                                           Params = {'Bucket': BUCKET_NAME, 'Key': test}, 
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

                if mask_type == 'test':
                    resized = resize(resized, 400, 300)
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
                    resized = resize(edges, 400, 300)
                    frame = resized

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
                   resized = resize(lanes, 600, 337)
                   frame = resized

                
                # Preparing for export
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                resized = resize(frame, 600, 337)
                frame = resized
                # Preparing for export
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
        else:
            pass


# Using flask routing to connect to video stream
@server.route('/video_stream_predict_lines/<scene_name>')
def video_stream_predict_lines(scene_name):
    return Response(process_stream('predict_lines', 800, 600, scene_name), mimetype='multipart/x-mixed-replace; boundary=frame')


# For the dropdown menu
quantity_dropdown = html.Div(
    [
        dcc.Dropdown(
            id='quantity_dropdown',
            options=get_scene_names(),
            value='scene_1.mp4'
        ),
    ],
)

# Hosts webpage description and dropdown menu
column1 = dbc.Col(
    [
        dcc.Markdown(
            """
        
            ## Model Overview
             In this web application, we demonstrate road lane identification using OpenCV tools such as edge detection, and Hough line detection. We find that our implementation is effective in perfect weather and road conditions. The model struggles with sun glare, shadows, patchy roads, multiple lanes, and traffic. We consider this model a good baseline and look forward to further research in the field. The video data was collected by our team on western Los Angeles roads. The videos are being streamed from an Amazon S3 bucket and a PostgreSQL database hosted on Elephantsql. Below you can select different video scenes and observe how our model performed. The two blue lines are our model's predictionand are being applied in real time.
            """
        ),
        quantity_dropdown

    ],
)

# Hosts the video stream
column2 = dbc.Col(
    [
       html.Div(html.Img(id='output'))
    ]
)

# To be displayed on index page
layout = dbc.Row([column1, column2])

# Rendering the webpage
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    dbc.Container(id='page-content', className='mt-4'),
    footer               
])

# Video Stream routing
@app.callback(Output('output', 'src'),
              [Input('quantity_dropdown', 'value')])

def play_video(scene_name):
    return "/video_stream_predict_lines/" + scene_name

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
    app.run_server()