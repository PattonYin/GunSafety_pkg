# Patent package from R
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import ast

class Patent_Descriptive:
    ''' 
    Python version of the patent package from R
    '''
    def __init__(self, data) :
        self.data = data
        
    def reformat(self):
        ''' 
        reformat the dataset to correct datatype. 
        SHOULD be run before any other functions. 
        '''
        # transform city, name, state into list
        for col in ['inventorsName', 'inventorCity', 'inventorState', 'assigneeName', 'assigneeCity', 'assigneeState']:
            self.data[col] = self.data[col].apply(self.convert_string_to_list)
        # convert cpcInventiveFlattened into list
        self.data['cpcInventiveFlattened'] = self.data['cpcInventiveFlattened'].str.replace(r"[\[\]']", "", regex=True)
        self.data['cpcInventiveFlattened'] = self.data['cpcInventiveFlattened'].apply(lambda x: x.split(';') if pd.notna(x) else x)
        # convert datePublished, applicationFilingDate into datetime
        for col in ['datePublished', 'applicationFilingDate']:
            self.data[col] = pd.to_datetime(self.data[col], errors='coerce', format='%Y-%m-%d').dt.date
        return self.data

    
    def clean_by(self, column):
        """
        Clean the dataset based on a column.
        This function cleans the dataset based on the columns about demographic data, including:
        inventorState, assigneeState, inventorName, assigneeName, inventorCity, and assigneeCity.
        If the column is inventorState or assigneeState, it will separate the column into multiple rows,
        clean the duplicates, and other countries.
        input:
            self.data (pd.DataFrame): The dataset to clean.
            column (str): The name of the column to clean. It can be inventorState or assigneeState.
        output:
            pd.DataFrame: The cleaned dataset. Usually, it has more rows than the original dataset.
        """
        # Clean square brackets and single quotes
        # self.data[column] = self.data[column].str.replace(r"[\[\]']", "", regex=True)
        # Expand the column into multiple rows split by ', '
        new_set = self.data.copy()
        # new_set = new_set.drop(column, axis=1).join(new_set.explode(column).reset_index(drop=True))
        new_set = new_set.explode(column).reset_index(drop=True)
        if column in ["inventorState", "assigneeState"]:
            # Clean specific states and remove duplicates and non-US states
            replacements = {
                "CA 91106": "CA",
                "MT 59829": "MT",
                "N/A": pd.NA,
                "NB": pd.NA,
                "PR": pd.NA,
                "CH": pd.NA,
                "GB2": pd.NA,
                "Attorney at Law 1041": pd.NA,
                "US": pd.NA
            }
            new_set[column] = new_set[column].replace(replacements)
        return new_set
    
    def convert_string_to_list(self, value):
        '''Convert string to list using ast.literal_eval if applicable
        HELPER function with reformat
        '''
        if pd.isna(value) or value == np.nan:  # Checks for NA or NaN values
            return value  # Returns the NA value as is
        try:
            return ast.literal_eval(value)  # Tries to convert string to list
        except (ValueError, SyntaxError) as e:
            # Handles any value that literal_eval can't parse
            if type(value) == str:
                return [value]
            else: 
                return pd.NA  # You can decide how to handle errors
        
        
if __name__ == "__main__":
    data = pd.read_csv('/Users/liusimin/Desktop/Gun Safety/papers/patents_public.csv')
    subset = data.iloc[30000:30100].reset_index(drop=True)  
    # test0: reformat 
    PD = Patent_Descriptive(subset)
    # print(PD.data[['guid','inventorCity']].head())
    # print(type(PD.data['inventorCity'].iloc[0]))
    PD.reformat()
    # print(PD.data['inventorCity'].iloc[0])
    # print(type(PD.data['inventorCity'].iloc[0]))
    # print(PD.data.head())

    # test1: general test on invnetorState
    PD = Patent_Descriptive(subset)
    for col in ['inventorsName', 'inventorCity', 'inventorState', 'assigneeName', 'assigneeCity', 'assigneeState']:
        print(PD.data[['guid',col]])
        print('original dataset shape:', PD.data.shape)
        pd_cb1 = PD.clean_by(col)
        print(pd_cb1[['guid',col]])
        print('cleaned dataset shape:', pd_cb1.shape)
        print('#'*30)
        
    
        
    
    