import pandas as pd
import os
import numpy as np

df_basics = pd.read_csv("../data/raw/df_basics.csv")
edge_list = pd.read_csv("../data/raw/edge_list.csv")
df_classifications = pd.read_csv("../data/raw/patent_classification.csv")

method_map = {}

def get_patents(ids=None):
    """subset the basic dataframe with patents with the given ids. Returns the whole dataframe if no ids are given.

    Args:
        ids (str list, optional): list of Ids. Defaults to None.

    Returns:
        pd.dataframe: dataframe subsetted
    """
    if not ids:
        return df_basics
    
    data = df_basics[df_basics['guid'].isin(ids)]

    return data

def get_citations(patent_id):
    """
    With patent id given, return the list of cited patent ids.
    
    Args:
        patent_id (str) : patent id
        
    Returns:
        list : list of cited patent ids
    """
    
    citations = edge_list[edge_list['child'] == patent_id]['parent'].to_list()
    if len(citations) == 0:
        print(f"Citation not available.")
    return citations

def get_cited_by(patent_id):
    """With patent id given, return the list of patents that cited the patent.
    
    Args:
        patent_id (str) : patent id
        
    Returns:
        list : list of patents that cited the patent
    """    
    
    citations = edge_list[edge_list['parent'] == patent_id]['child'].to_list()
    if len(citations) == 0:
        print(f"Citation not available.")
    return citations
    
def subset_patents(column_name, requirements):
    """
    Subset the patents based on the column name and range.
    The options are "datePublished", "inventorsName", "inventorCity", "inventorState", "assigneeName", "assigneeCity", "assigneeState", "cpcInventiveFlattened".
    
    Args:
        column_name (str) : name of the column e.g. "datePublished" or "inventorsName"
        range (tuple) or names (list): range of the column or list of the names e.g. ("2010-01-01", "2011-01-01") or ["Richard L.", "Marshfield"]
        
    Returns:
        df_subset (dataframe) : the subset of the patents
    """
    if column_name not in method_map:
        raise ValueError(f"Column name {column_name} is not in the options.")
    
    subset_method = method_map[column_name]
    return subset_method(column_name, requirements)


def _subset_by_date(column_name, requirements, df=None):
    """
    Subset the patents based on the datePublished column.
    
    Args:
        requirements (tuple of time) : range of the datePublished e.g. ("2010-01-01", "2011-01-01")
        
    Returns:
        df_subset (dataframe) : the subset of the patents
    """
    start, end = requirements
    
    if df is None:
        df = df_basics.copy()
    df["datePublished"] = df["datePublished"].astype(str)
    df["datePublished"] = pd.to_datetime(df["datePublished"].str[:10])
    df_subset = df[(df['datePublished'] >= start) & (df['datePublished'] <= end)]
    return df_subset

def _subset_with_list(column_name, requirements, df=None):
    """
    Subset the patents based on the column name and list.
    
    Args:
        column_name (str) : name of the column e.g. "inventorsName" or "inventorState"
        requirements (list) : list of the information to subset e.g. ["Richard L.", "Marshfield"] or ["CT", "MA"]
        
    Returns:
        df_subset (dataframe) : the subset of the patents
    """
    
    if df is None:
        df = df_basics.copy()
    
    if column_name not in method_map:
        raise ValueError(f"Column name {column_name} is not in the options.")
    
    df_subset = df[df[column_name].apply(lambda x: any(item in str(x) for item in requirements))] 
    
    return df_subset

def subset_patents_by_cpc(cpc_codes):
    """
    Filter the patent ids by the cpc codes.
    
    Args:
        cpc_codes (list of list) : list of cpc codes e.g. [["F41","A","3","58"], ["F41", "C", "3", "14"]]
    
    Returns:
        ids (list) : the ids of the patents subsetted
    """
    ids = []
    for cpc_list in cpc_codes:
        df_to_subset = df_classifications.copy()
        for index, cpc in enumerate(cpc_list):
            if index > 1:
                cpc = np.float64(cpc)
            df_to_subset = df_to_subset[df_to_subset[f"{index}"] == cpc]
        ids.extend(df_to_subset['4'].to_list())
    
    return ids

method_map = {
    "datePublished": _subset_by_date,
    "inventorsName": _subset_with_list,
    "inventorCity": _subset_with_list, 
    "inventorState": _subset_with_list,
    "assigneeName": _subset_with_list,
    "assigneeCity": _subset_with_list,
    "assigneeState": _subset_with_list,
    "cpcInventiveFlattened": _subset_with_list
}

if __name__ == "__main__":
    ids = ["US-20170067712-A9"]
    print(get_patents(ids))
    print("-------------------")
    
    print(get_citations("US-10921097-B1"))
    print(get_cited_by("US-5992291-A"))
    print("-------------------")
    
    requirements = ("1950-01-01", "2015-12-31")
    print(len(subset_patents("datePublished", requirements)))
    # export_to_temp(subset_patents("datePublished", requirements), "1950-2015")
    print("-------------------")
    
    requirements = ["Richard L.", "Marshfield"] 
    print(len(subset_patents("inventorsName", requirements)))
    print("-------------------")
    
    requirements = ["CT", "MA"]
    print(len(subset_patents("inventorState", requirements)))
    print("-------------------")
    
    requirements = ["ITT Corporation"]
    print(len(subset_patents("assigneeName", requirements)))
    print(subset_patents("assigneeName", requirements))
    print("-------------------")
    
    requirements = [["F41","A","3"], ["F41", "C", "3", "14"]]
    print(len(subset_patents_by_cpc(requirements)))
    print("-------------------")