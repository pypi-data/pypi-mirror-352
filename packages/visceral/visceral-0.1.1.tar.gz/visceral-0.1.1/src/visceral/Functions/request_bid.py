import requests

def request_bid(survey_id, authorization, team_id, panel_provider_id):
    url = f"https://visceralos.com/survey/{survey_id}/request_bid"
    print("Requesting bid url is ", url)
    
    headers = {
        "Authorization": authorization,
        "team_id": str(team_id)  # Ensure team_id is a string
    }
    
    payload = {
        "panel_provider_id": panel_provider_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
       
        return response_data
        
    except requests.exceptions.RequestException as e:
        return None

