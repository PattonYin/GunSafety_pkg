import pandas as pd

from utils.fetcher_helper import query_df
from utils.fetcher_helper import query_img


class Fetcher:
    def __init__(self):
        self.id_index_df = pd.read_csv("data/extract_3k.csv")
    
    def query_text(self, search_requirements):
        """With searching requirements given, return the abstract of the patent.
        
        Args:
            search_requirements (dict) : requirements for patent search
            
        Returns:
            _TBD_ : the abstract of the patent or bulk of patents
        """
        ids = search_requirements["ids"]
        method = search_requirements["method"]
        content = search_requirements["content"]
        df_name = f"df_{content}"
        
        if method == "local":
            data = query_df(df_name, ids)
        else:
            data = "not implemented yet."
        return data
    
    def query_img(self, ids, output_folder):
        """With searching requirements given, return the image of the patent.
        
        Args:
            ids (list) : list of patent ids
            
        """
        # Subset the ids from the index dataframe and make it list
        index_list = self.id_index_df[self.id_index_df['guid'].isin(ids)]['index'].to_list()
        print(index_list)
        query_img(index_list, output_folder)
        
    

if __name__ == "__main__":
    fetcher = Fetcher()
    search_requirements = {
        "ids": ["US-20170067712-A9"],
        "method": "local",
        "content": "descriptions"
    }
    print(fetcher.query_text(search_requirements))
    
    ids = ["US-0441389-A", "US-0442014-A"]
    output_folder = "output_test"
    fetcher.query_img(ids, output_folder)
    