# Patent package from R
import pandas as pd
import matplotlib.pyplot as plt
import ast
from collections import Counter
import matplotlib.ticker as ticker
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
        try: # transform city, name, state into list
            for col in ['inventorsName', 'inventorCity', 'inventorState', 'assigneeName', 'assigneeCity', 'assigneeState']:
                self.data[col] = self.data[col].apply(self.convert_string_to_list)
        except KeyError:
            pass
        try: # convert cpcInventiveFlattened into list
            self.data['cpcInventiveFlattened'] = self.data['cpcInventiveFlattened'].str.replace(r"[\[\]']", "", regex=True)
            self.data['cpcInventiveFlattened'] = self.data['cpcInventiveFlattened'].apply(lambda x: x.split(';') if pd.notna(x) else x)
        except KeyError:
            pass
        try: # convert datePublished, applicationFilingDate into datetime
            self.data['datePublished'] = pd.to_datetime(self.data['datePublished'], errors = 'coerce')
            self.data['applicationFilingDate'] = pd.to_datetime(self.data['applicationFilingDate'], errors = 'coerce')
        except KeyError:
            pass
        return self.data

    
    def clean_by(self, data, column):
        """
        Clean the dataset based on a column.
        This function cleans the dataset based on the columns about demographic data, including:
        inventorState, assigneeState, inventorName, assigneeName, inventorCity, and assigneeCity.
        If the column is inventorState or assigneeState, it will separate the column into multiple rows,
        clean the duplicates, and other countries.
        input:
            data (pd.DataFrame): The dataset to clean.
            column (str): The name of the column to clean. It can be inventorState or assigneeState.
        output:
            pd.DataFrame: The cleaned dataset. Usually, it has more rows than the original dataset.
        """
        # Clean square brackets and single quotes
        # self.data[column] = self.data[column].str.replace(r"[\[\]']", "", regex=True)
        # Expand the column into multiple rows split by ', '
        new_set = data.copy()
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
    
    def frequency(self, data, column, graph = True, num = 5, rotation = 45,
                  descending = True, figsize = (10, 6), color = 'hotpink'):
        """
        Generate a frequency table for a column.
        This function generates a frequency table for a column.
        If the column is 'keywords', it will generate a frequency table for the keywords.
        input:
            data (pd.DataFrame): The dataset to analyze.
            column (str): The name of the column to analyze.
            graph (bool): Whether to generate a bar plot. Default is True.
            num (int): The top n values to display in the plot. Default is 5.
            rotation (int): The rotation of the x-axis labels in the plot. Default is 45.
            descending (bool): Whether to sort the frequency table in descending order. Default is True.
            figsize (tuple): The size of the plot. Default is (10, 6).
            color (str): The color of the bars in the plot. Default is 'hotpink'.
        output:
            pd.DataFrame: The frequency table for the column.
        """
        if column not in data.columns:
            raise ValueError(f"The column '{column}' does not exist in the DataFrame.")
        # Generate frequency table
        if column == 'keyword':
            all_words = [word for sublist in data['keyword'] if sublist is not pd.NA for word in sublist]
            word_counts = Counter(all_words)
            frequency_table = pd.DataFrame(word_counts.items(), columns=[column, 'Frequency']).sort_values(by='Frequency', ascending=False).reset_index(drop=True)
        else: 
            frequency_table = data[column].value_counts().sort_values(ascending=(not descending)).reset_index()
            frequency_table.columns = [column, 'Frequency']
        # Display the frequency table
        print(f"Frequency table for '{column}':")
        print(frequency_table.head(num))
        # Plot the frequency distribution
        if graph: 
            plt.figure(figsize=figsize)
            frequency_table.iloc[:num].plot(x= column, y = 'Frequency', kind='bar', color = color)
            plt.title(f'Frequency Distribution of {column}')
            plt.xlabel(column)
            plt.xticks(rotation = rotation, ha='right', fontsize=10)
            plt.ylabel('Frequency')
            plt.tight_layout()
            plt.show()
        return frequency_table
    
    def freq_by_group(self, data, group, target, graph = True, rotation = 45,
                      num = 5, figsize = (10, 6), color = 'tomato', 
                      descending = True):
        ''' 
        Draw the frequency distribution of a target variable by a group variable. 
        Default is to draw bar plots.
        inputs:
            data (pd.DataFrame): The dataset to analyze.
            group (str): The name of the column to group by.
            target (str): The name of the column to analyze.
            graph (bool): Whether to generate a bar plot. Default is True.
            rotation (int): The rotation of the x-axis labels in the plot. Default is 45.
            num (int): The top n values to display in the plot. Default is 5.
            figsize (tuple): The size of the plot. Default is (10, 6).
            color (str): The color of the bars in the plot. Default is 'tomato'.
            descending (bool): Whether to sort the frequency table in descending order. Default is True.
        output: list. A list of frequency tables for each group.
        '''
        # Check if the columns exist in the DataFrame
        if group not in data or target not in data:
            raise ValueError(f"One or both columns '{group}' and '{target}' do not exist in the DataFrame.")
        grouped = data.groupby(group)  # Group the dataframe by the specified column
        frequency_tables = []  # List to store frequency tables
        for group_name, group_df in grouped:
            if target == 'keyword':
                all_words = [word for sublist in group_df['keyword'] if sublist is not pd.NA for word in sublist]
                word_counts = Counter(all_words)
                frequency_table = pd.DataFrame(word_counts.items(), columns=[target, 'Frequency']).sort_values(by='Frequency', ascending=False).reset_index(drop=True)
            else: 
                frequency_table = data[target].value_counts().sort_values(ascending=(not descending)).reset_index()
                frequency_table.columns = [target, 'Frequency']
            print(f"Frequency table for '{target}' by '{group}': {group_name}")
            print(frequency_table.head(num))
            frequency_tables.append(frequency_table)
            
            if graph: 
                try: 
                    plt.figure(figsize=figsize)
                    frequency_table.iloc[:num].plot(x= target, y = 'Frequency', kind='bar', color = color)
                    plt.title(f'Frequency Distribution of {target} for {group_name}')
                    plt.xlabel(target)
                    plt.xticks(rotation = rotation, ha='right', fontsize=10)
                    plt.ylabel('Frequency')
                    plt.tight_layout()
                    plt.show()
                except TypeError:
                    print(f"No data available for '{group_name}'")
                    continue
        return frequency_tables
    
    def separate_category(self, data):
        ''' 
        Separate the cpcInventiveFlattened column into multiple columns and rows.
        input: 
            data (pd.DataFrame): The dataset to separate.
        output:
            pd.DataFrame: The dataset with cpcInventiveFlattened separated into multiple columns and rows.
        '''
        data = data.explode('cpcInventiveFlattened').reset_index(drop=True)
        pattern = r'([A-Z])(\d+)([A-Z])(\d+)/(\d+)'
        # Extract the parts of the CPC code using the defined pattern
        cpc_parts = data['cpcInventiveFlattened'].str.extract(pattern)
        cpc_parts.columns = ['category', 'subcategory1', 'subcategory2', 'subcategory3', 'subcategory4']
        # Concatenate the original DataFrame with the new columns
        data = pd.concat([data, cpc_parts], axis=1)
        return data
    
    def dummy_by_time(self, data, column, cutoff, dummy = 'dummy'):
        ''' 
        Create the dummy code for a column by time.
        input:
            data (pd.DataFrame): The dataset to use. 
            column (str): The name of the column to create the dummy variable for.
            cutoff (str): The cutoff time to create the dummy variable.
            dummy (str): The name of the dummy variable. Default is 'dummy'.
        output:
            pd.DataFrame: The dataset with the dummy variable.
        '''
        if isinstance(cutoff, str):
            cutoff = pd.to_datetime(cutoff)
        else: 
            raise ValueError("The cutoff time should be a string.")
        data[dummy] = (data[column] < cutoff).astype(int)
        return data
    
    def first_appear(self, data, target, graph = True, figsize = (10, 6), color = 'lightgreen'):
        ''' 
        Generate a bar plot of the first appearance of target column.
        input:
            data (pd.DataFrame): The dataset to analyze.
            target (str): The name of the column to analyze.
            graph (bool): Whether to generate a line plot. Default is True.
            figsize (tuple): The size of the plot. Default is (10, 6).
            color (str): The color of the bars in the plot. Default is 'lightgreen'.
        output:
            pd.DataFrame: The first appearance of target column.
        '''
        data = data[target].astype(str)
        first_appear = data.groupby(target)['datePublished'].min().sort_values().reset_index()
        first_appear.columns = [target, 'FirstAppearance']
        first_appear['Year'] = first_appear['FirstAppearance'].dt.year
        counts = first_appear.groupby('Year').size()
        print(counts)
        if graph: 
            plt.figure(figsize=figsize)
            counts.plot(kind='line', color=color)
            plt.title('First Appearance of ' + target + ' Over Time')
            plt.xlabel('Year')
            plt.ylabel('Frequency')
            ax = plt.gca()  # 'get current axis'
            ax.xaxis.set_major_locator(ticker.MultipleLocator(base=15)) 
            plt.tight_layout()
            plt.show()
        return first_appear
  
     # ----------- HELPER Function Section ----------- 
    def convert_string_to_list(self, value):
        '''Convert string to list using ast.literal_eval if applicable
        HELPER function with reformat
        '''
        if pd.isna(value):  
            return value  
        try:
            return ast.literal_eval(value)  
        except (ValueError, SyntaxError):
            if type(value) == str:
                return [value]
            else: 
                return pd.NA  
        
