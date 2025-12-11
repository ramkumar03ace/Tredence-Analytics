# SimpleLangGraph

A minimal agent workflow engine built with Python and FastAPI. It supports defining workflows as graphs of nodes (tools) and edges, with shared state, branching, and looping.

## Features

- **Graph Engine**: Define workflows with nodes, edges, and condition-based transitions.
- **State Management**: Shared dictionary state passed between nodes.
- **Tool Registry**: Simple decoration-based registry for Python functions.
- **API**: FastAPI endpoints to create and run workflows.
- **Example Workflow**: "Code Review Mini-Agent" that loops until quality checks pass.

## Project Structure

```
app/
  engine.py        # Core graph execution logic
  main.py          # FastAPI application
  registry.py      # Tool registry
  schemas.py       # Pydantic data models
  workflows/
    code_review.py # Example usage
```

## Setup and Run

1. **Install Dependencies**
   It is recommended to use a virtual environment.
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install fastapi uvicorn requests
   ```

2. **Start the Server**
   ```bash
   uvicorn app.main:app --reload
   ```
   The server will start at `http://127.0.0.1:8000`.

3. **Run the Example**
   Open a new terminal and run the test script:
   ```bash
   python test_workflow.py
   ```
   This script:
   - Fetches the pre-loaded "Code Review" graph ID.
   - Triggers a run with initial state.
   - Prints the execution history and final state.

## API Endpoints

- `POST /graph/create`: Create a new workflow definition.
- `POST /graph/run`: Execute a workflow.
- `GET /graph/state/{run_id}`: Get the status and state of a run.

## Workflow Capabilities

- **Nodes**: Wrappers around registered Python functions.
- **Edges**: Directed connections. Can be unconditional or conditional (Python expression).
- **Looping**: Cycles in the graph are supported (e.g., A -> B -> A).
- **Branching**: A node can have multiple outgoing edges with different conditions.

## Future Improvements

- **Persistence**: Store graphs and runs in a database (SQLite/PostgreSQL) instead of memory.
- **Async Support**: Make the engine fully async to better handle I/O bound tools.
- **Visualization**: React frontend to visualize the graph structure.
- **Streaming**: WebSocket support for real-time log streaming.
