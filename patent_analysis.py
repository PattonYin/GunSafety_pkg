import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import os
import json
from tqdm import tqdm, trange
from datetime import datetime
from pandas import NaT
import seaborn as sns
import numpy as np



class first_appear:
    def __init__(self):
        self.dataset = None

    def run(self, patent_path="data/df_basics.csv", classification_path="data/patent_classification.csv"):
        self.parent_date_process(patents_path=patent_path) # 1.0 - parent_date_process
        first_appear.subset_category(classification_path=classification_path) # 1.1 - subset_category        
        first_appear.join_date() # 1.2 - join_date
        first_appear.find_earliest_date() # 1.3 - first_date
        first_appear.plot_date() # 1.4 - plot_date

    # 1.0 - parent_date_process
    def parent_date_process(self, patents_path="data/df_basics.csv", output_path="temp/patent_date.csv"):
        """
        Process the parent date of all patents and save it to a csv file.

        Args:
            all_patents_path (str, optional): Path to the dataframe containing the patent ids and datePublished. Defaults to "data/df_basics.csv".
        """
        df_all_patents = pd.read_csv(patents_path, low_memory=False)
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
        """
        Join the date of the first appeared patent to each category and save to individual csv files.

        Args:
            data_path_01 (str, optional): input data path. Defaults to "temp/patent_date.csv".
            data_path_02 (str, optional): input data path. Defaults to "temp/cate_subsetted_data".
            output_path (str, optional): output data path. Defaults to "temp/cate_date_data".
        """
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
        """
        Find the earliest date and corresponding id for each category and save to a csv file.

        Args:
            data_path_01 (str, optional): input data path . Defaults to "temp/cate_date_data".
            output_path (str, optional): output data path. Defaults to "output/first_appeared.csv".
        """
        list = []
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
            list.append([earliest_id, earliest_date, earliest_cate])
        first_appeared = pd.DataFrame(list, columns=['guid', '1st_appeared_date', 'earliest_cate'])
        first_appeared.to_csv(output_path, index=False)

    # 1.4 - plot out how the patents distribute over time
    def plot_date(self, file_path="output/first_appeared.csv"):
        """
        Plot the distribution of the patents over time.

        Args:
            file_path (str, optional): input file path. Defaults to "output/first_appeared.csv".
        """
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
    def __init__(self, patents_path="data/df_basics.csv", compute_edge_list=False):
        self.df_basics = pd.read_csv(patents_path)
        self.edge_list = pd.read_csv("data/edge_list.csv")
        if compute_edge_list:
            self.compute_edge_list()
            
    def compute_edge_list(self):
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
    
class network_plot:
    def __init__(self):
        self.edge_list = pd.read_csv("data/edge_list.csv")
    
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
    # first_appear = first_appear()
    # first_appear.run()
    # first_appear.plot_date()
    
    # compute_patent_citation_span = compute_patent_citation_span(patents_path="temp/2010-2011.csv", compute_edge_list=True) not working, due to the limited number of references
    # compute_patent_citation_span = compute_patent_citation_span()
    # compute_patent_citation_span.date_span()
    # compute_patent_citation_span.average_span()
    # compute_patent_citation_span.plot_distribution_2()
    # compute_patent_citation_span.plot_distribution_2(save=True, output_path="output/avg_span_distribution.png")
    
    network_plot = network_plot()
    with open('config.json') as f:
        ids = json.load(f)['network_id_02']
    network_plot.plot_network(ids)
    # network_plot.plot_freq_count(ids=None)
    
    
    
    # ids = ['US-10001331-B2',
    #         'US-10001332-B1',
    #         'US-10001335-B2',
    #         'US-10001336-B2',
    #         'US-10001337-B2',
    #         'US-10001340-B1',
    #         'US-10001342-B2',
    #         'US-10001345-B2',
    #         'US-10003756-B2',
    #         'US-10004136-B2',
    #         'US-10004209-B2',
    #         'US-10005556-B2',
    #         'US-10006727-B2',
    #         'US-10006728-B2',
    #         'US-10006729-B2',
    #         'US-10006736-B2',
    #         'US-10006739-B2',
    #         'US-10006741-B2',
    #         'US-10006745-B2',
    #         'US-10012457-B2',
    #         'US-10012464-B2',
    #         'US-10012466-B2',
    #         'US-10012469-B2',
    #         'US-10012470-B2',
    #         'US-10012472-B2',
    #         'US-10012533-B2',
    #         'US-10017250-B2',
    #         'US-10018433-B2',
    #         'US-10018434-B2',
    #         'US-10018435-B2',
    #         'US-10018438-B2',
    #         'US-10018445-B2',
    #         'US-10018446-B2',
    #         'US-10018448-B2',
    #         'US-10018449-B2',
    #         'US-10024616-B2',
    #         'US-10024619-B2',
    #         'US-10024621-B2',
    #         'US-10024628-B2',
    #         'US-10024629-B2',
    #         'US-10024630-B2',
    #         'US-10024634-B2',
    #         'US-10025306-B2',
    #         'US-10030813-B2',
    #         'US-10030922-B2',
    #         'US-10030939-B2',
    #         'US-10030940-B2',
    #         'US-10032387-B2',
    #         'US-10036603-B2',
    #         'US-10036606-B2',
    #         'US-10036608-B2',
    #         'US-10036612-B2',
    #         'US-10036613-B2',
    #         'US-10036799-B2',
    #         'US-10041752-B2',
    #         'US-10041757-B2',
    #         'US-10041763-B2',
    #         'US-10042360-B2',
    #         'US-10045561-B2',
    #         'US-10048028-B2',
    #         'US-10048029-B2',
    #         'US-10048030-B2',
    #         'US-10048043-B2',
    #         'US-10051984-B2',
    #         'US-10053803-B2',
    #         'US-10054392-B2',
    #         'US-10054394-B2',
    #         'US-10054399-B2',
    #         'US-10054400-B2',
    #         'US-10054405-B2',
    #         'US-10057468-B2',
    #         'US-10059445-B2',
    #         'US-10060177-B2',
    #         'US-10060689-B2',
    #         'US-10060691-B2',
    #         'US-10060692-B2',
    #         'US-10060694-B2',
    #         'US-10060701-B1',
    #         'US-10060705-B2',
    #         'US-10060706-B2',
    #         'US-10061069-B2',
    #         'US-10062028-B2',
    #         'US-10062464-B2',
    #         'US-10063522-B2',
    #         'US-10065095-B2',
    #         'US-10065718-B1',
    #         'US-10065720-B2',
    #         'US-10066885-B2',
    #         'US-10066886-B2',
    #         'US-10066887-B1',
    #         'US-10066888-B2',
    #         'US-10066890-B1',
    #         'US-10066892-B1',
    #         'US-10066893-B2',
    #         'US-10066897-B2',
    #         'US-10066898-B1',
    #         'US-10066900-B2',
    #         'US-10066901-B2',
    #         'US-10066903-B2',
    #         'US-10066906-B2']
    

    