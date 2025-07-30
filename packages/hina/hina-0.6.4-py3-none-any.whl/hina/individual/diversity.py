import networkx as nx 
from collections import defaultdict
import numpy as np 
import pandas as pd 

def diversity(B, attr=None):
    """
    Computes the diversity value of individual nodes in a bipartite graph based on a specified attribute or the object nodeset.

    The diversity value is calculated based on Shannon entropy formula, normalized by the logarithm of the number of unique attribute categories.
    It measures how evenly a student's connections are distributed across different objects or object attribute categories.

    Parameters:
    -----------
    B : networkx.Graph
        A bipartite graph. Nodes need to have a 'bipartite' attribute indicating their partition. 
    attr : str, optional
        The column name of the attribute related to the studied objects in the input dataframe. 
        For example, if the bipartite graph B represents relationships between students and interaction codes (e.g., (student, interaction_codes)), 
        the attr could be a column like interaction_dimensions, which categorizes the interaction codes into broader dimensions.
        If attr is provided, diversity is calculated based on the categories of the specified attribute.
        If attr is None, the function uses the object nodes themselves (e.g., interaction_codes) 
        as the target for diversity calculation.

    Returns:
    --------
    dict
        A dictionary where keys are nodes and values are their diversity values. 
        The diversity value is a float between 0 and 1,
        where 0 indicates no diversity (all connections of an indivdiual to a single category) 
        and 1 indicates maximum diversity (evenly distributed
        connections across all categories).
     dataframe
       A dataframe containing diversity value of each student node
    """
  
    v = set()
    node_bipartite_list = [x for x in [data['bipartite'] for n, data in B.nodes(data=True)]\
                     if not (x in v or v.add(x))]
    
    if attr is None:
        attr_set = [j for i,j in B.edges]
    else:
        attr_set = [data[attr] for n, data in B.nodes(data=True) if data.get('bipartite') == node_bipartite_list[1]]
        
    quantity_by_attr = defaultdict(lambda: defaultdict(float))

    # Iterate over edges
    for i, j, wij in B.edges(data='weight'):
        if j in attr_set:  
            quantity_by_attr[i][j] += wij
        elif B.nodes[j][attr] in attr_set: 
            j = B.nodes[j][attr]
            quantity_by_attr[i][j] += wij
    
    N = len(set(attr_set))

    diversity = {}
    for i in quantity_by_attr:
        wi = sum(quantity_by_attr[i].values())  # Total weight for node i
        if wi > 0:  # Avoid division by zero
            diversity[i] = -sum((w / wi) * np.log(w / wi) for w in quantity_by_attr[i].values() if w > 0)
            diversity[i] /= np.log(N) 
        else:
            diversity[i] = 0  
    diversity_df = pd.DataFrame(list(diversity.items()), columns=['username', 'diversity'])
    return diversity, diversity_df
