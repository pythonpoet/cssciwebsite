from flask import Flask, render_template,request,jsonify,send_file
import pandas as pd
import matplotlib.pyplot as plt

import os
import sqlite3
from table import *
import database

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
df=0
plot_data =0
gpd_init_lower =0
gpd_init_upper =0

def mask_df(df,lowest_gdp, highest_gdp):
    print(lowest_gdp, highest_gdp)
    filtered_df = df[(df['gdp'] >= lowest_gdp) & (df['gdp'] <= highest_gdp)]
    print("filtere_df:", filtered_df.head())
    return filtered_df

def init():
    global df, plot_data, gpd_init_lower,gpd_init_upper
    df = handle_db('david.db')
    gpd_init_lower,gpd_init_upper = calculate_lower_upper_values(df)
    new_df = mask_df(df,gpd_init_lower,gpd_init_upper)
    plt = make_table(new_df)
    plot_data = plot_to_png(plt)
    
init()
# Define a function to calculate the most lower and upper values
def calculate_lower_upper_values(df):
    # Your calculation logic here
    # For demonstration purposes, let's assume some default values
    lower_value = df['gdp'].min()
    upper_value = df['gdp'].max()
    return lower_value, upper_value

def handle_db(db_name):
    # check if db is already initialised
    if not os.path.exists(db_name):
        #Imports file that initialise database
        import data
        db = database.Database(db_name=db_name)
        data.initialise_db(db)
    db = database.Database(db_name=db_name)
    return db.read_data()

@app.route('/')
def index():
    return "hello world"
    global df, plot_data, gpd_init_lower,gpd_init_upper
    # Initialize an empty list to store file contents
    blog_posts = ""


                
    print("david was here")
    return render_template('index.html',)# blog_posts=blog_posts,)#data={"plot_data":plot_data,"lower_value":gpd_init_lower,"upper_value":gpd_init_upper})

# Route to handle processing the values sent from the client
@app.route('/process_values', methods=['POST'])
def process_values():
    global df, plot_data, gpd_lower,gpd_upper
    # Retrieve values from the request
    data = request.json
    gpd_lower = float(data['lowerValue'])
    gpd_upper = float(data['upperValue'])

    #update the graph
    new_df = mask_df(df,gpd_lower, gpd_upper)
    plt = make_table(new_df)
    plot_data = plot_to_png(plt)
    
    # Process the values as needed
    # For demonstration, just return them
    return jsonify({'lowerValue': gpd_lower, 'upperValue': gpd_upper})

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    input_string = request.form['input_string']

     # Read the contents of the uploaded file into a string
    file_contents = uploaded_file.read().decode('utf-8')
    
    import backend.python_psychologist.python_psychologist 
    insights =backend.python_psychologist.python_psychologist.psychologist_find_insights(file_contents)

    return insights


@app.route('/robot-icon')
def get_bot_icon():
    # Replace 'path_to_bot_icon' with the actual path to your bot icon image
    return send_file('static/robot.png', mimetype='image/png')

if __name__ == '__main__':
    print("run programm")
    init()
    app.run(debug=True,port=5144)