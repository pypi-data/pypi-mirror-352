import aiohttp
import json
import time

async def send_to_ingest_api(annotated_text, processed_question, raw_text, workspace_id, main_team_id,question_id, user_id, user_changes=False):
    question_id=str(question_id)
    url = f"https://natlanglabs--visceral-qdrant-api--learning-fastapi-app.modal.run/learning/question/{question_id}/ingest"
    
    # Construct the payload
    payload = {
        "metadata": {
            "user_id": str(user_id),
            "workspace_id":str(workspace_id),
            "team_id":str(main_team_id)
        },
        "sample": {
            "raw_text": raw_text,
            "annotation": json.dumps(annotated_text),  # Convert dict to string if needed
            "final_json": json.dumps(processed_question)  # Convert dict to string if needed
        }
    }



    # Create a ClientSession and make the request
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                url,
                params={"user_changes": str(user_changes)},
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5)  # 5 second timeout
            ) as response:
                # Fire and forget - we don't wait for or process the response
                pass
        except Exception as e:
            # Log error but don't raise it (fire and forget)
            print(f"Error sending to ingest API: {str(e)}")




