import requests
import sys

def test_workflow():
    base_url = "http://127.0.0.1:8000"
    
    print("1. Checking Root...")
    try:
        r = requests.get(base_url + "/")
        data = r.json()
        print(f"Root: {data}")
        graph_id = data.get("code_review_graph_id")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    if not graph_id:
        print("Error: Code review graph ID not found")
        return

    print(f"2. Running Workflow with Graph ID: {graph_id}")
    initial_state = {"code": "def foo(): pass", "log": []}
    
    r = requests.post(f"{base_url}/graph/run", json={
        "graph_id": graph_id,
        "initial_state": initial_state
    })
    
    if r.status_code != 200:
        print(f"Run failed: {r.text}")
        return
        
    result = r.json()
    print("Run Result:")
    print(f"Status: {result.get('status')}")
    print(f"History: {result.get('history')}")
    print(f"Final State Log: {result.get('final_state', {}).get('log')}")
    print(f"Quality Score: {result.get('final_state', {}).get('quality_score')}")

if __name__ == "__main__":
    test_workflow()
