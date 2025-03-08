import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Getting credentials from environment variables
SERVICENOW_URL = os.getenv("SERVICENOW_INSTANCE")
USER = os.getenv("SERVICENOW_USERNAME")
PWD = os.getenv("SERVICENOW_PASSWORD")

# Check if credentials are loaded correctly
if not SERVICENOW_URL or not USER or not PWD:
    raise ValueError("ServiceNow credentials are missing. Set environment variables")

# URL to the incident table
INCIDENT_API_URL = f"{SERVICENOW_URL}/api/now/table/incident"

# Function to fetch incident
def get_incident(incident_ids):
    """
    Fetch incidents from ServiceNow using their incident ids
    """
    incident_details = []

    for incident_id in incident_ids:
        incident_url = f"{INCIDENT_API_URL}?sysparm_query=number={incident_id}"

        headers = {
            "Accept": "application/json"
        }

        response = requests.get(incident_url, auth=(USER, PWD), headers=headers)

        #print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if "result" in data and data["result"]:
                incident = data["result"][0]

                incident_details.append({
                    "close_notes": incident.get("close_notes", "No resolution provided"),
                })
            else:
                incident_details.append({"incident_number": incident_id, "error": "Incident not found"})
        else:
            incident_details.append({"number": incident_id, "error": f"{response.status_code} - {response.text}"})
    return incident_details

# Example usage
#incident_ids = ["INC0010015", "INC0008111", "INC0000001", "INC0000002"]
#incident = get_incident(incident_ids)
