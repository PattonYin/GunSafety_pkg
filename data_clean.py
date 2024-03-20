# data clean code

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import ast

data = pd.read_csv('/Users/liusimin/Desktop/Gun Safety/papers/patents_public.csv')

# transform city, name, state into list
def convert_string_to_list(value):
    '''Convert string to list using ast.literal_eval if applicable'''
    if pd.isna(value):  # Checks for NA or NaN values
        return value  # Returns the NA value as is
    try:
        return ast.literal_eval(value)  # Tries to convert string to list
    except (ValueError, SyntaxError) as e:
        # Handles any value that literal_eval can't parse
        if type(value) == str:
            return [value]
        return pd.NA  # You can decide how to handle errors


for col in ['inventorsName', 'inventorCity', 'inventorState', 'assigneeName', 'assigneeCity', 'assigneeState']:
    data[col] = data[col].apply(convert_string_to_list)
 
# check accuracy; pass
# for col in ['inventorsName', 'inventorCity', 'inventorState', 'assigneeName', 'assigneeCity', 'assigneeState']:
#     print(col)
#     for i in range(30000, 30010):
#         print(data[col].iloc[i])
#         print(type(data[col].iloc[i]))
#     print('*' * 20)

# convert cpcInventiveFlattened into list
data['cpcInventiveFlattened'] = data['cpcInventiveFlattened'].apply(lambda x: x.split(', ') if pd.notna(x) else x)

# check accuracy; pass
# for i in range(30000, 30010):
#     print(data['cpcInventiveFlattened'].iloc[i])
#     print(type(data['cpcInventiveFlattened'].iloc[i]))
# print('*' * 20)

# convert datePublished, applicationFilingDate into datetime
for col in ['datePublished', 'applicationFilingDate']:
    data[col] = pd.to_datetime(data[col], errors='coerce').dt.date
# print(data[['datePublished', 'applicationFilingDate']].head())


data.to_csv('/Users/liusimin/Desktop/Gun Safety/papers/patents_public2.csv', index=False)