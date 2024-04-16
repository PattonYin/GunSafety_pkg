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

def first_appear_analysis(path_to_data="data", file_path="raw/df_basics.csv",df=None):
    # Step 1.0 - parent_date_process
    if df is None:
        parent_date_process(path_to_data=path_to_data, file_path=file_path)
    else:
        parent_date_process(path_to_data=path_to_data, file=df) 
    # 1.1 - subset_category    
    subset_category(path_to_data=path_to_data) 
    # 1.2 - join_date    
    join_date(path_to_data=path_to_data) 
    # 1.3 - first_date
    find_earliest_date(path_to_data=path_to_data)
    # 1.4 - plot_date
    plot_date(path_to_data=path_to_data)

# 1.0 - parent_date_process
def parent_date_process(path_to_data="data", file_path="raw/df_basics.csv", file=None):
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
    
    if file is None:
        df_all_patents = pd.read_csv(patents_path, low_memory=False)
    else:
        df_all_patents = file
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
    
    
class compute_patent_citation_span:
    def __init__(self, patents_path="data/df_basics.csv", subset_edge_list=False):
        self.df_basics = pd.read_csv(patents_path)
        self.edge_list = pd.read_csv("data/edge_list.csv")
        if subset_edge_list:
            self.subset_edge_list()
            
    def subset_edge_list(self):
        """Compute the edge list of the patents.
        """
        raw_edge_list = self.edge_list
        # Subset the edge_list only if the ids in 'child' column are in the df_basics guid column
        edge_list = raw_edge_list[raw_edge_list['child'].isin(self.df_basics['guid'])]
        self.edge_list = edge_list
        
    def date_span(self, output_path="output/citation_span.csv"):
        """Compute the citation span for each patent.
        
        Args:
            output_path (str, optional): output file path. Defaults to "output/citation_span.csv".
        """
        output = self.edge_list.copy()
        for i in trange(len(self.edge_list)):
            # get the date of both the citing and cited patents
            id_1 = self.edge_list.iloc[i]['child']
            id_2 = self.edge_list.iloc[i]['parent']
            date_1_row = self.df_basics[self.df_basics['guid'] == id_1]['datePublished'].astype(str)
            date_1 = date_1_row.values[0] if not date_1_row.empty else NaT
            
            date_2_row = self.df_basics[self.df_basics['guid'] == id_2]['datePublished'].astype(str)
            date_2 = date_2_row.values[0] if not date_2_row.empty else NaT
            
            if pd.isna(date_1) or pd.isna(date_2):
                continue
            date_1 = datetime.strptime(date_1[:10], '%Y-%m-%d')
            date_2 = datetime.strptime(date_2[:10], '%Y-%m-%d')
            span = (date_1 - date_2).days
            # add the citation span to the output dataframe
            output.at[i, 'span'] = span
        
        output.to_csv(output_path, index=False)
        
    def average_span(self, data_path="output/citation_span.csv", output_path="output/avg_citation_span.csv"):
        """Compute the average citation span.
        
        Args:
            data_path (str, optional): input file path. Defaults to "output/citation_span.csv".
            output_path (str, optional): output file path. Defaults to "output/avg_citation_span.csv".
        """
        df_span = pd.read_csv(data_path)
        # initialize another dataframe to store the average span for each patent
        df_avg_span = pd.DataFrame(columns=['child_guid', 'avg_span'])
        
        patent_group = df_span.groupby('child')
        # compute the average span for each patent
        avg_span = patent_group['span'].mean()
        child_list = []
        span_list = []
        for child, span in avg_span.items():
            child_list.append(child)
            span_list.append(span)
        df_avg_span['child_guid'] = child_list
        df_avg_span['avg_span'] = span_list
        df_avg_span.to_csv(output_path, index=False)
    
    def plot_distribution(self, data_path="output/avg_citation_span.csv", save=False, output_path="output/avg_span_distribution.png"):
        """Plot the distribution of the average citation span.
        
        Args:
            data_path (str, optional): input file path. Defaults to "output/avg_citation_span.csv".
        """
        df_avg_span = pd.read_csv(data_path)
        plt.figure(figsize=(10, 6))
        plt.hist(df_avg_span['avg_span'], bins=50, color='pink', edgecolor='red')
        plt.title('Distribution of Average Span')
        plt.xlabel('Average Span')
        plt.ylabel('Frequency')
        plt.grid(axis='y', alpha=0.75)

        if save:
            plt.savefig(output_path, dpi=300)
            plt.close()
        else:
            plt.show()
    
    
    def plot_distribution_2(self, data_path="output/avg_citation_span.csv", bins=50, kde=True, color='teal', save=False, output_path="output/avg_span_distribution.png"):
        """Plot the distribution of the citation span.
        
        Args:
            data_path (str, optional): input file path. Defaults to "output/citation_span.csv".
        """
        df_avg_span = pd.read_csv(data_path)
        df_avg_span.replace([np.inf, -np.inf], np.nan, inplace=True)
        sns.set(style="whitegrid")
        plt.figure(figsize=(12, 7))
        sns.histplot(df_avg_span['avg_span'], bins=bins, kde=kde, color=color)
        plt.title('Distribution of Average Span with KDE', fontsize=15)
        plt.xlabel('Average Span', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        
        if save:
            plt.savefig(output_path, dpi=300)
            plt.close()
        else:
            plt.show()






if __name__ == "__main__":
    data_path = "data"
    first_appear_analysis(data_path)