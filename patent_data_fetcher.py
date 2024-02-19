import pandas as pd

from utils.fetcher_helper import query_df
from utils.fetcher_helper import query_img


class Fetcher:
    def __init__(self):
        self.id_index_df = pd.read_csv("data/extract_3k.csv")
        self.edge_list = pd.read_csv("data/edge_list.csv")
    
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
        
    def get_citations(self, patent_id):
        """With patent id given, return the list of cited patent ids.
        
        Args:
            patent_id (str) : patent id
            
        Returns:
            list : list of cited patent ids
        """
        return self.edge_list[self.edge_list['child'] == patent_id]['parent'].to_list()
    
    def get_cited_by(self, patent_id):
        """With patent id given, return the list of patents that cited the patent.
        
        Args:
            patent_id (str) : patent id
            
        Returns:
            list : list of patents that cited the patent
        """
        return self.edge_list[self.edge_list['parent'] == patent_id]['child'].to_list()
        
    

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
    
    print(fetcher.get_citations("US-10921097-B1"))
    print(fetcher.get_cited_by("US-5992291-A"))
    