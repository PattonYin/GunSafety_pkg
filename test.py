import unittest

from patent_data_fetcher import Fetcher

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