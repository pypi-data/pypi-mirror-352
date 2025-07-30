import requests
import json


async def get_learning(query, user_id,team_id,top_k=1):
    url = 'https://natlanglabs--visceral-qdrant-api--learning-fastapi-app.modal.run/learnings/get/annotation-generation'
    
    payload = {
        "query": str(query),
        "top_k": int(top_k),
        "user_id": str(user_id),
        "team_id": str(team_id)
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        
        data = response.json()
        
        # Check if learnings exist and not empty
        if not data.get('learnings') or len(data['learnings']) == 0:
            return None
            
        learning = data['learnings'][0]
        
        # Create the mapping string
        mapping_str = f"The input text was: {learning['raw_text']}\nand the output annotation was: {learning['annotation']}"
        
        return mapping_str

    except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
        print(f"Error: {e}")
        return None
