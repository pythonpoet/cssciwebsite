import pandas as pd
import numpy as np
from helper import *
import pycountry
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import sqlite3
from database import *

def df_to_db(db_name:str,df: pd.DataFrame):
    # Create a connection to the SQLite database (or it will be created if it doesn't exist)
    conn = sqlite3.connect(db_name)

    # Write the DataFrame to a table in the SQLite database
    df.to_sql('data_table', conn, if_exists='replace', index=False)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def count_country(df):
        # Count occurrences of each country
    country_counts = df['country'].value_counts()

    # Print each country along with its count
    for country, count in country_counts.items():
        if count > 1:
            print(f"More than once: Country: {country}, Count: {count}")

def read_data():
    # Assuming your CSV file is named 'data.csv' and is located in the same directory as your Python script
    file_path = 'data/Internet Speed 2022.csv'
    gdp_file = 'data/Countries GDP 1960-2020.csv'
    gini_file = 'data/economic-inequality-gini-index.csv'
    # Read the CSV file into a pandas DataFrame
    df_internet_speed = pd.read_csv(file_path)
    df_gdp = pd.read_csv(gdp_file)
    df_gini = pd.read_csv(gini_file)
    return df_internet_speed, df_gdp, df_gini

def clean_gini_data(df_gini):
    # In the dataset there is the difference beteween urban and rural area.
    # -> I cant use this information
    df_gini = df_gini.dropna(subset=['Code'])
    # Pivot the DataFrame to have 'Year' as columns
    pivoted_gini_df = df_gini.pivot(index='Entity', columns='Year', values='Gini coefficient')
    # Reset the index to make 'Entity' a column again
    pivoted_gini_df.reset_index(inplace=True)
    # Rename header
    pivoted_gini_df.columns = ['country'] + ['gini_' + str(col) for col in pivoted_gini_df.columns[1:]]
    #! Will do in sqlite
    #pivoted_gini_df= pivoted_gini_df.dropna(subset='Gini_2019')

    return pivoted_gini_df

def clean_gdp(df_gdp):
    # Rename header
    df_gdp.columns = ['country'] + ['code'] + ['gdp_' + str(col) for col in df_gdp.columns[2:]]
    df_gdp.drop(columns=['code'], inplace=True)
    return df_gdp

def clean_internet_speed(df_internet_speed):
    # Cleaning not implemented
    return df_internet_speed
def merge_data(df_internet_speed, df_gdp, df_gini):
    merged_df = merge_df(df1=df_internet_speed, df2=df_gdp, tag='country')
    
    count_country(merged_df)
    merged_df = merge_df(df1=merged_df,df2=df_gini, tag='country')
    
    return merged_df
def create_shared_table(df_internet_speed, df_gdp, df_gini):
    # Create a list of DataFrames
    dfs = [df_internet_speed, df_gdp, df_gini]

    print(df_gdp["gdp_2019"])
    print(df_gini["gini_2019"])

    # Find the common columns across all DataFrames
    common_cols = set.intersection(*[set(df.columns) for df in dfs])

    # Combine all DataFrames into a single DataFrame
    df_all = pd.concat(dfs, axis=1)
    df_merged = df_all[common_cols]

    # Create an SQLite connection
    conn = sqlite3.connect('sample.db')
    c = conn.cursor()

    # Create a table for the shared columns
    c.execute('''CREATE TABLE shared_table
                (country TEXT PRIMARY KEY, broadband REAL, "GDP 2019" REAL, "Gini 2019" REAL)''')

    # Populate the shared table with data from all DataFrames
    values = df_merged.values.tolist()
    c.executemany('INSERT INTO shared_table (country, broadband, "GDP 2019", "Gini 2019") VALUES (?, ?, ?, ?)', values)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def initialise_db(db: Database):
    # read data
    df_internet_speed, df_gdp, df_gini = read_data()

    # clean df_gini
    df_gini = clean_gini_data(df_gini)
    # clean df_gdp
    df_gdp = clean_gdp(df_gdp)
    # clean df_internet_speed
    df_internet_speed = clean_internet_speed(df_internet_speed)
    #write to db
    db.write_data(df_internet_speed, df_gdp, df_gini)

    
# Test
if __name__ == "__main__":
    initialise_db("test.db")