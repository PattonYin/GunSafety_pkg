import pandas as pd
import requests
import time
import platform
import os
from tqdm import trange
from utils.vision_img import API_calling

class TextExtract:
    def __init__(self):
        # initial variables to pull the urls
        self.id_cname = None
        self.df_task = None
        self.failed_list = []
        self.id_todo = None
        self.refined_csv = pd.read_csv('data/refined.csv') if os.path.exists("data/refined.csv") else None
        
        self.system = platform.system()
        self.headers_mac = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        # TODO: add windows headers
        self.headers_windows = None
        
        # Initial variables to pull titles; authors; date; city
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.GPT = API_calling()
        self.df_extract = pd.read_csv("data/extract_3k.csv")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.raw_response = []
        self.refined_response = []
        self.failed_list_api = []
        
        
    def load_df(self, id_path, url_path, id_cname='guid'):
        '''
        To load the dataset to the TextExtract Object,
        
        Parameters:
            id_path (str): the path to the csv file that contains the missing id
            url_path (str): the path to the csv file that contains the url
            id_cname (str): the column name of the id in the id_path (optional, default='guid')           
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
            print(f"The directory 'images' was created.")
    
    def download_img(self, start_index=0, end_index=None, t_wait=0.5):
        '''
        To download the images from the urls in the df_task
        
        Parameters:
            start_index (int): the index of the first row to download
            end_index (int): the index of the last row to download
            t_wait (float): the time to wait between each download
        '''
        if end_index is None:
            end_index = len(self.df_task)
        
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

    def get_index_df(self, id_list):
        # Subset the df_extract to only the ids that are in the id_list, and only the first two columns (index and guid kept)
        df_todo = self.df_extract[self.df_extract['guid'].isin(id_list)]
        # get the index list
        index_df = df_todo[['index', 'guid']]
        print(index_df.head())
        return index_df

    def get_info(self, id_list=None, start_index=0):
        if id_list is None:
            id_list = self.id_list[start_index:]

        try:
            index_df = self.get_index_df(id_list)
            
            curr_list = []
            id_pt = index_df['guid'].iloc[0]
            for i in trange(1, len(index_df)):
                if index_df['guid'].iloc[i] != id_pt:
                    print("curr_id: ", index_df['guid'].iloc[i])
                    print("prev_id: ", id_pt)
                    # Get all images for one patent
                    image_path_list = []
                    for x in curr_list:
                        image_path_list.append("images/" + str(x) + '.tif')
                    # Api Calling
                    response = self.GPT.get_info(image_path_list, self.headers)
                    
                    # Save Data
                    self.raw_response.append([id_pt, response])
                    try:
                        r = response['choices'][0]['message']['content'] # refine the response
                        self.refined_response.append([id_pt, r]) # append the refined response
                        print("response: \n", r)
                    except:
                        print(response)
                        print("KeyError occured.", self.failed_list_api)
                        self.failed_list_api.append(index_df['guid'].iloc[i])
                        self.refined_response.append([id_pt, "KeyError"]) # append the refined response

                    # Reset the variables
                    curr_list = []
                    id_pt = index_df['guid'].iloc[i]
                    curr_i = i
                else:
                    print("curr_id: ", index_df['guid'].iloc[i])
                    print("appending")
                    curr_list.append(index_df['index'].iloc[i])
                    continue
            print("Done!")
            print("Failed list:", self.failed_list_api)
            self.save()
        except KeyboardInterrupt:
            print("interrupted.")
            print("Failed list:", self.failed_list_api)
            self.save()
        
    def save(self):
        print("Saving...")
        print("failed ids: ", self.failed_list_api)
        if not os.path.exists("data"):
            os.makedirs("data")
            print(f"The directory 'data' was created.")

        # Load if already exists, otherwise create a new one
        raw_df_new = pd.DataFrame(self.raw_response, columns=['id', 'response'])
        refined_df_new = pd.DataFrame(self.refined_response, columns=['id', 'response'])
        
        
        if not os.path.exists("data/raw.csv"):
            print("creating new raw.csv...")
            raw_df_new.to_csv("data/raw.csv", index=False)
            print(f"raw.csv was saved.")
        else:
            print("loading prev raw.csv...")
            raw_df = pd.read_csv("data/raw.csv")
            raw_df_out = pd.concat([raw_df, raw_df_new], ignore_index=True)
            raw_df_out.to_csv("data/raw.csv", index=False)
        
        if not os.path.exists("data/refined.csv"):
            print("creating new refined.csv...")
            refined_df_new.to_csv("data/refined.csv", index=False)
            print(f"refined.csv was saved.")
        else:
            print("loading prev refined.csv...")
            refined_df = pd.read_csv("data/refined.csv")
            refined_df_out = pd.concat([refined_df, refined_df_new], ignore_index=True)
            refined_df_out.to_csv("data/refined.csv", index=False)

    def unscraped(self):
        id_list_all = self.df_extract.guid.to_list()
        id_done = self.refined_csv.id.to_list()
        self.id_todo = [item for item in id_list_all if item not in id_done]
        print(len(self.id_todo))
        
    def clean_up_error(self):
        refined = pd.read_csv(r'data\refined.csv')
        refined_new = refined[refined['content'] != 'KeyError']
        refined_new.to_csv('data/refined.csv', index=False)

    def look_up_raw(self):
        raw = pd.read_csv('data/raw.csv')
        # From the id_todo, get the corresponding response in the raw.csv
        raw_info = raw[raw['id'].isin(self.id_todo)]
        # For the response column, Get rid of the NaN, and any cell with string 'error' in it
        raw_info = raw_info.dropna()
        raw_info = raw_info[~raw_info['response'].str.contains("error")]
        print(len(raw_info))

if __name__ == "__main__":
    extractor = TextExtract()
    # extractor.unscraped()
    # print(extractor.id_todo)
    extractor.get_info()    
    failed_list = ['US-0561954-A', 'US-0561954-A', 'US-0561954-A', 'US-0561954-A', 'US-0561954-A']
    
