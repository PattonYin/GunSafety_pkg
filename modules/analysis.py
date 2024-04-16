import os
import pandas as pd
from tqdm import tqdm, trange
from datetime import datetime
import matplotlib.pyplot as plt

def check_path(path_to_data):
    if os.path.exists(path_to_data):
        return
    else:
        raise FileNotFoundError(f"{path_to_data} does not exist.\nPlease specify the path to the patent data")

def first_appear_analysis(path_to_data="data", file_path="raw/df_basics.csv"):
    # Step 1.0 - parent_date_process
    parent_date_process(path_to_data=path_to_data, file_path=file_path) 
    # 1.1 - subset_category    
    subset_category(path_to_data=path_to_data) 
    # 1.2 - join_date    
    join_date(path_to_data=path_to_data) 
    # 1.3 - first_date
    find_earliest_date(path_to_data=path_to_data)
    # 1.4 - plot_date
    plot_date(path_to_data=path_to_data)

# 1.0 - parent_date_process
def parent_date_process(path_to_data="data", file_path="raw/df_basics.csv"):
    """
    Extract the parent date of all the patents and save it to a csv file.

    Args:
        path_to_data(str, optional): Path to the directory containing the patent data. Defaults to "data".
    """
    check_path(path_to_data)
    
    # configure path variables and initialize output folder
    patents_path = os.path.join(path_to_data, file_path)
    output_folder = os.path.join(path_to_data, "intermediate/first_appear")
    os.makedirs(output_folder, exist_ok=True)
    output_path=os.path.join(path_to_data, "intermediate/first_appear/patent_date.csv")
    
    df_all_patents = pd.read_csv(patents_path, low_memory=False)
    print("csv read")
    df_out = df_all_patents[['guid', 'datePublished']]
    print("subsetted")
    df_out.to_csv(output_path, index=False)
    
# 1.1 - for each category, find the first appeared patent and the corresponding date
def subset_category(path_to_data="data"):
    """
    Subset the patents by category and save them to individual csv files.

    Args:
        path_to_data(str, optional): Path to the directory containing the patent data. Defaults to "data".
    """
    check_path(path_to_data)
    
    # configure path variables and initialize output folder
    classification_path = os.path.join(path_to_data, "raw/patent_classification.csv")
    output_path = os.path.join(path_to_data, "intermediate/first_appear/cate_subsetted")
    os.makedirs(output_path, exist_ok=True)

    df_parent_with_cate = pd.read_csv(classification_path, low_memory=False)
    print("csv read")
    groups = df_parent_with_cate.groupby(['0', '1', '2', '3'])
    for name, group in tqdm(groups, desc="subsetting patents by category"):
        group.to_csv(f'{output_path}/{name}.csv', index=False)

            
# 1.2 - for each individual csv, join with parent_date.csv to get the date of the first appeared patent
def join_date(path_to_data="data"):
    """
    Join the date of the first appeared patent to each category and save to individual csv files.

    Args:
        path_to_data(str, optional): Path to the directory containing the patent data. Defaults to "data".
    """
    check_path(path_to_data)

    # configure path variables and initialize output folder    
    data_path_01 = os.path.join(path_to_data, "intermediate/first_appear/patent_date.csv")
    data_path_02 = os.path.join(path_to_data, "intermediate/first_appear/cate_subsetted")
    output_path = os.path.join(path_to_data, "intermediate/first_appear/cate_date_joined")
    os.makedirs(output_path, exist_ok=True)

    df_patent_date = pd.read_csv(data_path_01, low_memory=False)
    for file in tqdm(os.listdir(data_path_02), desc="joining date to patents"):
        df = pd.read_csv(f'{data_path_02}/{file}', low_memory=False)
        # rename column '4' to 'guid'
        df.rename(columns={'4': 'guid'}, inplace=True)
        df_out = pd.merge(df, df_patent_date, how='left', on='guid')
        df_out.to_csv(f'{output_path}/{file}', index=False)
            
# 1.3 - for each individual csv, find the earliest date and corresponding id
def find_earliest_date(path_to_data="data"):
    """
    Find the earliest date and corresponding id for each category and save to a csv file.

    Args:
        path_to_data(str, optional): Path to the directory containing the patent data. Defaults to "data".
    """
    check_path(path_to_data)
    
    # configure path variables and initialize output folder    
    data_path_01 = os.path.join(path_to_data, "intermediate/first_appear/cate_date_joined")
    output_path = os.path.join(path_to_data, "processed/first_appeared.csv")
    
    list_pt = []
    index = 0
    for file in tqdm(os.listdir(data_path_01), desc="finding the earliest date"):
        df = pd.read_csv(f'{data_path_01}/{file}', low_memory=False)
        # modify the datePublished column, by taking only the first 10 characters (which looks like 2000-01-01), and then convert to datetime, then find the earliest date
        df['datePublished'] = df['datePublished'].astype(str)
        df['datePublished'] = pd.to_datetime(df['datePublished'].str[:10])
        earliest_date = df['datePublished'].min()
        # find the corresponding id
        earliest_id = df[df['datePublished'] == earliest_date]['guid'].values[0]
        earliest_cate_1 = str(df[df['datePublished'] == earliest_date]['0'].values[0])
        earliest_cate_2 = str(df[df['datePublished'] == earliest_date]['1'].values[0])
        earliest_cate_3 = str(int(df[df['datePublished'] == earliest_date]['2'].values[0]))
        earliest_cate_4 = str(int(df[df['datePublished'] == earliest_date]['3'].values[0]))
        earliest_cate = earliest_cate_1 + '/' + earliest_cate_2 + '/' + earliest_cate_3 + '/' + earliest_cate_4
        list_pt.append([earliest_id, earliest_date, earliest_cate])
    first_appeared = pd.DataFrame(list_pt, columns=['guid', '1st_appeared_date', 'earliest_cate'])
    first_appeared.to_csv(output_path, index=False)

# 1.4 - plot out how the patents distribute over time
def plot_date(path_to_data="data"):
    """
    Plot the distribution of the patents over time.

    Args:
        path_to_data(str, optional): Path to the directory containing the patent data. Defaults to "data".
    """
    check_path(path_to_data)

    # configure path variables and initialize output folder    
    file_path = os.path.join(path_to_data, "processed/first_appeared.csv")
    
    df = pd.read_csv(file_path, low_memory=False)
    df['1st_appeared_date'] = pd.to_datetime(df['1st_appeared_date'])
    # Extract the year from the date and Group by year and count the number of patents
    df['Year'] = df['1st_appeared_date'].dt.year
    counts = df.groupby('Year').size()
    
    # Plot the counts
    plt.figure(figsize=(10, 6))
    counts.plot(kind='line', color='skyblue')
    plt.title('Number of New Classifications Each Year')
    plt.xlabel('Year')
    plt.ylabel('Number of New Classifications')
    plt.show()        
    
    


if __name__ == "__main__":
    data_path = "data"
    first_appear_analysis(data_path)