import sys
import json
from typing import Any, Dict, Optional
import httpx
import websockets
from mcp.server.fastmcp import FastMCP
from typing import Tuple
from .request_bid import request_bid

# Initialize FastMCP server
mcp = FastMCP("visceral-mcp")


from dotenv import load_dotenv
import os

load_dotenv()  # Automatically looks for a .env file in the current dir


# Constants
API_BASE = "https://visceralos.com"
AUTH_TOKEN =  "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Mjg4LCJraW5kIjoidXNlciIsImV4cGlyZXMiOjE3NjEwNzE5MDB9.idyfUAhZbp8chzHrrn8BQCT6hH16vRTMMHcgEo9Sei_CoblGY6XA_Yecpsv24bYtk2HBccocnwqnEEtU6buZovgDEiShqCecS2UQtXLba2vYlw46yAj4Uvo24NvRJYxFN8vpnHlD4nitNcofg4e8pKnPxZzgTcpV6M_Ub0fo5H1Z1eooNRRrh7na6_BBmSM8zdFIPq_Emz0AAwq-yNsKYdS5eU4YGqiou2cQoo1MZ4eEt7r1bMJt_T_NAeSIogxK4CIuQ744XyRcBzIoC-u3vo5OPIXM_9O0Iwu-KE5HdE2eHHf3u-1dmsq9-Zz1LZwnvWtNHF8eELIlYIuQsmwSNh-bDjDqNHh6F7onLC9mOGamoe6s9h08c0jdRWBHIHR8ncDvcGmEwua8Jg_-sCqElKukpuFe1G6X5oaVNiEJEgiFU62fTQLMYqBF2-ZOzgnZNKsn_38HA7fQrnH_SwMHbzlmmoBjTMEx53rApKeFRtLU8qYDvP3nZEjc4awM638hO5zr2nH4a_bYrrtSukHpYCHmh_aOBuU7oLQkvF7dISwAWHIOnqy7ei5jKcdhiFyrOvMTgCjaDdWzCLP7rioSVbXhHz2gTelqAOXITD-TiINj5aJd4JKUGi9PSJkFqQJ4Ntykxd3-1uEl0Y0N3Xkx9rWKaKIhveoMzPjsiNjZuZY"  # You should use environment variables for this in production


TEAM_ID = "484"
# You can hardcode a workspace ID here for testing
DEFAULT_WORKSPACE_ID = "1101"  # Optional fallback


WEBSOCKET_URL = "wss://natlanglabs--create-survey.modal.run/ws"


SURVEY_API_URL = "https://natlanglabs--mcp-survey-create-survey.modal.run"




# Store created workspace IDs for later use in the session


# print(f"Debug: Starting viscera-flow server", file=sys.stderr)

@mcp.tool()
async def create_workspace(title: str) -> str:
    """Create a new workspace with the specified title.
    
    Args:
        title: The title for the new workspace
    """
    print(f"Debug: Creating workspace with title '{title}'", file=sys.stderr)
    
    url = f"{API_BASE}/workspaces"
    
    # Set up headers with team_id as a header
    headers = {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json",
        "team_id": TEAM_ID
    }
    
    # Payload with just the title
    payload = {
        "title": title
    }
    
   
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            print(f"Debug: Response status: {response.status_code}", file=sys.stderr)
            
            response.raise_for_status()
            response_data = response.json()
            
            # Store the workspace ID for later use
            workspace_data = response_data.get("workspace", {})
            workspace_id = workspace_data.get("id")
            
            
            
            return workspace_id
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            text = e.response.text
            print(f"Debug: HTTPStatusError: {status} - {text}", file=sys.stderr)
            return f"Error creating workspace: HTTP {status} - {text}"
        except Exception as e:
            print(f"Debug: Exception: {str(e)}", file=sys.stderr)
            return f"Error creating workspace: {str(e)}"



async def distribute_to_panel_providers(survey_id: str, authorization: str, team_id: str) -> str:
    """Distribute the survey to panel providers.
    Instructions: Do not print out details of the survey. Just tell the user that the survey has been distributed successfully.
    
    Args:
        survey_id: The ID of the survey to distribute
        authorization: The authorization token
        team_id: The ID of the team
    """
    panel_provider_id = "1"
    
    # Debug information
    print(f"Debug: Distributing survey {survey_id} to panel provider {panel_provider_id}", file=sys.stderr)
    
    response = request_bid(survey_id, authorization, team_id, panel_provider_id)
    if response: 
        
        
        # Create a concise summary
        
        return response
    else:
        return "Failed to submit bid request"
    

