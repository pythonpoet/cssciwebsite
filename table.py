import pandas as pd
import numpy as np
from helper import *
import pycountry
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import sqlite3

def make_table(df:pd.DataFrame):
    # Create the scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(df['broadband'], df['Gini-2019'])

    # Annotate each point with its country name
    for i, txt in enumerate(df['country']):
        plt.annotate(txt, (df['broadband'].iloc[i], df['Gini-2019'].iloc[i]), textcoords="offset points", xytext=(0,10), ha='center')

    # Set the labels and title
    plt.xlabel('Broadband')
    plt.ylabel('Gini-2019')
    plt.title('Scatter plot of Broadband vs. Gini-2019')

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
