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
        self.data[column] = self.data[column].str.replace(r"[\[\]']", "", regex=True)
        # Expand the column into multiple rows split by ', '
        new_set = self.data.copy()
        new_set = new_set.drop(column, axis=1).join(
            new_set[column].str.split(', ', expand=True).stack().reset_index(level=1, drop=True).rename(column)
        )
        if column in ["inventorState", "assigneeState"]:
            # Clean specific states and remove duplicates and non-US states
            replacements = {
                "CA 91106": "CA",
                "MT 59829": "MT",
                "N/A": np.nan,
                "NB": np.nan,
                "PR": np.nan,
                "CH": np.nan,
                "GB2": np.nan,
                "Attorney at Law 1041": np.nan,
                "US": np.nan
            }
            new_set[column] = new_set[column].replace(replacements)
        
        return new_set
        
        
if __name__ == "__main__":
    data = pd.read_csv('/Users/liusimin/Desktop/Gun Safety/papers/patents_public2.csv')
    subset = data.iloc[30000:30100].reset_index(drop=True)  
    # test1: general test on invnetorState
    PD = Patent_Descriptive(subset)
    print(PD.data[['guid','inventorState']])
    print('original dataset shape:', PD.data.shape)
    print('*' * 20)
    pd_cb1 = PD.clean_by('inventorState')
    print(pd_cb1[['guid','inventorState']])
    print('cleaned dataset shape:', pd_cb1.shape)
    
    # test2: test on multiple states
    
    