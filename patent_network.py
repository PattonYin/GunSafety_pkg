import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

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
    network_plot = Network_plot()
    ids = ["US-10001331-B2"]
    network_plot.plot_network(ids)