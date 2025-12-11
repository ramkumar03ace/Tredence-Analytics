import uuid
import logging
from typing import Dict, Any, List, Optional
from app.schemas import GraphDefinition, Edge
from app.registry import registry

logger = logging.getLogger(__name__)

class GraphInstance:
    def __init__(self, definition: GraphDefinition):
        self.id = str(uuid.uuid4())
        self.definition = definition
        self.nodes = {n.id: n for n in definition.nodes}
        # Organize edges by from_node for faster lookup
        self.edges_by_source: Dict[str, List[Edge]] = {}
        for edge in definition.edges:
            if edge.from_node not in self.edges_by_source:
                self.edges_by_source[edge.from_node] = []
            self.edges_by_source[edge.from_node].append(edge)

    def get_node(self, node_id: str):
        return self.nodes.get(node_id)
    
    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        return self.edges_by_source.get(node_id, [])

class RunContext:
    def __init__(self, run_id: str, graph: GraphInstance, initial_state: Dict[str, Any]):
        self.run_id = run_id
        self.graph = graph
        self.state = initial_state
        self.status = "created"
        self.history: List[str] = [] # List of node Ids
        self.step_count = 0
        self.max_steps = 50 # Prevent infinite loops

class WorkflowEngine:
    def __init__(self):
        self.graphs: Dict[str, GraphInstance] = {}
        self.runs: Dict[str, RunContext] = {}

    def create_graph(self, definition: GraphDefinition) -> str:
        graph = GraphInstance(definition)
        self.graphs[graph.id] = graph
        return graph.id

    def get_run(self, run_id: str) -> Optional[RunContext]:
        return self.runs.get(run_id)

    def execute_run(self, graph_id: str, initial_state: Dict[str, Any]) -> str:
        if graph_id not in self.graphs:
            raise ValueError(f"Graph {graph_id} not found")
        
        graph = self.graphs[graph_id]
        run_id = str(uuid.uuid4())
        context = RunContext(run_id, graph, initial_state)
        self.runs[run_id] = context
        
        self._run_loop(context)
        return run_id

    def _run_loop(self, context: RunContext):
        context.status = "running"
        current_node_id = context.graph.definition.start_node
        
        try:
            while current_node_id and context.step_count < context.max_steps:
                context.history.append(current_node_id)
                node_def = context.graph.get_node(current_node_id)
                
                if not node_def:
                    logger.error(f"Node {current_node_id} not found")
                    break
                
                # Execute Node
                tool_func = registry.get_tool(node_def.tool_name)
                if not tool_func:
                    raise ValueError(f"Tool {node_def.tool_name} not found for node {current_node_id}")
                
                # Tool receives state, returns updates to state
                # We interpret tool return value as a dict to update the state
                logger.info(f"Executing {current_node_id} (Tool: {node_def.tool_name})")
                updates = tool_func(context.state)
                if updates and isinstance(updates, dict):
                    context.state.update(updates)
                
                context.step_count += 1
                
                # Determine Next Node
                next_node_id = None
                edges = context.graph.get_outgoing_edges(current_node_id)
                
                for edge in edges:
                    if edge.condition:
                        # Evaluate condition
                        # Safe eval: we allow state access
                        try:
                            # Use state as locals
                            if eval(edge.condition, {}, context.state):
                                next_node_id = edge.to_node
                                break
                        except Exception as e:
                            logger.error(f"Error evaluating condition '{edge.condition}': {e}")
                            continue
                    else:
                        # Unconditional edge
                        next_node_id = edge.to_node
                        break
                
                current_node_id = next_node_id
            
            context.status = "completed"
        except Exception as e:
            logger.exception("Workflow failed")
            context.status = "failed"
            context.state["error"] = str(e)

# Global Engine
engine = WorkflowEngine()
