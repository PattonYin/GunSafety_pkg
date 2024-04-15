import unittest
import pandas as pd

from patent_data_fetcher import Fetcher
from keyword_analysis import Keyword_Analysis
from patent_descriptive import Patent_Descriptive


class TestFetcher(unittest.TestCase):
    
    def setUp(self):
        # Setup code that runs before each test method
        self.fetcher = Fetcher()

    def test_query_text_valid(self):
        # Test a valid case
        search_requirements = {
            "ids": ["US-20170067712-A9"],
            "method": "local",
            "content": "descriptions"
        }
        result = self.fetcher.query_text(search_requirements)
        self.assertIsNotNone(result)  # Replace with more specific assertions
    
    def test_query_img_valid(self):
        # Test a valid case
        # Testing by checking whether there are files in the output folder\
        ids = ["US-0441389-A", "US-0442014-A"]
        output_folder = "output_test"
        self.fetcher.query_img(ids, output_folder)
        self.assertTrue(len(os.listdir(output_folder)) > 0)
        
    def tearDown(self):
        # remove the output folder
        output_folder = "output_test"
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
            
def test_run_sm():
    dataset = pd.read_csv(r'X:\code\GunSafety_pkg\data_large\df_descriptions.csv')
    KA = Keyword_Analysis(data=dataset, num_keywords = 10)
    keyword = KA.get_keywords()
    print(keyword.head())
    fck = KA.get_word_count(catch_word = True, keyword = True)
    print(fck.head())
    # import dataset
    pd_data = pd.read_csv(r'X:\code\GunSafety_pkg\data_large\clean_data2.csv')
    print(2)
    # merge the dataset
    data = pd.merge(keyword, pd_data, on='guid', how='left')
    # create a Patent_Descriptive object 
    pdt1 = Patent_Descriptive(data = data)
    # reformat the dataset
    pdt1.reformat()
    print(3)
    # check frequency
    kf = pdt1.frequency(data = pdt1.data, column = 'keywords', n = 30)
    pdt1.data['year'] = pdt1.data['datePublished'].dt.year
    pdt1.data['decade'] = (pdt1.data['year'] // 10) * 10
    kfd = pdt1.freq_by_group(data = pdt1.data, group = 'decade', target = 'keyword', num = 20)
    pdt1.data = pdt1.separate_category(pdt1.data)
    print(4)

    # subselect all F41 patents
    F41 = pdt1.data.loc[(pdt1.data['category'] == 'F') & (pdt1.data['subcategory1'] == '41')]

    # select F41A, F41C, F41G for firearms
    F41A = F41.loc[F41['subcategory2'] == 'A']
    F41C = F41.loc[F41['subcategory2'] == 'C']
    F41G = F41.loc[F41['subcategory2'] == 'G']

    print(5)
    # prolific states
    state_data = pdt1.clean_by(pdt1.data, 'inventorState')
    state_freq = pdt1.frequency(data = state_data, column = 'inventorState', num = 20)

    # prolific inventors
    inventor_data = pdt1.clean_by(pdt1.data, 'inventorsName')
    inventor_freq = pdt1.frequency(data = inventor_data, column = 'inventorsName', num = 20)
    
    assignee_data = pdt1.clean_by(pdt1.data, 'assigneeName')
    assignee_data = pdt1.dummy_by_time(data = assignee_data, column = 'datePublished', cutoff = '2000-01-01', dummy = 'dummy')
    assignee_2000s = assignee_data.loc[assignee_data['dummy'] == 0]

    assignee_2000s_freq = pdt1.frequency(column = 'assigneeName', data = assignee_2000s)
    
if __name__ == '__main__':
    test_run_sm()