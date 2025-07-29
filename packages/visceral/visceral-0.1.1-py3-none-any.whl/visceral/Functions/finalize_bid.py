import requests

def finalize_bid(survey_id, authorization, team_id, bid_id):
    url = f"https://visceralos.com/survey/{survey_id}/bid/{bid_id}"
    
    headers = {
        "Authorization": authorization,
        "team_id": str(team_id),
        "Content-Type": "application/json" 
    }
    
    payload = {
        "accepted": True
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response_data = response.json()
        print("response_data from finalize_bid", response_data)
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
        print(f"Response url: {url}")
       
        return response_data
        
    except requests.exceptions.RequestException as e:
        print("error in finalize_bid", e)
        return None
        

