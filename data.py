import pandas as pd
import numpy as np
from helper import *
import pycountry
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import sqlite3



# Assuming your CSV file is named 'data.csv' and is located in the same directory as your Python script
file_path = 'data/Internet Speed 2022.csv'
gdp_file = 'data/Countries GDP 1960-2020.csv'
gini_file = 'data/economic-inequality-gini-index.csv'
# Read the CSV file into a pandas DataFrame
df_internet_speed = pd.read_csv(file_path)
df_gdp = pd.read_csv(gdp_file)
df_gini = pd.read_csv(gini_file)

print(df_gini[df_gini['Code'] == np.NaN])

df_gini = df_gini.dropna(subset=['Code'])

# Pivot the DataFrame to have 'Year' as columns
pivoted_gini_df = df_gini.pivot(index='Entity', columns='Year', values='Gini coefficient')

# Reset the index to make 'Entity' a column again
pivoted_gini_df.reset_index(inplace=True)



pivoted_gini_df.columns = ['country'] + ['Gini-' + str(col) for col in pivoted_gini_df.columns[1:]]
# Display the pivoted DataFrame


## rename header df_gdp
df_gdp.columns = ['country'] + ['code'] + ['GDP-' + str(col) for col in df_gdp.columns[2:]]
print(df_gdp.head())
# merge df
merged_df = merge_df(df1=df_internet_speed, df2=df_gdp, tag='country')
print(len(merged_df))

merged_df = merge_df(df1=merged_df,df2=pivoted_gini_df, tag='country')
print(len(merged_df))

# Display the first few rows of the DataFrame
print(merged_df.head())

df = merged_df
df = df.dropna(subset='Gini-2019')
df = df.dropna(subset='GDP-2019')
print(len(df))


# Create a connection to the SQLite database (or it will be created if it doesn't exist)
conn = sqlite3.connect('david.db')

# Write the DataFrame to a table in the SQLite database
df.to_sql('data_table', conn, if_exists='replace', index=False)

# Commit the changes and close the connection
conn.commit()
conn.close()