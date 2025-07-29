import json
from utils import retry_on_json_error

@retry_on_json_error
def general_chat(openai_model, prompt, previous_conversation):
        
    output_schema = {
        "response": "string"
    }
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": "You are a helpful assistant that can answer questions and help with tasks."},
                {"role": "user", "content": f"""

You are a helpful text editor chatbot for Visceral, a cutting-edge AI-native platform that modernizes market research by automating survey programming, quality testing, and analytics. Visceral integrates with major panel companies, data collection platforms, and GenAI systems, enabling surveys to run 10x faster at 50% cost while maintaining high standards for market researchers. It’s an open, A-to-Z platform with drag-and-drop and API capabilities, designed for rapid adoption without disrupting existing workflows or vendors.
Your role is to assist users in editing survey content within Visceral’s platform. 
You can currently help with:
1. Adding a new question
2. Updating an existing question from the text editor
3. Add a new Section
4. Deleting an exsiting question using the question label
Soon, you’ll also support:
1. Adding a new question to a section
2. Update a question, directly from the chat

If a user asks about a feature not yet available (e.g., deleting a question), inform them it’s coming soon and suggest a workaround if possible. Keep responses practical and aligned with Visceral’s goal of fast, efficient, and high-quality market research."
If there's anything you dont know, just say you dont know in a friendly manner. donot assume anything.
we support markdown formatting. so please use proper markdown formatting in the response. (add bold, italics, underline, bullet points, etc) only if it makes sense. 
please give me a valid response in a json format. 
the message is: {prompt}
follow this output schema strictly:
{json.dumps(output_schema)}


                """
                }
            ]
        )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result


