import pandas as pd
import requests
import time
import platform
import os


class TextExtract:
    def __init__(self):
        # initial variables to pull the urls
        self.id_cname = None
        self.df_task = None
        self.failed_list = []
        
        self.system = platform.system()
        self.headers_mac = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        # TODO: add windows headers
        self.headers_windows = None
        
        # Initial variables to pull titles; authors; date; city
        self.api_key = None
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.raw_response = []
        self.refined_response = []
        self.failed_list = []
        
        
    def load_df(self, id_path, id_cname='guid', url_path):
        '''
        To load the dataset to the TextExtract Object,
        
        Parameters:
            id_path (str): the path to the csv file that contains the missing id
            id_cname (str): the column name of the id in the id_path
            url_path (str): the path to the csv file that contains the url
        '''
        self.id_cname = id_cname
        df_missing = pd.read_csv(id_path)
        df_missing_id = df_missing[id_cname]
        df_url = pd.read_csv(url_path)
        df_url.columns = [id_cname, 'url']
        self.df_task = pd.merge(df_missing_id, df_url, on=id_cname, how='left') 
        
    def preperation(self):
        # Select a header based on the system
        if self.system == 'Darwin':
            headers = self.headers_mac
        elif self.system == 'Windows':
            headers = self.headers_windows
            
        # Create a folder to store the images if not exist
        if not os.path.exists("images"):
            os.makedirs("images")
            print(f"The directory {folder_path} was created.")
    
    def download_img(self, start_index=0, end_index=len(self.df_task), t_wait=0.5):
        '''
        To download the images from the urls in the df_task
        
        Parameters:
            start_index (int): the index of the first row to download
            end_index (int): the index of the last row to download
            t_wait (float): the time to wait between each download
        '''
        
        self.preperation()
        try:
            for i in range(start_index, end_index):
                curr_id = self.df_task.loc[i, self.id_cname]
                curr_i = i
                img_url = self.df_task.loc[i, 'url']
            
                response = requests.get(img_url, headers=headers)
                
                if response.status_code == 200:
                    file_path = "images/" + str(i) + ".tif"
            
                    # Open the file in binary write mode and save the image
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
            
                    print(f"Image downloaded successfully and saved to {file_path}")
                    time.sleep(t_wait)
                else:
                    print(f"Failed to download the image. Status code: {response.status_code}")
                    self.failed_list.append(i)
                    break
        except:
            print(self.failed_list)
        print("Done!")
        print("Failed list:", self.failed_list)

    def get_info(self, start_index=0, end_index):
        