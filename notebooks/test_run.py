import sys
import os
import pandas as pd

notebook_dir = os.path.dirname(os.path.abspath("__file__"))
modules_dir = os.path.join(os.path.dirname(notebook_dir), 'modules')

if modules_dir not in sys.path:
    sys.path.append(modules_dir)

from keyword_analysis import Keyword_Analysis
from patent_descriptive import Patent_Descriptive

# import dataset
pd_data = pd.read_csv('../data/raw/patents.csv')
# merge the dataset
# create a Patent_Descriptive object 
pdt1 = Patent_Descriptive(data = pd_data)
# reformat the dataset
pdt1.reformat()

assignee_data = pdt1.clean_by(pdt1.data, 'assigneeName')
assignee_data = pdt1.dummy_by_time(data = assignee_data, column = 'datePublished', cutoff = '2000-01-01', dummy = 'dummy')
assignee_2000s = assignee_data.loc[assignee_data['dummy'] == 0]
print(assignee_2000s)