import json
import asyncio
from utils import retry_on_json_error

@retry_on_json_error
def phone_classification(openai_model,prompt):
    
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        # model="o1",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[ 
            {"role": "system", "content": "You are an intelligent text classifier that accurately determines whether 'Phone' is used as a category label or as part of a sentence, ensuring precise classification."},
            {"role": "user", "content": f"""
The input text you receive will contain the word "Phone" somewhere in the text. Your goal is to determine whether "Phone" is used as part of a sentence or as a category label.
### Examples:
Input Text:
``` What is your phone number ``` 
- Here, "Phone" is part of the sentence.
- Expected Output:
{{
    "phone": false
}}
Input Text:
``` Phone: Call them at their number ``` 
Here, "Phone" acts as a category label.
Expected Output:
             {{
    "phone": true
}}
Task:
If "Phone" is used as a category label, return {{ "phone": true }}.
If "Phone" is part of a sentence, return {{ "phone": false }}.
Ensure the output is a valid JSON object.
The input text to analyze is: {prompt} """


            }
        ]
    ) 

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result





