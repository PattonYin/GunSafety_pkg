import os
import json
import pandas as pd
from pandas import NaT
from tqdm import tqdm, trange
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import seaborn as sns


df_basics = None
df_edge_list = None

def check_path(path_to_data):
    if os.path.exists(path_to_data):
        return
    else:
        raise FileNotFoundError(f"{path_to_data} does not exist.\nPlease specify the path to the patent data")

def first_appear_analysis(path_to_data="data", df=df_basics):
    df_basics=pd.read_csv(os.path.join(path_to_data, "raw/df_basics.csv"))
    df_edge_list = pd.read_csv(os.path.join(path_to_data, "raw/edge_list.csv"))
    # Step 1.0 - parent_date_process
    parent_date_process(path_to_data=path_to_data, df=df) 
    # 1.1 - subset_category    
    subset_category(path_to_data=path_to_data) 
    # 1.2 - join_date    
    join_date(path_to_data=path_to_data) 
    # 1.3 - first_date
    find_earliest_date(path_to_data=path_to_data)
    # 1.4 - plot_date
    plot_date(path_to_data=path_to_data)

# 1.0 - parent_date_process
def parent_date_process(path_to_data="data", df=df_basics):
    """
    Extract the parent date of all the patents and save it to a csv file.

    Args:
        path_to_data(str, optional): Path to the directory containing the patent data. Defaults to "data".
    """
    check_path(path_to_data)
    
    # configure path variables and initialize output folder
    output_folder = os.path.join(path_to_data, "intermediate/first_appear")
    os.makedirs(output_folder, exist_ok=True)
    output_path=os.path.join(path_to_data, "intermediate/first_appear/patent_date.csv")
    try:
        df_out = df[['guid', 'datePublished']]
    except:
        print("check the column names")
    df_out.to_csv(output_path, index=False)
    print("step 1 Done")
    
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
    groups = df_parent_with_cate.groupby(['0', '1', '2', '3'])
    for name, group in tqdm(groups, desc="subsetting patents by category"):
        group.to_csv(f'{output_path}/{name}.csv', index=False)
    print("step 2 Done")

            
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
    print("step 3 Done")
            
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
    print("step 4 Done")

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
    

def compute_patent_citation_span(path_to_data="data", edge_list=df_edge_list):
    global df_edge_list
    global df_basics
    check_path(path_to_data)
    df_edge_list = pd.read_csv(os.path.join(path_to_data, "raw/edge_list.csv"))
    df_basics = pd.read_csv(os.path.join(path_to_data, "raw/df_basics.csv"))
    
    # edge_list = compute_edge_list(df_edge_list)
    # date_span(path_to_data=path_to_data, edge_list=df_edge_list)    
    average_span(path_to_data=path_to_data)
    plot_distribution(path_to_data=path_to_data)
    plot_distribution_2(path_to_data=path_to_data)
    
    
def compute_edge_list(edge_list):
    """Compute the edge list of the patents.
    """
    raw_edge_list = edge_list
    # Subset the edge_list only if the ids in 'child' column are in the df_basics guid column
    edge_list = raw_edge_list[raw_edge_list['child'].isin(df_basics['guid'])]
    print("subsetting done")
    return edge_list
    
def date_span(path_to_data, edge_list=df_edge_list):
    check_path(path_to_data)
    
    output_path = os.path.join(path_to_data, "processed/citation_span.csv")
    
    output = edge_list
    for i in trange(len(edge_list)):
        # get the date of both the citing and cited patents
        id_1 = edge_list.iloc[i]['child']
        id_2 = edge_list.iloc[i]['parent']
        date_1_row = df_basics[df_basics['guid'] == id_1]['datePublished'].astype(str)
        date_1 = date_1_row.values[0] if not date_1_row.empty else pd.NaT
        
        date_2_row = df_basics[df_basics['guid'] == id_2]['datePublished'].astype(str)
        date_2 = date_2_row.values[0] if not date_2_row.empty else pd.NaT
        
        if pd.isna(date_1) or pd.isna(date_2):
            continue
        
        date_1 = datetime.strptime(date_1[:10], '%Y-%m-%d')
        date_2 = datetime.strptime(date_2[:10], '%Y-%m-%d')
        span = (date_1 - date_2).days
        # add the citation span to the output dataframe
        output.at[i, 'span'] = span
    
    output.to_csv(output_path, index=False)
    print("step 1 Done - computed citation time span")
    
def average_span(path_to_data="data"):
    """Compute the average citation span.
    
    Args:
        path_to_data (str, optional): input file path. Defaults to "output/citation_span.csv".
        output_path (str, optional): output file path. Defaults to "output/avg_citation_span.csv".
    """
    check_path(path_to_data)
    # Configure path variables
    data_path = os.path.join(path_to_data, 'processed/citation_span.csv')
    output_path = os.path.join(path_to_data, 'processed/avg_citation_span.csv')
    
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
    print("step 2 Done - computed average time span")

def plot_distribution(path_to_data="data", save=False):
    """Plot the distribution of the average citation span.
    
    Args:
        path_to_data (str, optional): input file path. Defaults to "output/avg_citation_span.csv".
    """
    check_path(path_to_data)
    # configure path variables
    data_path = os.path.join(path_to_data, 'processed/avg_citation_span.csv')
    output_path = os.path.join(path_to_data, 'processed/avg_span_distribution.png')
    
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


