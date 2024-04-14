from fuzzywuzzy import process
import pandas as pd

def merge_df(df1, df2, tag):
    # Dictionary to store mappings between country names
    country_mapping = {}

    # Iterate through countries in df2 and find best matches in df
    for country in df1[tag]:
        # Find best match in df
        match = process.extractOne(country, df2[tag])
        # Add mapping to dictionary
        country_mapping[country] = match[0]

    # Replace country names in df2 with their best matches
    df1[tag] = df1[tag].map(country_mapping)

    # Now, you can merge the two dataframes based on country column
    merged_df = pd.merge(df2, df1, on=tag, how='inner')
    return merged_df