import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import os
from tqdm import tqdm

class first_appear:
    def __init__(self):
        self.x = None

    def run(self):
        self.parent_date_process() # 1.0 - parent_date_process
        first_appear.subset_category() # 1.1 - subset_category        
        first_appear.join_date() # 1.2 - join_date
        first_appear.find_earliest_date() # 1.3 - first_date
        first_appear.plot_date() # 1.4 - plot_date

    # 1.0 - parent_date_process
    def parent_date_process(self, all_patents_path="data/df_basics.csv", output_path="temp/patent_date.csv"):
        """
        Process the parent date of all patents and save it to a csv file.

        Args:
            all_patents_path (str, optional): Path to the dataframe containing the patent ids and datePublished. Defaults to "data/df_basics.csv".
        """
        df_all_patents = pd.read_csv(all_patents_path, low_memory=False)
        print("csv read")
        df_out = df_all_patents[['guid', 'datePublished']]
        print("subsetted")
        os.makedirs('temp', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        df_out.to_csv(output_path, index=False)
        
    # 1.1 - for each category, find the first appeared patent and the corresponding date
    def subset_category(self, classification_path="data/patent_classification.csv", output_path = 'temp/cate_subsetted_data'):
        """
        Subset the patents by category and save them to individual csv files.

        Args:
            classification_path (str, optional): path to the cpc classifications. Defaults to "data/patent_classification.csv".
            output_path (str, optional): folder of the output path. Defaults to 'temp/cate_subsetted_data'.
        """
        df_parent_with_cate = pd.read_csv(classification_path, low_memory=False)
        print("csv read")
        groups = df_parent_with_cate.groupby(['0', '1', '2', '3'])
        os.makedirs(output_path, exist_ok=True)
        for name, group in tqdm(groups, desc="subsetting patents by category"):
            group.to_csv(f'{output_path}/{name}.csv', index=False)

                
    # 1.2 - for each individual csv, join with parent_date.csv to get the date of the first appeared patent
    def join_date(self, data_path_01="temp/patent_date.csv", data_path_02="temp/cate_subsetted_data", output_path="temp/cate_date_data"):
        df_patent_date = pd.read_csv(data_path_01, low_memory=False)
        os.makedirs(output_path, exist_ok=True)
        for file in tqdm(os.listdir(data_path_02), desc="joining date to patents"):
            df = pd.read_csv(f'{data_path_02}/{file}', low_memory=False)
            # rename column '4' to 'guid'
            df.rename(columns={'4': 'guid'}, inplace=True)
            df_out = pd.merge(df, df_patent_date, how='left', on='guid')
            df_out.to_csv(f'{output_path}/{file}', index=False)
                
    # 1.3 - for each individual csv, find the earliest date and corresponding id
    def find_earliest_date(self, data_path_01="temp/cate_date_data", output_path="output/first_appeared.csv"):
        list = []
        index = 0
        for file in tqdm(os.listdir(data_path_01), desc="finding the earliest date"):
            df = pd.read_csv(f'{data_path_01}/{file}', low_memory=False)
            # modify the datePublished column, by taking only the first 10 characters (which looks like 2000-01-01), and then convert to datetime, then find the earliest date
            df['datePublished'] = pd.to_datetime(df['datePublished'].str[:10])
            earliest_date = df['datePublished'].min()
            # find the corresponding id
            earliest_id = df[df['datePublished'] == earliest_date]['guid'].values[0]
            earliest_cate_1 = str(df[df['datePublished'] == earliest_date]['0'].values[0])
            earliest_cate_2 = str(df[df['datePublished'] == earliest_date]['1'].values[0])
            earliest_cate_3 = str(int(df[df['datePublished'] == earliest_date]['2'].values[0]))
            earliest_cate_4 = str(int(df[df['datePublished'] == earliest_date]['3'].values[0]))
            earliest_cate = earliest_cate_1 + '/' + earliest_cate_2 + '/' + earliest_cate_3 + '/' + earliest_cate_4
            list.append([earliest_id, earliest_date, earliest_cate])
        first_appeared = pd.DataFrame(list, columns=['guid', '1st_appeared_date', 'earliest_cate'])
        first_appeared.to_csv(output_path, index=False)

    # 1.4 - plot out how the patents distribute over time
    def plot_date(self, file_path="output/first_appeared.csv"):
        df = pd.read_csv(file_path, low_memory=False)
        df['1st_appeared_date'] = pd.to_datetime(df['1st_appeared_date'])
        # Extract the year from the date and Group by year and count the number of patents
        df['Year'] = df['1st_appeared_date'].dt.year
        counts = df.groupby('Year').size()

        # Plot the counts
        plt.figure(figsize=(10, 6))
        counts.plot(kind='line')
        plt.title('Number of Patents Over Time')
        plt.xlabel('Year')
        plt.ylabel('Number of Patents')
        plt.show()        
    

class Network_plot:
    def __init__(self):
        self.edge_list = pd.read_csv("data/edge_list.csv")
    
    def subset_edge_list(self, ids):
        """Subset the edge list with given ids.
        
        Args:
            ids (list) : list of patent ids
        
        Returns:
            _TBD_ : subset of the edge list
        """
        return self.edge_list[self.edge_list['0'].isin(ids) | self.edge_list['1'].isin(ids)]
    
    def plot_network(self, ids, edge_color='brown', node_color='skyblue', node_alpha=0.9, node_size=100, width=1, linewidths=1, figsize=(10, 10)):
        """Plot the network of the patents with given ids.
        
        Args:
            ids (list) : list of patent ids
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add edges to the graph
        edge_list = self.subset_edge_list(ids)
        for index, row in edge_list.iterrows():
            G.add_edge(row['0'], row['1'])
        
        # Plot the graph
        plt.figure(figsize=figsize)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, edge_color=edge_color, width=width, linewidths=linewidths,
                node_size=node_size, node_color=node_color, alpha=node_alpha,
                labels={node: node for node in G.nodes()})
        plt.axis('off')
        plt.show()
    
        
if __name__ == "__main__":
    first_appear = first_appear()
    first_appear.run()
    
    # network_plot = Network_plot()
    # ids = ["US-10001331-B2"]
    # network_plot.plot_network(ids)
    