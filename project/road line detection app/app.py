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

import psycopg2


# Acessing Credentials
config = configparser.ConfigParser()
config.read('../credentials/credentials.ini')

# S3 Bucket Credentials
ACCESS_KEY_ID = config['Amazon S3 Bucket tyler9937']['ACCESS_KEY_ID']
SECRET_ACCESS_KEY = config['Amazon S3 Bucket tyler9937']['SECRET_ACCESS_KEY']

# ElephantSql Credentials
USERNAME = config['ElephantSql Road Lane Detection Instance']['USERNAME']
PASSWORD = config['ElephantSql Road Lane Detection Instance']['PASSWORD']
DATABASE = config['ElephantSql Road Lane Detection Instance']['DATABASE']
HOST = config['ElephantSql Road Lane Detection Instance']['HOST']

# Connecting to Amazon S3 Bucket
S3_CLIENT = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)
BUCKET_NAME = 'road-line-detection-scenes'      
TEMP_KEY = 'scene_1.mp4' 


# Creating Flask and Dash servers
server = Flask(__name__)
app = dash.Dash(__name__, server = server, external_stylesheets=external_stylesheets, meta_tags=meta_tags)
app.config.suppress_callback_exceptions = True # see https://dash.plot.ly/urls
app.title = 'Tanzanian Ministry of Water Data Analysis' # appears in browser title bar


def connect(DATABASE, USERNAME, PASSWORD, HOST):
    """ Connect to the PostgreSQL database server """
    elephantsql_client = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')

        # Connect to ElephantSQL-hosted PostgreSQL
        elephantsql_client = psycopg2.connect(dbname=DATABASE, user=USERNAME, password=PASSWORD, host=HOST)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    return elephantsql_client

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
                resized = resize(frame, width, height)
                frame = resized
                # Preparing for export
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
        else:
            pass


@server.route('/video_stream_predict_lines/<test>')
def video_stream_predict_lines(test):

    return Response(process_stream('predict_lines', 800, 600, test), mimetype='multipart/x-mixed-replace; boundary=frame')

# @server.route('/video_stream_edge_detection')
# def video_stream_edge_detection():
#     return Response(process_stream('edge_detection', 400, 300), mimetype='multipart/x-mixed-replace; boundary=frame')

# @server.route('/video_stream_original')
# def video_stream_original():
#     return Response(process_stream('original', 400, 300), mimetype='multipart/x-mixed-replace; boundary=frame')


quantity_dropdown = html.Div(
    [
        
        dcc.Dropdown(
            id='quantity_dropdown',
            options=get_scene_names(),
            value='scene_1.mp4'
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
        quantity_dropdown

    ],
)

column2 = dbc.Col(
    [
       html.Div(html.Img(id='output')),
    #    html.Div(html.Img(src="/video_stream_edge_detection"),style={'float': 'left'}),
    #    html.Div(html.Img(src="/video_stream_original", style={'float': 'right'})),

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
    app.run_server(debug=True)