# Patent Analysis

This is a demostration of the `Keyword_Analysis` and `Patent_Descriptive` classes. `Keyword_Analysis` does keyword analysis for patents in the patent dataset, and `Patent_Descriptive` does descriptive analysis. 

## Keyword_Analysis
`Keyword_Analysis` has 6 attributes and 2 functions for users to input and use:
### Attributes: 
- `data`: The data set to analyze. 
- `catch_word`: A list of words that the users want to check frequency with. By default, catch_word is `["safe", "safer","safety", "safely", "secure", "security", "securely", "securer", "secured","secures"]`. 
- `column`: The column of the text. By default, column is `descriptionHtml`. 
- `identifier`: The unique identifier column. By default, identifier is `guid`. 
- `keywords`: A dictionary of `guid: keywords` pairs. Initialized as empty and can be filled in with `get_keywords` method. 
- `num_keywords`: The number of keywords to extract from the text. By default, num_keywords is 15. 

### Methods:
- `get_keywords`: Get the keywords from the dataset
        
    - output: pd.DataFrame. The dataframe with the keywords column. 
- `get_word_count`: Get the frequency of catch words or keywords in the dataset. A word or phrase is allowed up to length of 3. 
    
    input: 

    - catch_word (bool): whether to count the frequency of catch words. Default is True. 
    
    - keyword (bool): whether to count the frequency of keywords. Default is False. 
    
    output: 
    
    - pd.DataFrame. The dataframe with the separate columns of catch word frequencies, and a keyword column filled with a dictionary. The dictionary in the keyword column is the frequency of keywords. 

## Patent_Descriptive
Python version of the `patent` package from R.

### Functions
- `reformat`: Reformat the dataset to correct data type. Should be run **before** any other functions. 

    input: 

    - data (pd.DataFrame): data to clean

    output: 

    - pd.DataFrame: The cleaned dataset.

- `clean_by`: Clean the dataset based on a column.
    This function cleans the dataset based on the columns about demographic data, including: inventorState, assigneeState, inventorName, assigneeName, inventorCity, and assigneeCity. If the column is inventorState or assigneeState, it will separate the column into multiple rows, clean the duplicates, and other countries.
        
    input:

    - data (pd.DataFrame): data to clean

    - column (str): The name of the column to clean. It can be inventorState or assigneeState.
        
    output:
            
    - pd.DataFrame: The cleaned dataset. Usually, it has more rows than the original dataset.

- `frequency`: Generate a frequency table for a column. Come with a graph. If the column is `keywords`, it will generate a frequency table for the keywords.

    input:

    - data (pd.DataFrame): The dataset to analyze.
    - column (str): The name of the column to analyze.
    - graph (bool): Whether to generate a bar plot. Default is True.
    - num (int): The top n values to display in the plot. Default is 5.
    - rotation (int): The rotation of the x-axis labels in the plot. Default is 45.
    - descending (bool): Whether to sort the frequency table in descending order Default is True.
    - figsize (tuple): The size of the plot. Default is (10, 6).
    - color (str): The color of the bars in the plot. Default is 'hotpink'.

    output:
    - pd.DataFrame: The frequency table for the column.

- `freq_by_group`: Draw the frequency distribution of a target variable by a group variable. Default draws bar plots.
    
    input:
    - data (pd.DataFrame): The dataset to analyze.
    - group (str): The name of the column to group by.
    - target (str): The name of the column to analyze.
    - graph (bool): Whether to generate a bar plot. Default is True.
    - rotation (int): The rotation of the x-axis labels in the plot. Default is 45.
    - num (int): The top n values to display in the plot. Default is 5.
    - figsize (tuple): The size of the plot. Default is (10, 6).
    - color (str): The color of the bars in the plot. Default is `tomato`.
    - descending (bool): Whether to sort the frequency table in descending order. Default is True.

    output: 
    - list. A list of frequency tables for each group.

- `separate_category`: Separate the `cpcInventiveFlattened` column into multiple columns and rows.

    input: 
    - data (pd.DataFrame): The dataset to separate.

    output:
    - pd.DataFrame: The dataset with `cpcInventiveFlattened` separated into multiple columns and rows.

