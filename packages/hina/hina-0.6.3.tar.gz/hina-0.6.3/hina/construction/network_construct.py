import networkx as nx 
import pandas as pd 
from collections import Counter
import warnings 

def get_bipartite(df,student_col,object_col,attr_col = None,group_col = None):
 
    """
    Constructs a bipartite graph from a given DataFrame.

    This function creates a weighted bipartite graph representing relationships between individuals and studied 
    objects (e.g. coded constructs, behaviors, subtasks).The graph can optionally include group information for 
    student nodes and attribute information for object nodes. Node types (student or object) are added as 
    attributes to facilitate further individual-level analysis.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame containing the data to construct the bipartite graph.
    student_col : str
        The column name in the DataFrame representing student nodes.
    object_col : str
        The column name in the DataFrame representing the studied object nodes.
    attr_col : str, optional
        The column name in the DataFrame representing attributes for object nodes (e.g. the dimension of coded constructs). 
        If provided, these attributes will be added as node attributes in the graph. Default is None.
    group_col : str, optional
        The column name in the DataFrame representing group information for student nodes. If provided, these groups
        will be added as node attributes in the graph. Default is None.

    Returns:
    --------
    networkx.Graph
        A bipartite graph with the following properties:
        - Nodes: Student nodes and object nodes, with 'bipartite' attribute indicating their type.
        - Edges: Weighted edges between student and object nodes, where weights represent the frequency of relationships.
        - Node attributes: If `group_col` is provided, student nodes will have a group attribute. If `attr_col` is provided,
          object nodes will have an attribute.

    Example:
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'student': ['Alice', 'Bob', 'Alice', 'Charlie'],
    ...     'object': ['ask questions', 'answer questions', 'evaluating', 'monitoring'],
    ...     'group': ['A', 'B', 'A', 'B'],
    ...     'attr': ['cognitive', 'cognitive', 'metacognitive', 'metacognitive']
    ... })
    >>> B = get_bipartite(df, student_col='student', object_col='object', attr_col='attr', group_col='group')
    >>> print(B.nodes(data=True))
    [('Alice', {'bipartite': 'student', 'group': 'A'}), 
     ('Bob', {'bipartite': 'student', 'group': 'B'}), 
     ('Charlie', {'bipartite': 'student', 'group': 'B'}), 
     ('ask question', {'bipartite': 'object', 'attr': 'cognitive}), 
     ('answer questions', {'bipartite': 'object', 'attr': 'cognitive'})]
    """
    # Drop rows with NaN or empty student_col
	
    original_size = len(df)
    df = df.dropna(subset=[student_col])
    df = df[df[student_col].astype(str).str.strip() != ""]
    removed_count = original_size - len(df)
    if removed_count > 0:
        warnings.warn(
            f"{removed_count} rows with empty '{student_col}' values were removed",
            UserWarning,
            stacklevel=2  
        )
	    
    # Fill NaN in other relevant columns
    fill_cols = [object_col]
    if attr_col: fill_cols.append(attr_col)
    if group_col: fill_cols.append(group_col)
    df[fill_cols] = df[fill_cols].fillna("NA").astype(str)
	
    edge_dict = Counter([tuple(e) for e in df[[student_col,object_col]].values])
    edgelist = [tuple([it[0][0],it[0][1],{'weight':it[1]}]) for it in edge_dict.items()]
    
    B = nx.Graph()
    B.add_nodes_from([i[0] for i in edgelist],bipartite= student_col)
    B.add_nodes_from([i[1] for i in edgelist],bipartite= object_col)
    B.add_edges_from(edgelist)
    if group_col is not None:
        student_groups = df[[student_col, group_col]].drop_duplicates().set_index(student_col)[group_col].to_dict()
        nx.set_node_attributes(B, {n: {group_col: student_groups[n]} for n in B.nodes if n in student_groups})
    if attr_col is not None:
        object_attrs = df[[object_col, attr_col]].drop_duplicates().set_index(object_col)[attr_col].to_dict()
        nx.set_node_attributes(B, {n: {attr_col: object_attrs[n]} for n in B.nodes if n in object_attrs})

    return B



def get_tripartite(df,student_col,object1_col,object2_col,group_col = None):

    """
    Constructs a tripartite graph from a given DataFrame.

    This function creates a weighted tripartite graph representing relationships between student nodes and two types of
    object nodes (e.g. codes from different modalities). This method can be particularly useful for multimodal data analysis.  
    The graph can optionally include group information for student nodes as student attributes to facilitate further individual-level analysis.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame containing the data to construct the tripartite graph.
    student_col : str
        The column name in the DataFrame representing student nodes.
    object1_col : str
        The column name in the DataFrame representing the first type of object nodes.
    object2_col : str
        The column name in the DataFrame representing the second type of object nodes.
    group_col : str, optional
        The column name in the DataFrame representing group information for student nodes. If provided, these groups
        will be added as node attributes in the graph. Default is None.

    Returns:
    --------
    networkx.Graph
        A tripartite graph with the following properties:
        - Nodes: Student nodes and joint object nodes (combining `object1_col` and `object2_col`), with 'bipartite' and
          'tripartite' attributes indicating their type.
        - Edges: Weighted edges between student and joint object nodes, where weights represent the frequency of relationships.
        - Node attributes: If `group_col` is provided, student nodes will have a group attribute.

    Example:
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'student': ['Alice', 'Bob', 'Alice', 'Charlie'],
    ...     'object1': ['ask questions', 'answer questions', 'evaluating', 'monitoring'],
    ...     'object2': ['tilt head', 'shake head', 'nod head', 'nod head'],
    ...     'group': ['A', 'B', 'A', 'B']
    ... })
    """  
    df_ = df.copy()
    # Drop rows with NaN or empty student_col

    original_size = len(df_)
    df_ = df_.dropna(subset=[student_col])
    df_ = df_[df_[student_col].astype(str).str.strip() != ""]

    removed_count = original_size - len(df_)
    if removed_count > 0:
        warnings.warn(
            f"{removed_count} rows with empty '{student_col}' values were removed",
            UserWarning,
            stacklevel=2  
        )
	    
    # Fill NaN in other columns and convert to string 
    fill_cols = [object1_col, object2_col]
    if group_col: fill_cols.append(group_col)
    df_[fill_cols] = df_[fill_cols].fillna("NA").astype(str)
    df_['joint_objects'] = df_[object1_col].str.cat(df_[object2_col], sep='**')

    edge_dict = Counter([tuple(e) for e in df_[[student_col,'joint_objects']].values])
    edgelist = [tuple([it[0][0],it[0][1],{'weight':it[1]}]) for it in edge_dict.items()]
    
    T = nx.Graph()
    T.add_nodes_from([i[0] for i in edgelist],bipartite= student_col)
    T.add_nodes_from([i[1] for i in edgelist],bipartite= f"({object1_col},{object2_col})", tripartite = True)
    T.add_edges_from(edgelist)

    if group_col is not None:
        student_groups = df_[[student_col, group_col]].drop_duplicates().set_index(student_col)[group_col].to_dict()
        nx.set_node_attributes(T, {n: {group_col: student_groups[n]} for n in T.nodes if n in student_groups})
    
    return T