def plot_distribution_2(path_to_data="data", save=False, bins=50, kde=True, color='teal'):
    """Plot the distribution of the citation span.
    
    Args:
        path_to_data (str, optional): input file path. Defaults to "output/citation_span.csv".
    """
    check_path(path_to_data)
    # configure path variables
    data_path = os.path.join(path_to_data, 'processed/avg_citation_span.csv')
    output_path = os.path.join(path_to_data, 'processed/avg_span_distribution_2.png')
    
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

class network_plot:
    def __init__(self, edge_list=None):
        self.edge_list = edge_list
    
    def subset_edge_list(self, ids):
        """Subset the edge list with given ids.
        
        Args:
            ids (list) : list of patent ids
        
        Returns:
            _TBD_ : subset of the edge list
        """
        if ids is None:
            return self.edge_list
        return self.edge_list[self.edge_list['child'].isin(ids) | self.edge_list['parent'].isin(ids)]
    
    def prepare_edge_list(self, edge_list, threshold=1):
        # Compute the parent_count and child_count for each patent
        parent_count = edge_list['parent'].value_counts()
        child_count = edge_list['child'].value_counts()
        # remove the rows with parent count == 1
        print("removing rows")
        edge_list = edge_list[edge_list['parent'].isin(parent_count[parent_count > threshold].index)]
        
        return edge_list
        
    
    def plot_network(self, ids, threshold=2, edge_color='grey', node_color=["darkslategray", "aliceblue"], node_alpha=0.5, line_alpha=0.5, node_size_scale=100, width=0.3, linewidths=0.5, outline_color='black', figsize=(10, 10), font_size=8, labels=False):
        """Plot the network of the patents with given ids.
        
        Args:
            ids (list) : list of patent ids
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add edges to the graph
        print('subsetting edge list')
        edge_list = self.prepare_edge_list(self.subset_edge_list(ids), threshold=threshold)
        
        print('adding edges')
        for index, row in edge_list.iterrows():
            G.add_edge(row['child'], row['parent'])
            
        # determine the node size based on the number of citations
        node_size = [G.degree(node) * node_size_scale for node in G]
        
        # The more times of being referenced, the deeper the color, the more times of referencing, the brighter the color, the color changes from skyblue to deep red
        # Calculate the difference between in-degree and out-degree for each node
        degree_difference = {node: G.in_degree(node) - G.out_degree(node) for node in G}

        # Normalize the differences to a 0-1 scale
        min_diff = min(degree_difference.values())
        max_diff = max(degree_difference.values())
        normalized_diff = {node: (degree_difference[node] - min_diff) / (max_diff - min_diff) if max_diff > min_diff else 0.5 for node in G}

        # Map the normalized differences to a color gradient from skyblue to red
        import matplotlib.colors as mcolors

        def get_node_color(value, node_color=node_color):
            # Create a color map from skyblue to red
            cmap = mcolors.LinearSegmentedColormap.from_list("grad", node_color)
            return cmap(value)

        node_color = [get_node_color(normalized_diff[node]) for node in G]

                                
        # Plot the graph
        plt.figure(figsize=figsize)
        pos = nx.spring_layout(G)
        if labels:
            the_labels = {node: node for node in G.nodes()}
        else:
            the_labels = None
        nx.draw(G, pos, edge_color=edge_color, width=width, linewidths=linewidths,
                node_size=node_size, node_color=node_color, alpha=node_alpha, font_size=font_size, edgecolors=outline_color,
                with_labels=labels, labels=the_labels)
        plt.axis('off')
        plt.show()
        
        
    
    def plot_freq_count(self, ids, top_num=20):
        edge_list = self.prepare_edge_list(self.subset_edge_list(ids))
        parent_count = edge_list['parent'].value_counts()
        # plot the frequency count of the patents in descending order only the top 20
        plt.figure(figsize=(10, 8))
        parent_count[:top_num].plot(kind='bar', color='turquoise', width=0.8)
        plt.title('Top ' + str(top_num) + ' Most Cited Patents')  # Dynamically set the title based on top_num
        plt.xlabel('Patent ID')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()  # This will adjust the plot to fit better
        plt.grid(axis='y', alpha=0.75)
        plt.show()

    def plot_freq_count(self, ids):
        edge_list = self.prepare_edge_list(self.subset_edge_list(ids))
        parent_count = edge_list['parent'].value_counts()
        # Plot the frequency count of the patents in descending order for all patents
        plt.figure(figsize=(12, 8))  # You may need to adjust this size depending on the total number of patents
        ax = plt.gca()  # Get current axes

        # Hide top and right spines
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        # Show left and bottom spines
        ax.spines['left'].set_visible(True)
        ax.spines['bottom'].set_visible(True)

        # Plot all values. Removed the slicing to include all patents.
        parent_count.plot(kind='bar', color='turquoise', width=0.8)
        plt.title('Frequency Count of All Cited Patents')  # Updated title since we are not limiting to top_num anymore
        plt.xlabel('Patent ID')
        plt.ylabel('Frequency')
        plt.xticks(rotation=90, ha='right')  # Rotate x-ticks to 90 degrees for better label readability
        
        # Adding a grid
        plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')  # Customize the grid appearance

        plt.tight_layout()  # This will adjust the plot to fit better
        plt.show()

if __name__ == "__main__":
    data_path = "data"
    # first_appear_analysis(data_path)
    # compute_patent_citation_span(data_path)
    plot_distribution_2(data_path)