- `dummy_by_time`: Create the dummy code for a column by time. Time before the cutoff is coded as 1, and time after the cutoff is coded as 0.

    input:
    - data (pd.DataFrame): The dataset to use. 
    - column (str): The name of the column to create the dummy variable for.
    - cutoff (str): The cutoff time to create the dummy variable.
    - dummy (str): The name of the dummy variable. Default is 'dummy'.
    
    output:
    - pd.DataFrame: The dataset with the dummy variable.

- `first_appear`: Generate a line plot of the first appearance of target column.

    input:
    - data (pd.DataFrame): The dataset to analyze.
    - target (str): The name of the column to analyze.
    - graph (bool): Whether to generate a bar plot. Default is True.
    - figsize (tuple): The size of the plot. Default is (10, 6).
    - color (str): The color of the bars in the plot. Default is 'lightgreen'.

    output:
    - pd.DataFrame: The first appearance of target column.

## Sample Use

1. Import the dataset and create a `Keyword_Analysis` object. 
```
# import packages
import pandas as pd
from keyword_analysis import Keyword_Analysis
from patent_descriptive import * 

# import the dataset
sample_abstract = pd.read_csv('./data/raw/sample_abstract.csv')

# create an object
KA = Keyword_Analysis(data=dataset, num_keywords = 10)
```
2. Create a dataset with a column of keywords. 
```
keyword = KA.get_keywords()
print(keyword.head())
```
3. Check the frequency of catch words and keywords
```
fck = KA.get_word_count(catch_word = True, keyword = True)
print(fck.head())
```
4. Check the overall frequency of keywords 
```
# import dataset
pd_data = pd.read_csv('/Users/liusimin/Desktop/Gun Safety/papers/all_patents3.csv')
# merge the dataset
data = pd.merge(keyword, pd_data, on='guid', how='left')

# reformat the dataset
data = reformat(data)
# check frequency
kf = frequency(data = data, column = 'keyword', num = 30)
```
From the frequency plot of `kf`, while keyword is the x axis, frequency is the y axis, the plot shows that `barrel`, `target`, and `trigger` are the top 3 words of gun components that have been mentioned most frequently for all F41 firearm related patents over time.   

5. Check the keyword frequency by decades
```
data['year'] = data['datePublished'].dt.year
data['decade'] = (data['year'] // 10) * 10
kfd = freq_by_group(data = data, group = 'decade', target = 'keyword', num = 20)
```
`kfd` is a list of frequency tables of keywords by decades. From 1830s to 1890s, the recurring appearance of terms like "barrel", "breech", "trigger", and "hammer" across multiple decades points to these as areas of significant advancement and focus within the field of firearms, reflecting the technological challenges and demands of the times. 

Starting from 20 century to mid 20 century, "barrels", "breech mechanisms", and "trigger" suggests that innovations were focused on refining the efficiency and functionality of these elements. The appearance of terms like "bolt" and "breach block" in the later decades could indicate specific advancements and a possible shift towards more sophisticated firearm technology during this period.

The keywords from the 1960s to the 1990s depict a steady emphasis on the primary components of firearms, such as barrels and triggers, while also hinting at increased attention to precision and targeting, as seen with the term "target." The appearance of "missile" in the 1960s could indicate an era-specific interest in missile technology or larger caliber projectiles. Throughout these decades, there seems to be a trend towards refining the fundamental aspects of firearms while also incorporating advancements that enhance the weapon's precision and modular capabilities.

Entering the 21 century, there is a noticeable shift from specific components like "barrel" and "trigger" in earlier decades to more holistic terms such as "device," "system," and "embodiment." This could suggest a trend toward more complex, system-level innovations in firearms, possibly integrating electronic or digital technologies, which became increasingly prevalent in the 2000s and beyond.

