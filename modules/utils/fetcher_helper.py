import pandas as pd
import os
from PIL import Image

def query_df(df_name, path=None):
    """
    Query the dataframe and return the dataframe.
    
    Args:
        df_name (str): the name of the dataframe
        
    Returns:
        DataFrame: the dataframe
    """

        
    return None

def query_img(index_list, output_folder, path=None):
    """
    Query the image from the index list and save it to the output folder.
    
    Args:
        index_list (list): list of index
        output_folder (str): the folder to save the images
    """
    # Fetches local images at this moment
    if path is None: path = "data_large/images/"
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"The directory {output_folder} was created.")
    
    for index in index_list:
        img_path = f"{path}{index}.tif"
        img = Image.open(img_path)
        img.save(f"{output_folder}/{index}.png")
        print(f"{index}.png was saved.")
    