@mcp.tool()
async def create_agent(title: str, workspace_id: str) -> Tuple[str, str]:
    """Create a new agent in the specified workspace.
    
    Args:
        title: The title for the new survey agent
        workspace_id: The ID of the workspace 
        
    """
    # Determine which workspace ID to use
    target_workspace_id = workspace_id
    agent_type = "survey_v2_agent"
    
    url = f"{API_BASE}/workspace/{target_workspace_id}/agents"
    
    # Set up headers
    headers = {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json",
        "team_id": TEAM_ID
    }
    
    # Payload with title and agent type
    payload = {
        "title": title,
        "type": agent_type
    }
    

    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            print(f"Debug: Response status: {response.status_code}", file=sys.stderr)
            
            response.raise_for_status()
            response_data = response.json()
            agent_id=response_data.get("agent", {}).get("id")
            agent_id_hash=response_data.get("agent", {}).get("id_hash")
            
            return agent_id, agent_id_hash
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            text = e.response.text
            print(f"Debug: HTTPStatusError: {status} - {text}", file=sys.stderr)
            return f"Error creating agent: HTTP {status} - {text}", None
        except Exception as e:
            print(f"Debug: Exception: {str(e)}", file=sys.stderr)
            return f"Error creating agent: {str(e)}", None
        
@mcp.tool()
async def generate_survey_data(objective: str) :
    """Generate survey data using the HTTP API endpoint.
    
    Args:
        objective: The survey objective
    """
    # print(f"Debug: Generating survey with objective: '{objective}'", file=sys.stderr)
    
    url = SURVEY_API_URL
    
    # Set up headers
    headers = {
        "Content-Type": "application/json",
        
    }
    
    # Payload with objective
    payload = {
        "objective": objective
    }
    
    
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=2000.0)  # Longer timeout for survey generation
            print(f"Debug: Response status: {response.status_code}", file=sys.stderr)
            
            response.raise_for_status()
            response_data = response.json()
            # print(f"Debug: Received survey data of length {len(str(response_data.get('complete_survey_data', {})))}")
            return response_data.get("complete_survey_data", {})
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            text = e.response.text
            print(f"Debug: Survey generation HTTPStatusError: {status} - {text}", file=sys.stderr)
            raise Exception(f"Error generating survey: HTTP {status} - {text}")
        except Exception as e:
            print(f"Debug: Survey generation exception: {str(e)}", file=sys.stderr)
            raise e


async def patch_survey_to_agent(agent_id: str, survey_data) -> str:
    """Update the agent with the survey data.
    
    Args:
        agent_id: The ID of the agent to update
        survey_data: The complete survey data
    IMPORTANT: DONOT SHOW THE PAYLOAD TO THE USER.
    """
    # print(f"Debug: Updating agent {agent_id} with survey data", file=sys.stderr)
    
    url = f"{API_BASE}/agent/{agent_id}"
    
    # Set up headers
    headers = {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json",
        "team_id": TEAM_ID
    }
    
    # Payload with survey data and published flag
    payload = {
        "data": survey_data,
        "published": True
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(url, json=payload, headers=headers, timeout=120.0)

            
            return f"Survey successfully published to agent {agent_id}"
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            text = e.response.text
            print(f"Debug: HTTPStatusError: {status} - {text}", file=sys.stderr)
            return f"Error updating agent: HTTP {status} - {text}"
        except Exception as e:
            print(f"Debug: Exception: {str(e)}", file=sys.stderr)
            return f"Error updating agent: {str(e)}"
        



@mcp.tool()
async def create_survey(workspace_title: str, agent_title: str, objective: str) -> str:
    """Create a workspace and then create an agent in that workspace in one step.
    
    Args:
        workspace_title: The title for the new workspace
        agent_title: The title for the new agent

    Instructions:
    1. Understand if the user wants to use the panels by Visceral, or would they like to collect the data on their own using the link provided by Visceral.
    2. If they want to use the panels, then call the distribute_to_panel_providers function. However, if they want to collect the data on their own, then do not call the distribute_to_panel_providers function and give them the link to the survey.
    """
    # Step 1: Create workspace
    status_updates = []
    workspace_id = await create_workspace(workspace_title)
    
    # Check if workspace creation was successful by looking for "successfully" in the result
    
    
    # Extract workspace ID from the result
    
    
    
    # Step 2: Create agent in the new workspace
    agent_id_created , agent_id_hash = await create_agent(
        title=agent_title,
        workspace_id=workspace_id
       
    )

    try:
        survey_data = await generate_survey_data(objective)
        try :
            update_result = await patch_survey_to_agent(agent_id_created, survey_data)
            status_updates.append("✓ Survey generated successfully")
        except Exception as e:
            return f"Failed to generate survey: {str(e)}\n\nPartial progress: {' '.join(status_updates)}"
    except Exception as e:
        return f"Failed to generate survey: {str(e)}\n\nPartial progress: {' '.join(status_updates)}"
    
    # Final success message
    panel_provider_id =1
    if panel_provider_id == 1 or panel_provider_id == "1":
        try:
            response = await distribute_to_panel_providers(agent_id_created, AUTH_TOKEN, TEAM_ID)
            print(response)
        except Exception as e:
            return f"Failed to distribute survey to panel providers: {str(e)}"
        url=f"visceralopinions.com/{agent_id_hash}"
        return "The survey has been distributed to the panel providers. You can access it in your Visceral account. However the url for the survey is : " + url
    else:
        url=f"visceralopinions.com/{agent_id_hash}"
        return "The survey has been published to the following url: " + url
    

def main():
    """Entry point for the package"""
    print("Welcome to MCP server for Visceral", file=sys.stderr)
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()



