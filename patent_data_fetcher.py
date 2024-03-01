import pandas as pd
import numpy as np

from utils.fetcher_helper import query_df
from utils.fetcher_helper import query_img


class Fetcher:
    def __init__(self):
        self.id_index_df = pd.read_csv("data/extract_3k.csv")
        self.df_basics = pd.read_csv("data/df_basics.csv")
        self.df_classifications = pd.read_csv("data/patent_classification.csv")
        self.edge_list = pd.read_csv("data/edge_list.csv")

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
    
    def get_basics(self, ids):
        """
        With the ids given, return the basic information of the patent. If no ids are given, return the whole dataframe.
        
        Args:
            ids (list) : list of ids to subset
            
        Returns:
            data (pd.DataFrame) : the abstract of the patent or bulk of patents
        """
        
        if not ids:
            return self.df_basics
        
        data = self.df_basics[self.df_basics['guid'].isin(ids)]

        return data
    
    def query_img(self, ids, output_folder):
        """
        With searching requirements given, copy the images to the output folder.
        
        Args:
            ids (list) : list of patent ids
        """
        # Subset the ids from the index dataframe and make it list
        index_list = self.id_index_df[self.id_index_df['guid'].isin(ids)]['index'].to_list()
        print(index_list)
        query_img(index_list, output_folder)
        
    def get_citations(self, patent_id):
        """
        With patent id given, return the list of cited patent ids.
        
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

    def subset_patents(self, column_name, requirements):
        """
        Subset the patents based on the column name and range.
        The options are "datePublished", "inventorsName", "inventorCity", "inventorState", "assigneeName", "assigneeCity", "assigneeState", "cpcInventiveFlattened".
        
        Args:
            column_name (str) : name of the column e.g. "datePublished" or "inventorsName"
            range (tuple) or names (list): range of the column or list of the names e.g. ("2010-01-01", "2011-01-01") or ["Richard L.", "Marshfield"]
            
        Returns:
            df_subset (dataframe) : the subset of the patents
        """
        if column_name not in self.method_map:
            raise ValueError(f"Column name {column_name} is not in the options.")
        
        subset_method = self.method_map[column_name]
        return subset_method(column_name, requirements)
        
    def _subset_by_date(self, column_name, requirements, df=None):
        """
        Subset the patents based on the datePublished column.
        
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
        """
        Subset the patents based on the column name and list.
        
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

    def filter_patents_by_cpc(self, cpc_codes):
        """
        Filter the patent ids by the cpc codes.
        
        Args:
            cpc_codes (list of list) : list of cpc codes e.g. [["F41","A","3","58"], ["F41", "C", "3", "14"]]
        
        Returns:
            ids (list) : the ids of the patents subsetted
        """
        ids = []
        for cpc_list in cpc_codes:
            df_to_subset = self.df_classifications
            for index, cpc in enumerate(cpc_list):
                if index > 1:
                    cpc = np.float64(cpc)
                df_to_subset = df_to_subset[df_to_subset[f"{index}"] == cpc]
            ids.extend(df_to_subset['4'].to_list())
        
        return ids
                

if __name__ == "__main__":
    fetcher = Fetcher()
    ids = ["US-20170067712-A9"]
    print(fetcher.get_basics(ids))
    
    ids = ["US-0441389-A", "US-0442014-A"]
    output_folder = "output_test"
    fetcher.query_img(ids, output_folder)
    
    print(fetcher.get_citations("US-10921097-B1"))
    print(fetcher.get_cited_by("US-5992291-A"))
    
    requirements = ("2010-01-01", "2011-01-01")
    print(len(fetcher.subset_patents("datePublished", requirements)))
    
    requirements = ["Richard L.", "Marshfield"] 
    print(len(fetcher.subset_patents("inventorsName", requirements)))
    
    requirements = ["CT", "MA"]
    print(len(fetcher.subset_patents("inventorState", requirements)))
    
    requirements = [["F41","A","3"], ["F41", "C", "3", "14"]]
    print(len(fetcher.filter_patents_by_cpc(requirements)))