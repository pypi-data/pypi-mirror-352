import json
import asyncio
from utils import retry_on_json_error

@retry_on_json_error
async def recommend_provider_segments(openai_model,audience,budget):
    
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        # model="o1",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a panel recommendation expert. You will be receiving a audience and you need to return the correct provder it will fall into."},
            {"role": "user", "content": f"""
            You are a panel recommendation expert. You will be receiving a audience and you need to return the correct provder it will fall into.
            We currently support the following providers:  Consumer, B2B.
            you will also be receiving the budget of the user, please make sure you return me the exact budget but without any dollar sign or commas.
            
            Please return the json in the following format:
            {{
                "provider": "provider",
                "budget": "budget"
            }}
            please give me a valid json.
            make sure you use the exact names for the providers as mentioned above.
            please mark the audience, with the correct provider. The audience is: {audience} 
            and the budget is: {budget}

            """
            }
        ]
    ) 

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result



