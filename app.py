from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt


import sqlite3
from table import *

app = Flask(__name__)

@app.route('/')
def index():
    # Connect to SQLite database
    conn = sqlite3.connect('david.db')

    # Read DataFrame from SQLite database
    df = pd.read_sql_query("SELECT * FROM data_table", conn)

    # Close database connection
    conn.close()

    plt = make_table(df)
    plot_data = plot_to_png(plt)
    # Render the HTML template with the plot data
    return render_template('index.html', plot_data=plot_data)

if __name__ == '__main__':
    app.run(debug=True)