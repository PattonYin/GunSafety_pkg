import pandas as pd

from utils.fetcher_helper import query_df
from utils.fetcher_helper import query_img


class Fetcher:
    def __init__(self):
        self.id_index_df = pd.read_csv("data/extract_3k.csv")
        self.df_basics = query_df("df_basics", [])
        self.method_map = {
            "datePublished": self._subset_by_date,
            "inventorsName": self._subset_with_list,
            "inventorCity": self._subset_with_list, 
            "inventorState": self._subset_with_list,
            "assigneeName": self._subset_with_list,
            "assigneeCity": self._subset_with_list,
            "assigneeState": self._subset_with_list,
            "cpcInventiveFlattened": self._subset_with_list
        }
    
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
        
    def subset_patents(self, column_name, requirements):
        """Subset the patents based on the column name and range.
        
        Args:
            column_name (str) : name of the column
            range (tuple) : range of the column
            
        Returns:
            df_subset (dataframe) : the subset of the patents
        """
        if column_name not in self.method_map:
            raise ValueError(f"Column name {column_name} is not in the options.")
        
        subset_method = self.method_map[column_name]
        return subset_method(column_name, requirements)
        
    def _subset_by_date(self, column_name, requirements, df=None):
        """Subset the patents based on the datePublished column.
        
        Args:
            requirements (tuple of time) : range of the datePublished e.g. ("2010-01-01", "2011-01-01")
            
        Returns:
            df_subset (dataframe) : the subset of the patents
        """
        start, end = requirements
        
        if df is None:
            df = self.df_basics
        
        df["datePublished"] = pd.to_datetime(df["datePublished"].str[:10])
        df_subset = df[(df['datePublished'] >= start) & (df['datePublished'] <= end)]
        return df_subset
    
    def _subset_with_list(self, column_name, requirements, df=None):
        """Subset the patents based on the column name and list.
        
        Args:
            column_name (str) : name of the column e.g. "inventorsName" or "inventorState"
            requirements (list) : list of the information to subset e.g. ["Richard L.", "Marshfield"] or ["CT", "MA"]
            
        Returns:
            df_subset (dataframe) : the subset of the patents
        """
        
        if df is None:
            df = self.df_basics
        
        if column_name not in self.method_map:
            raise ValueError(f"Column name {column_name} is not in the options.")
        
        df_subset = df[df[column_name].apply(lambda x: any(item in str(x) for item in requirements))] 
        
        return df_subset

if __name__ == "__main__":
    fetcher = Fetcher()
    # search_requirements = {
    #     "ids": ["US-20170067712-A9"],
    #     "method": "local",
    #     "content": "descriptions"
    # }
    # print(fetcher.query_text(search_requirements))
    
    # ids = ["US-0441389-A", "US-0442014-A"]
    # output_folder = "output_test"
    # fetcher.query_img(ids, output_folder)
    
    requirements = ("2010-01-01", "2011-01-01")
    print(len(fetcher.subset_patents("datePublished", requirements)))
    
    requirements = ["Richard L.", "Marshfield"] 
    print(len(fetcher.subset_patents("inventorsName", requirements)))
    
    requirements = ["CT", "MA"]
    print(len(fetcher.subset_patents("inventorState", requirements)))
    
