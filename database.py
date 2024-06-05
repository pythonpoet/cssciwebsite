import sqlite3
import pandas as pd
from typing import List
import numpy as np
class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        # Connect to SQLite database (creates if it doesn't exist)
        self.conn = sqlite3.connect(db_name)
        # Create a cursor object to execute SQL commands
        self.cursor = self.conn.cursor()
        print(f"Initialise database with db_name: {self.db_name}")

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        print(f"Destructing database instance: {self.db_name}")
    def create_blog_post_table(self):
        # Define the SQL command to create the table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS blog_post_table (
            id INTEGER PRIMARY KEY,
            blog_post_id TEXT NOT NULL,
            category_id TEXT NOT NULL,
            published_date TEXT NOT NULL,
        );
        '''
        # Execute the SQL command to create the table
        self.cursor.execute(create_table_query)
        print("blog_post_table table created successfully.")
    def create_access_table(self):
        # Define the SQL command to create the table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS access (
            id INTEGER PRIMARY KEY,
            category_id TEXT NOT NULL,
            Category_name TEXT NOT NULL,
            Category_type TEXT NOT NULL,
            Category_topic TEXT Not NULL,
        );
        '''
        # Execute the SQL command to create the table
        self.cursor.execute(create_table_query)
        print("access_table table created successfully.")

    def create_country_table(self):
        # Define the SQL command to create the table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        '''
        # Execute the SQL command to create the table
        self.cursor.execute(create_table_query)
        print("Country table created successfully.")

    def create_broadband_table(self):
        # Define the SQL command to create the table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS broadband_data (
            id INTEGER PRIMARY KEY,
            country TEXT NOT NULL,
            broadband_speed REAL NOT NULL
        );
        '''
        # Execute the SQL command to create the table
        self.cursor.execute(create_table_query)
        print("Broadband data table created successfully.")

    def create_gini_table(self, years: List[int]):
        # Define the SQL command to create the table
        create_table_query = f'''
        CREATE TABLE IF NOT EXISTS gini_index (
            id INTEGER PRIMARY KEY,
            country TEXT NOT NULL,
            {", ".join([f"gini_{year} REAL " for year in years])}
        );
        '''

        # Execute the SQL command to create the table
        self.cursor.execute(create_table_query)
        print("Gini index table created successfully.")

    def create_gdp_table(self, years: List[int]):
        # Define the SQL command to create the table
        create_table_query = f'''
        CREATE TABLE IF NOT EXISTS gdp_table (
            id INTEGER PRIMARY KEY,
            country TEXT NOT NULL,
            {", ".join([f"gdp_{year} REAL " for year in years])}
        );
        '''
        # Execute the SQL command to create the table
        self.cursor.execute(create_table_query)
        print("GDP table created successfully.")

    def insert_blog_post(self, blog_post_id, category_id, published_date):
        # Define the SQL command to insert values into the table
        insert_query = '''
        INSERT INTO blog_post_table (blog_post_id, category_id, published_date)
        VALUES (?, ?, ?);
        '''
        # Execute the SQL command to insert values into the table
        self.cursor.execute(insert_query, (blog_post_id, category_id, published_date))
        # Commit the transaction
        self.connection.commit()
        print("blog post inserted successfully.")


    def insert_country_data(self, countries: List[str]):
        # Insert country names into the table
        for name in countries:
            insert_query = "INSERT INTO countries (name) VALUES (?)"
            self.cursor.execute(insert_query, (name,))
        self.conn.commit()
        print("Country data inserted successfully.")

    def insert_broadband_data(self, df: pd.DataFrame):
        # Insert broadband data from DataFrame
        for index, row in df.iterrows():
            country = row['country']
            broadband = row['broadband']
            insert_query = "INSERT INTO broadband_data (country, broadband_speed) VALUES (?, ?)"
            self.cursor.execute(insert_query, (country, broadband))
        self.conn.commit()
        print("Broadband data inserted successfully.")

    def insert_gini_data(self, df: pd.DataFrame):
        # Insert Gini index data from DataFrame
        for index, row in df.iterrows():
            country = row['country']
            gini_values = row.values[1:]  # Extract Gini index values excluding the country column
            if any(gini_values):  # Check if there are any Gini index values for the current country
                placeholders = ', '.join(['?'] * len(gini_values))
                column_names = ', '.join(df.columns[1:])  # Exclude the country column from column names
                insert_query = f"INSERT INTO gini_index (country, {column_names}) VALUES (?, {placeholders})"
                self.cursor.execute(insert_query, [country] + list(gini_values))
        self.conn.commit()
        print("Gini index data inserted successfully.")
    
    def insert_gdp_data(self, df: pd.DataFrame):
        # Insert Gini index data from DataFrame
        for index, row in df.iterrows():
            country = row['country']
            gdp_values = row.values[1:]  # Extract Gini index values excluding the country column
            if any(gdp_values):  # Check if there are any Gini index values for the current country
                placeholders = ', '.join(['?'] * len(gdp_values))
                column_names = ', '.join(df.columns[1:])  # Exclude the country column from column names
                insert_query = f"INSERT INTO gdp_table (country, {column_names}) VALUES (?, {placeholders})"
                self.cursor.execute(insert_query, [country] + list(gdp_values))
        self.conn.commit()
        print("GDP data inserted successfully.")

    def read_data_coalesce(self, table_name, column_prefix):
        # Get the list of available index columns
       
        self.cursor.execute( f"PRAGMA table_info({table_name})")
        columns_info = self.cursor.fetchall()
        gini_columns = [column[1] for column in columns_info if column[1].startswith(column_prefix)]

        # Generate the COALESCE expression for selecting the latest non-null Gini index value
        coalesce_expr = f"COALESCE(" + ", ".join(gini_columns[::-1]) + ")"
        return coalesce_expr

    def read_country_broadband_gini(self):
        country_broadband_gini_data = []

        coalesce_gini = self.read_data_coalesce('gini_index', 'gini_')
        #coalesce_gpd = self.read_data_coalesce('gdp_table', 'gdp_','gpd')

        # Execute a SQL query to retrieve data from the database
        query = f'''
            SELECT c.name AS country, bd.broadband_speed AS broadband, {coalesce_gini} AS gini
            FROM countries c
            LEFT JOIN broadband_data bd ON c.name = bd.country
            LEFT JOIN gini_index gi ON c.name = gi.country
        '''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        for row in rows:
            country_broadband_gini_data.append(row)

        country_broadband_gini_df = pd.DataFrame(country_broadband_gini_data, columns=['country', 'broadband', 'gini'])
        return country_broadband_gini_df

    def read_country_gpd(self):
        country_gpd_data = []

        coalesce_gpd = self.read_data_coalesce('gdp_table', 'gdp_')

        # Execute a SQL query to retrieve data from the database
        query = f'''
            SELECT c.name AS country,  {coalesce_gpd} AS gdp
            FROM countries c
            LEFT JOIN gdp_table gt ON c.name = gt.country
        '''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        for row in rows:
            country_gpd_data.append(row)

        df_country_gdp = pd.DataFrame(country_gpd_data, columns=['country', 'gdp'])
        return df_country_gdp
               
    def read_data(self) -> pd.DataFrame:
        df_country_broadband_gini = self.read_country_broadband_gini()
        df_country_gdp = self.read_country_gpd()
        # merge df's
        df_country_broadband_gini_gdp = df_country_broadband_gini
        df_country_broadband_gini_gdp['gdp']= df_country_gdp['gdp']
        return df_country_broadband_gini_gdp
    def write_data(self,df_internet_speed, df_gdp, df_gini):
        # Initialise tables
        self.create_country_table()
        self.create_broadband_table()
        # read years in df
        gini_years = [int(column.split('_')[1]) for column in df_gini.columns if column.startswith('gini_')]
        self.create_gini_table(gini_years)
        # read years in df
        gdp_years = [int(column.split('_')[1]) for column in df_gdp.columns if column.startswith('gdp_')]
        
        self.create_gdp_table(gdp_years)

        # Write to datatable

        #Use ISO-coutry name
        import pycountry
        countries_ = list(pycountry.countries)
        countries = [country.name for country in countries_]
        self.insert_country_data(countries)

        self.insert_broadband_data(df_internet_speed)
        self.insert_gini_data(df_gini)
        self.insert_gdp_data(df_gdp)

# Test database with artificial data
if __name__ == "__main__":
    # Example usage:
    db = Database('example.db')
    db.create_country_table()
    db.create_broadband_table()

    countries = ["United States", "United Kingdom", "Germany"]
    db.insert_country_data(countries)

    # Example DataFrame for broadband data
    broadband_df = pd.DataFrame({
        'country': ["United States", "United Kingdom", "Germany"],
        'broadband': [50.5, 60.2, 45.8]
    })
    db.insert_broadband_data(broadband_df)

    # Example DataFrame for Gini index data
    gini_df = pd.DataFrame({
        'country': ["United States", "United Kingdom", "Germany"],
        'gini_2014': [0.41, 0.34, 0.29],
        'gini_2015': [0.42, 0.35, 0.30],
        'gini_2016': [0.43, 0.36, 0.60],
        'gini_2017': [0.43, 0.36, np.NaN]

    })

    years = [int(column.split('_')[1]) for column in gini_df.columns if column.startswith('gini_')]
    db.create_gini_table(years)
    db.insert_gini_data(gini_df)
    df = db.read_gini_data()
    print(df.head())
    df = db.read_data()
    print(df.head())
