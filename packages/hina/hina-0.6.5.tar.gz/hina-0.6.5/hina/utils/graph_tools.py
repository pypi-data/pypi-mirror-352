import networkx as nx

def save_network(G, filename, format='gml'):
    """
    Saves the bipartite network G (set of tuples (i,j,w)) to a specified file format.
    Supported formats: 'graphml', 'gexf', 'gpickle', etc.
    """
    # Convert edge set to a NetworkX graph
    B = nx.Graph()
    for s, t, w in G:
        B.add_edge(s, t, weight=w)

    if format == 'gml':
        nx.write_gml(B, filename + '.gml')
    elif format == 'gexf':
        nx.write_gexf(B, filename + '.gexf')
    elif format == 'graphml':
        nx.write_graphml(B, filename + '.graphml')
    else:
        raise ValueError("Unsupported format: {}".format(format))