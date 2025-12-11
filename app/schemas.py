from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Edge(BaseModel):
    from_node: str
    to_node: Optional[str] = None  # If None, it might use a condition
    condition: Optional[str] = None # Python expression string, e.g., "state['score'] > 5"
    # Actually, simpler branching model: 
    # Usually edges are a list. A node can have multiple outgoing edges. 
    # If multiple, we check conditions. The first one that matches wins. 
    # If no condition, it's a default path.

class Node(BaseModel):
    id: str
    tool_name: str # Name of the function in registry

class GraphDefinition(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    start_node: str

class WorkflowRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

class WorkflowStateResponse(BaseModel):
    run_id: str
    status: str # "running", "completed", "failed"
    state: Dict[str, Any]
    history: List[str] # List of node_ids executed
