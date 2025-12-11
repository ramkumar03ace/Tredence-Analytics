from fastapi import FastAPI, HTTPException
from app.schemas import GraphDefinition, WorkflowRunRequest, WorkflowStateResponse
from app.engine import engine
from app.workflows.code_review import get_code_review_graph_def
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SimpleLangGraph")

# Pre-load the Code Review workflow
code_review_graph_id = None

@app.on_event("startup")
def startup_event():
    global code_review_graph_id
    # Register/Create the example graph
    definition = get_code_review_graph_def()
    code_review_graph_id = engine.create_graph(definition)
    logger.info(f"Initialized Code Review Graph with ID: {code_review_graph_id}")

@app.post("/graph/create")
def create_graph(definition: GraphDefinition):
    graph_id = engine.create_graph(definition)
    return {"graph_id": graph_id}

@app.post("/graph/run")
def run_graph(request: WorkflowRunRequest):
    try:
        # If user passes "code_review" as graph_id (for convenience), map it
        gid = request.graph_id
        if gid == "code_review" and code_review_graph_id:
            gid = code_review_graph_id
            
        run_id = engine.execute_run(gid, request.initial_state)
        # Since execute_run is synchronous in my engine validation, 
        # we can fetch the final state immediately.
        # But commonly we return run_id.
        run_context = engine.get_run(run_id)
        return {
            "run_id": run_id,
            "status": run_context.status,
            "final_state": run_context.state,
            "history": run_context.history
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Run failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/state/{run_id}")
def get_run_state(run_id: str):
    context = engine.get_run(run_id)
    if not context:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return WorkflowStateResponse(
        run_id=context.run_id,
        status=context.status,
        state=context.state,
        history=context.history
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to SimpleLangGraph", "code_review_graph_id": code_review_graph_id}
