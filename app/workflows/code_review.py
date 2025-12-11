from app.registry import register_tool
from app.schemas import GraphDefinition, Node, Edge
from typing import Dict, Any
import random

# --- Tools ---

@register_tool("extract_functions")
def extract_functions(state: Dict[str, Any]):
    code = state.get("code", "")
    # Mock extraction
    return {"functions": ["func_a", "func_b"], "log": state.get("log", []) + ["Extracted functions"]}

@register_tool("check_complexity")
def check_complexity(state: Dict[str, Any]):
    # Mock complexity check
    return {"complexity": 5, "log": state["log"] + ["Checked complexity"]}

@register_tool("detect_issues")
def detect_issues(state: Dict[str, Any]):
    current_quality = state.get("quality_score", 0)
    # Simulate improvement or random quality
    # First run might be low, subsequent runs higher
    new_quality = current_quality + 20
    if new_quality > 100: new_quality = 100
    
    return {
        "issues": ["line too long"] if new_quality < 80 else [],
        "quality_score": new_quality,
        "log": state["log"] + [f"Detected issues. Quality: {new_quality}"]
    }

@register_tool("suggest_improvements")
def suggest_improvements(state: Dict[str, Any]):
    return {
        "suggestions": ["Refactor func_a"],
        "log": state["log"] + ["Made suggestions"]
    }

# --- Definition ---

def get_code_review_graph_def() -> GraphDefinition:
    nodes = [
        Node(id="extract", tool_name="extract_functions"),
        Node(id="complexity", tool_name="check_complexity"),
        Node(id="issues", tool_name="detect_issues"),
        Node(id="suggest", tool_name="suggest_improvements"),
    ]
    
    edges = [
        Edge(from_node="extract", to_node="complexity"),
        Edge(from_node="complexity", to_node="issues"),
        # Branching/Looping
        # If quality >= 80, End (no edge = end)
        # Else, go to suggest, then back to complexity (loop)
        Edge(from_node="issues", to_node=None, condition="quality_score >= 80"), # Implicitly if matched condition and to_node is None -> End? 
        # Wait, my engine logic: if to_node is None, it breaks loop?
        # My engine logic: `if not next_node_id: break`.
        # So `to_node=None` means stop.
        
        # Else continue to suggest
        Edge(from_node="issues", to_node="suggest"), # Default if above condition fails
        
        Edge(from_node="suggest", to_node="complexity"), # Loop back
    ]
    
    return GraphDefinition(
        nodes=nodes,
        edges=edges,
        start_node="extract"
    )
