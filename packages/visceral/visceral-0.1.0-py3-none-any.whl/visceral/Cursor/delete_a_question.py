import json
from utils import retry_on_json_error

@retry_on_json_error
def delete_question(openai_model, prompt):
        
    output_schema = {
       "question_label": "string",
     
    }
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": "You are a helpful assistant that can help the user delete a question from the survey."},
                {"role": "user", "content": f"""

You are a helpful text editor chatbot for Visceral, a cutting-edge AI-native platform that modernizes market research by automating survey programming, quality testing, and analytics. Visceral integrates with major panel companies, data collection platforms, and GenAI systems, enabling surveys to run 10x faster at 50% cost while maintaining high standards for market researchers. It’s an open, A-to-Z platform with drag-and-drop and API capabilities, designed for rapid adoption without disrupting existing workflows or vendors.
Your role is to assist users in editing survey content within Visceral’s platform. 
You can currently help with:
1. deleting a question
You will be given a question text and your goal is to find the question label for the question that the user wants to delete.
question label is the text that appears before the question text.
                 1. Question Label**  
                - Extract the exact identifier at the start (e.g., `"Q1"`, `"5Kn"`, etc.).
                 
please give me a valid response in a json format.
the user's message is: {prompt}
follow this output schema strictly:
{json.dumps(output_schema)}


                """
                }
            ]
        )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result


