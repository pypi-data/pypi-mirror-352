from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
from hina.app.api import utils
import base64
import networkx as nx
import json
from io import StringIO
import uuid
from datetime import datetime

app = FastAPI(title="HINA REST API")

origins = [
    # "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        # Encode the file contents in base64 and generate uuid and timestamp
        upload_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        encoded = base64.b64encode(contents).decode('utf-8') 
        df = utils.parse_contents(encoded, file.filename)
        return {
            "columns": df.columns.tolist(),
            "data": df.to_json(orient="split"),
            "upload_id": upload_id,
            "timestamp": timestamp,
            "filename": file.filename
        }
    except Exception as e:
        print(f"Error in upload_file: {str(e)}")
        return {"error": str(e)}, 500

@app.post("/build-hina-network")
async def build_hina_network_endpoint(
    data: str = Form(...),
    group_col: str = Form(None),  
    group: str = Form(...),
    student_col: str = Form(...),  
    object1_col: str = Form(...), 
    object2_col: str = Form(None),  
    attr_col: str = Form(None),   
    pruning: str = Form(...),     # "none" or "custom"
    alpha: float = Form(0.05),
    fix_deg: str = Form(None),
    layout: str = Form("bipartite")
):
    try:
        object2_col = None if object2_col in ["none", "null", "undefined", ""] else object2_col
        attr_col = None if attr_col in ["none", "null", "undefined", ""] else attr_col
        group_col = None if group_col in ["none", "null", "undefined", ""] else group_col
        
        df = pd.read_json(StringIO(data), orient="split")

        pruning_param = {"fix_deg": fix_deg, "alpha": alpha} if pruning == "custom" else "none"

        nx_G, pos, significant_edges = utils.build_hina_network(
            df=df, 
            group_col=group_col, 
            group=group, 
            student_col=student_col, 
            object1_col=object1_col, 
            object2_col=object2_col,
            attr_col=attr_col,
            pruning=pruning_param, 
            layout=layout
        )
        elements = utils.cy_elements_from_graph(nx_G, pos)
        return {
            "elements": elements,
            "significant_edges": significant_edges
        }
    except Exception as e:
        print(f"Error in build_hina_network_endpoint: {str(e)}")


@app.post("/build-cluster-network")
async def build_cluster_network_endpoint(
    data: str = Form(...),
    group_col: str = Form(None),  
    student_col: str = Form(...),  
    object1_col: str = Form(...), 
    object2_col: str = Form(None),  
    attr_col: str = Form(None),   
    pruning: str = Form(...),     # "none" or "custom"
    alpha: float = Form(0.05),
    fix_deg: str = Form(None),
    layout: str = Form("bipartite"),
    number_cluster: str = Form(None)
):
    try:
        attr_col = None if attr_col in ["none", "null", "undefined", ""] else attr_col
        group_col = None if group_col in ["none", "null", "undefined", ""] else group_col
        
        df = pd.read_json(StringIO(data), orient="split")
        pruning_param = {"fix_deg": fix_deg, "alpha": alpha} if pruning == "custom" else "none"

        nx_G, pos, significant_edges, cluster_labels, compression_ratio, object_object_graphs = utils.build_clustered_network(
            df=df, 
            group_col=group_col, 
            student_col=student_col, 
            object1_col=object1_col, 
            object2_col=object2_col,
            attr_col=attr_col,
            pruning=pruning_param, 
            layout=layout,
            number_cluster=number_cluster
        )
        elements = utils.cy_elements_from_graph(nx_G, pos)
        # Convert NetworkX graphs to JSON serializable format
        serializable_graphs = {}
        for comm_id, graph in object_object_graphs.items():
            serializable_graphs[comm_id] = nx.node_link_data(graph, edges="links")
        return {
            "elements": elements,
            "cluster_labels": cluster_labels,
            "compression_ratio": compression_ratio,
            "object_object_graphs": serializable_graphs,
            "significant_edges": significant_edges  
        }
    except Exception as e:
        print(f"Error in build_cluster_network_endpoint: {str(e)}")

@app.post("/build-object-network")
async def build_object_network_endpoint(
    data: str = Form(...),
    community_id: str = Form(...),
    object1_col: str = Form(...),  
    object2_col: str = Form(...),  
    layout: str = Form("bipartite")
):
    try:
        object_graphs_data = json.loads(data)        
        if community_id not in object_graphs_data:
            print(f"No object graph found for community ID {community_id}")
            # raise HTTPException(status_code=404, detail=f"No object graph found for community ID {community_id}")
        
        # Get the NetworkX graph for this community
        graph_data = object_graphs_data[community_id]
        # print(f"Graph data for community {community_id}: {graph_data}")
        G = nx.node_link_graph(graph_data, edges="links")
        if len(G.nodes()) == 0:
            return {"elements": [], "community_id": community_id}
        
        # Set attributes for nodes based on bipartite attribute
        for node, attrs in G.nodes(data=True):
            node_str = str(node)
            bipartite_value = str(attrs.get('bipartite', ''))
            if object1_col in bipartite_value:
                G.nodes[node]['color'] = 'blue' if node_str != 'NA' else 'black'
                G.nodes[node]['type'] = 'object1'
            else:
                G.nodes[node]['color'] = 'green' if node_str != 'NA' else 'black'
                G.nodes[node]['type'] = 'object2'
        
        if layout == 'spring':
            pos = nx.spring_layout(G, k=0.3)
        elif layout == 'circular':
            pos = nx.circular_layout(G)
        elif layout == 'bipartite':
            object1_nodes = [n for n, d in G.nodes(data=True) if d.get('type') == 'object1']
            if object1_nodes:
                pos = nx.bipartite_layout(G, object1_nodes, align='vertical', scale=1.5, aspect_ratio=0.7)
            else:
                pos = nx.spring_layout(G, k=0.3)
        else:
            pos = nx.spring_layout(G, k=0.3)
            
        elements = utils.cy_elements_from_graph(G, pos)
        return {
            "elements": elements,
            "community_id": community_id
        }
    except Exception as e:
        print(f"Error in build_object_network_endpoint: {str(e)}")
        # raise HTTPException(status_code=500, detail=str(e))
        return {"elements": [], "community_id": community_id, "error": str(e)}

@app.post("/quantity-diversity")
async def quantity_diversity_endpoint(
    data: str = Form(...),
    student_col: str = Form(...),  
    object1_col: str = Form(...),  
    object2_col: str = Form(...),
    attr_col: str = Form(None),   
    group_col: str = Form(None)   
):
    try:
        df = pd.read_json(StringIO(data), orient="split")
        attr_col = None if attr_col in ["none", "null", "undefined", ""] else attr_col
        group_col = None if group_col in ["none", "null", "undefined", ""] else group_col
        object2_col = None if object2_col in ["none", "null", "undefined", ""] else object2_col
        if object2_col is not None and attr_col is None:
            B= utils.get_tripartite(df, student_col, object1_col, object2_col, group_col)
        else:
            B = utils.get_bipartite(df, student_col, object1_col, attr_col, group_col)
        
        # Get all quantities
        quantity_results, _ = utils.quantity(B, attr=attr_col, group=group_col, return_type='all')
        # Get diversity
        diversity_results, _ = utils.diversity(B, attr=attr_col)
        
        response = {
            "quantity": quantity_results.get('quantity', {}),
            "normalized_quantity": quantity_results.get('normalized_quantity', {}),
            "diversity": diversity_results
        }
        # Convert tuple keys to string for JSON serialization
        if 'quantity_by_category' in quantity_results:
            category_dict = {}
            for (node, category), value in quantity_results['quantity_by_category'].items():
                if node not in category_dict:
                    category_dict[node] = {}
                category_dict[node][str(category)] = value
            response["quantity_by_category"] = category_dict
            
        if 'normalized_quantity_by_group' in quantity_results:
            response["normalized_quantity_by_group"] = quantity_results['normalized_quantity_by_group']       

        return utils.convert_numpy_scalars(response)
    except Exception as e:
        print(f"Error in quantity_diversity_endpoint: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
