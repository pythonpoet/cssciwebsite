import pandas as pd
import numpy as np
from helper import *
import pycountry
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import sqlite3
import pycountry

def get_country_code(country_name):
    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_3
    except LookupError:
        print(f'country_name: {country_name} Unknown')
        return 'Unknown'

def make_table(df:pd.DataFrame):
    # Create the scatter plot
    plt.figure(figsize=(12,8))
    plt.scatter(df['broadband'], df['gini'])

    # Annotate each point with its country name
    for i, txt in enumerate(df['country']):
        #txt = get_country_code(txt)
        plt.annotate(txt, (df['broadband'].iloc[i], df['gini'].iloc[i]), textcoords="offset points", xytext=(0,10), ha='center')

    # Set the labels and title
    plt.xlabel('Broadband')
    plt.ylabel('gini')
    plt.title('Scatter plot of Broadband vs. gini')

    # Show the plot
    plt.grid(True)
    return plt

def plot_to_png(plt):
    # Save plot to a bytes object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    return plot_data
