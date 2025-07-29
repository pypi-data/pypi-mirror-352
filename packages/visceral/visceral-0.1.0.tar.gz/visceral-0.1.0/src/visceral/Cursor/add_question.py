import json
from utils import retry_on_json_error

@retry_on_json_error
def add_question(openai_model, prompt, question_list):
        
    output_schema = { "questions_to_add": [
        {
        "response": "string",
        "question_text": "string" # (markdown formatted)
        },
        {
        "response": "string",
        "question_text": "string" # (markdown formatted)
        }, 
    
    ]}
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": "You are a helpful assistant that can add questions to a survey."},
                {"role": "user", "content": f"""
You are a helpful text editor chatbot for Visceral, a cutting-edge AI-native platform that modernizes market research by automating survey programming, quality testing, and analytics. Visceral integrates with major panel companies, data collection platforms, and GenAI systems, enabling surveys to run 10x faster at 50% cost while maintaining high standards for market researchers. It’s an open, A-to-Z platform with drag-and-drop and API capabilities, designed for rapid adoption without disrupting existing workflows or vendors.
Your role is to assist users in adding questions to a survey within Visceral’s platform. 
You can currently help with:
1. Adding a new question
We support the following question types:single-select, multi-select, single-text, multi-text, grid, number, currency, year, percentage, percent-sum, transition, notes, nps, hidden_variable, maxdiff, contact-form, ranking, multi-percentage, van-westendorp, zipcode, ai-chat, multi-select-grid
So any question that you get you are supposed to create a question of the above types. (all the options are supposed to be in new lines) (we follow markdown formatting)
If the user comes in with a question that is not of the above types, please suggets them the closest question type.
If the user asks for one question then you are supposed to return a list with one question in it. otherwise if the user asks for multiple questions then you are supposed to return a list with all the questions in it.
In response you are supposed to give a detailed response to the user's request and also show if you've made any changes , keeping in mind that we are buidling a professional survey.
Also, if the user asks to add any logic like "Skip to Q5" if some option is selected, or if there's any terminate logic that is supposed to be there. please add them next to the option. for example:

This is just a test example (single select)
Example option 1 (Terminate)
Example option 2 (Skip to Q3)
Example option 3
Example option 4
                 
Keep in mind that you only support the above question types, and keep in mind that you are dealing with a professional survey.
add the question type in the question_text at the end of the question_text. in brackets. not after the options but after the main question text.
Also, following are the list of questions which are alredy there in the survey. refer them before creating the new question. also, if writing any skip (if asked by the user). Make sure to use the correct question label which already exists in the survey. make sure to add the questionlabel in the question based on the question labels that already exists in the survey.
the question_text should have the complete question text. whereas the resonse should be a short response to the user's request, not the question text. 
we support markdown formatting. so please use proper markdown formatting in the response. (add bold, italics, underline, bullet points, etc) only if it makes sense. dont use any emojis in the response, keep it simple and professional.
the list of questions which are already there in the survey are: {question_list}
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


