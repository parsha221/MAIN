from typing import List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from servicenow import get_incident

# Define the State Types
class InputState(TypedDict):
    alarm_list: List[Dict[str, Any]]

class OverallState(TypedDict):
    alarm_list: List[Dict[str, Any]]
    incident_ids: List[str]
    incident_details: List[Dict[str, Any]]

class OutputState(TypedDict):
    incident_details: List[Dict[str, Any]]

# Function to Initialize State
def initialize_state(state: InputState) -> OverallState:
    alarm_list = state["alarm_list"]
    incident_ids = [alarm["incident_id"] for alarm in alarm_list if "incident_id" in alarm]
    return OverallState(alarm_list=alarm_list, incident_ids=incident_ids, incident_details=[])

# Function to Fetch Incident Details
def fetch_incidents_node(state: OverallState) -> OverallState:
    incident_ids = state.get("incident_ids", [])
   
    # Fetch incident details using the incident_ids
    incident_details = get_incident(incident_ids)
   
    # Format the Incident Details
    formatted_incident_details = []
    for incident in incident_details:
        formatted_incident_details.append({
            "role": "system",
            "content": incident.get("close_notes", "No resolution provided")
        })
   
    # Ensure that we return the state with both incident_ids and incident_details
    state["incident_details"] = formatted_incident_details
    return state

# Function to Output State
def output_state(state: OverallState) -> OutputState:
    return OutputState(incident_details=state["incident_details"])

# Define the State Graph
graph_builder = StateGraph(OverallState, input=InputState, output=OutputState)
graph_builder.add_node("initialize_state", initialize_state)
graph_builder.add_node("fetch_incidents", fetch_incidents_node)
graph_builder.add_node("output_state", output_state)

# Define the edges for the state graph
graph_builder.add_edge(START, "initialize_state")
graph_builder.add_edge("initialize_state", "fetch_incidents")
graph_builder.add_edge("fetch_incidents", "output_state")
graph_builder.add_edge("output_state", END)

# Compile the graph
graph = graph_builder.compile()

# Example usage of the state graph
alarm_list1 = [
    {"alarm_id": 1, "device_id": "Device_1", "alarm_type": "Critical", "description": "CPU usage above threshold", "severity": "High", "incident_id": "INC0000004"},
    {"alarm_id": 2, "device_id": "Device_2", "alarm_type": "Warning", "description": "Memory usage above threshold", "severity": "Medium"},
    {"alarm_id": 3, "device_id": "Device_3", "alarm_type": "Info", "description": "Disk space below threshold", "severity": "Low"},
    {"alarm_id": 4, "device_id": "Device_4", "alarm_type": "Critical", "description": "Network failure", "severity": "High"},
]

# Execute the Graph
answer = graph.invoke({"alarm_list": alarm_list1})
print(answer)
