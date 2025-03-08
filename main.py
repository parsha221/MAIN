from typing import List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from servicenow import get_incident

class InitializeState(TypedDict):
    alarm_list: List[Dict[str, Any]]

class ProcessState(TypedDict):
    incident_ids: List[str]

class State(TypedDict):
    incident_ids: List[str]
    incident_details: List[Dict[str, Any]]

class PrivateState(TypedDict):
    inc_det: List[Dict[str, Any]]

def initialize_state(alarm_list: List[Dict[str, Any]]) -> InitializeState:
    alarm_list1 = [
        {"alarm_id": 1, "device_id": "Device_1", "alarm_type": "Critical", "description": "CPU usage above threshold", "severity": "High", "incident_id": "INC0000004"},
        {"alarm_id": 2, "device_id": "Device_2", "alarm_type": "Warning", "description": "Memory usage above threshold", "severity": "Medium"},
        {"alarm_id": 3, "device_id": "Device_3", "alarm_type": "Info", "description": "Disk space below threshold", "severity": "Low"},
        {"alarm_id": 4, "device_id": "Device_4", "alarm_type": "Critical", "description": "Network failure", "severity": "High", "incident_id": "INC0000004"},
    ]
    return {"alarm_list": alarm_list1}

def process_state(state: InitializeState) -> ProcessState:
    alarm_list = state["alarm_list"]
    incident_ids = [alarm["incident_id"] for alarm in alarm_list if "incident_id" in alarm]
    return {"incident_ids": incident_ids}

def fetch_incidents_node(state: ProcessState) -> PrivateState:
    incident_ids = state.get("incident_ids", [])
    incident_details = get_incident(incident_ids)
    
    formatted_incident_details = []
    for incident in incident_details:
        formatted_incident_details.append({
            "role": "system",
            "content": incident.get("close_notes", "No resolution provided")
        })
    
    inc_det = {"inc_det": formatted_incident_details}
    return inc_det

# Defining Graph
graph_builder = StateGraph(State)
graph_builder.add_node("initialize_state", initialize_state)
graph_builder.add_node("process_state", process_state)
graph_builder.add_node("fetch_incidents", fetch_incidents_node)

graph_builder.add_edge(START, "initialize_state")
graph_builder.add_edge("initialize_state", "process_state")
graph_builder.add_edge("process_state", "fetch_incidents")
graph_builder.add_edge("fetch_incidents", END)

# Compiling the graph
graph = graph_builder.compile()

# Function to run the graph and print the output in the terminal
def run_graph():
    initial_state = initialize_state([])
    process_state_result = process_state(initial_state)
    final_state = fetch_incidents_node(process_state_result)
    return final_state["inc_det"]

# Running the graph and printing the output
if __name__ == "__main__":
    incident_details = run_graph()
    print(incident_details)