Over nearly two centuries, there's been a progression from basic mechanical components to sophisticated, integrated systems in firearm technology. Earlier decades focused on the essential elements and mechanics of firearms. As time went on, there was an evident shift toward enhancing precision, usability, modularity, and integrating new technologies, reflecting broader technological advancements and changing demands in both civilian and military contexts. The 21st century shows a marked emphasis on the systemic and device-oriented nature of firearms, which may include computer-aided design and manufacturing, the incorporation of smart technologies, and advanced materials.

6. Slice the dataset based on category
```
data = separate_category(data)

# subselect all F41 patents
F41 = data.loc[(data['category'] == 'F') & (data['subcategory1'] == '41')]

# select F41A, F41C, F41G for firearms
F41A = F41.loc[F41['subcategory2'] == 'A']
F41C = F41.loc[F41['subcategory2'] == 'C']
F41G = F41.loc[F41['subcategory2'] == 'G']
```

7. Analyze subcategories
```
# subcategory2 frequency for F41
F41_n = frequency(data = F41, column = 'subcategory2', num = len(F41['subcategory2'].unique()))

# subcategory3 frequency for F41A, F41C, F41G
F41A_n = frequency(data = F41A, column = 'subcategory3', rotation =0, num = len(F41A['subcategory3'].unique()))

F41C_n = frequency(data = F41C, column = 'subcategory3', rotation =0, num = len(F41C['subcategory3'].unique()))

F41G_n = frequency(data = F41G, column = 'subcategory3', rotation =0, num = len(F41G['subcategory3'].unique()))
```
Reading F41_n, A, G, H are the most prolific category under F41. F41A covers operational characteristics and details that are shared between small arms and larger artillery, such as cannons, including their mountings. F41G is dedicated to the sighting systems of weapons and their aiming methodologies. F41H relates to protective gear like armor, armored turrets, and vehicles, as well as general offensive and defensive implements, including camouflage.

From F41A_n, subcategories 9, 19, 17 are most under F41A. 
F41A09 pertains to the mechanisms for ammunition supply and loading, F41A19 deals with the mechanisms involved in the discharge or actuation of firearms, and F41A17 focuses on the safety features of firearms.

From F41C_n, subcategories 33, 23, 27 are most under F41C. 
F41C33 relates to methods and apparatus for wearing or transporting small firearms. F41C23 encompasses handguns such as pistols and revolvers. F41C27 is concerned with supplementary equipment for firearms.

From F41G_n, subcategories 1, 7, 3 are most under F41G. 
F41G01 involves devices used for aiming or aligning firearms to their targets. F41G07 deals with the systems that guide the trajectory of self-propelled missiles. F41G03 pertains to mechanisms or systems designed for targeting or positioning weapons.

8. Check prolific inventors and states
```
# prolific states
state_data = clean_by(data, 'inventorState')
state_freq = frequency(data = state_data, column = 'inventorState', num = 20)

# prolific inventors
inventor_data = clean_by(data, 'inventorsName')
inventor_freq = frequency(data = inventor_data, column = 'inventorsName', num = 20)
```
CA, WI, and VA stand out as the states with the highest number of firearm patents.

Jesse Gander, Mathew A. McPherson, and Timothy W. Markison have been identified as the most productive inventors in the realm of firearm patents over the years.

9. Check assignees after 2000.01.01
```
assignee_data = clean_by(data, 'assigneeName')
assignee_data = dummy_by_time(data = assignee_data, column = 'datePublished', cutoff = '2000-01-01', dummy = 'dummy')
assignee_2000s = assignee_data.loc[assignee_data['dummy'] == 0]

assignee_2000s_freq = frequency(column = 'assigneeName', data = assignee_2000s)
```
Top assignees after 2000 are Raytheon Company, and the United States of America as represented by the Secretary of the Navy, and Oshkosh Defense, LLC. 

10. Observe the evolution of innovation
```
fa = first_appear(data = F41, target = 'cpcInventiveFlattened', graph = True, figsize = (10, 6), color = 'tomato')
```
Each point on the line indicates the number of new categories that were introduced in a particular year. There is a particularly notable spike around 1925 where the number of patents jumps to its maximum on the chart, exceeding 40 patents in that year.