if __name__ == "__main__":
    data = pd.read_csv('/Users/liusimin/Desktop/Gun Safety/papers/patents_public.csv')
    subset = data.iloc[10000:30100].reset_index(drop=True)  
    # test0: reformat 
    # PD = Patent_Descriptive(subset)
    # print(PD.data[['guid','inventorCity']].head())
    # print(type(PD.data['inventorCity'].iloc[0]))
    # PD.reformat()
    # print(PD.data['inventorCity'].iloc[0])
    # print(type(PD.data['inventorCity'].iloc[0]))
    # print(PD.data.head())

    # test1: general test on invnetorState
    # PD = Patent_Descriptive(subset)
    # PD.reformat()
    # for col in ['inventorsName', 'inventorCity', 'inventorState', 'assigneeName', 'assigneeCity', 'assigneeState']:
    #     print(PD.data[['guid',col]])
    #     print('original dataset shape:', PD.data.shape)
    #     pd_cb1 = PD.clean_by(col)
    #     print(pd_cb1[['guid',col]])
    #     print('cleaned dataset shape:', pd_cb1.shape)
    
    # print('#'*50)
    # # test2: frequency
    # PD = Patent_Descriptive(subset)
    # PD.reformat()
    # pd_cb1 = PD.clean_by('inventorState')
    # is_freq = PD.frequency(pd_cb1, 'inventorState')
    
    # print('#'*50)
    # # test3: freq_by_group
    # PD = Patent_Descriptive(subset)
    # PD.reformat()
    # pdis = PD.clean_by('inventorState')
    # PD.data = pdis
    # pdisin = PD.clean_by('inventorsName')
    # PD.freq_by_group(pdisin, group = 'inventorState', target = 'inventorsName', graph = True)
    
    # test4: separate_category
    # PD = Patent_Descriptive(subset)
    # PD.reformat()
    # pd_sc = PD.separate_category(PD.data)
    # print(pd_sc.head())
    
    # test5: dummy_by_time
    # PD = Patent_Descriptive(subset)
    # PD.reformat()
    # dt0 = PD.dummy_by_time(PD.data, 'datePublished', '2006-06-01')
    # print(dt0.head())
    # dt_freq = PD.frequency(dt0, 'dummy')
