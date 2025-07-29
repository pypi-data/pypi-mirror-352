import json
from utils import retry_on_json_error

@retry_on_json_error
async def correction_prompt_via_chat(openai_model, question_text, instructions, previous_conversation=None):
    output_schema = {
        "chat": "string",
        "corrected_question": "string",
        "question_type": "string"
    }

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful assistant that corrects survey questions."},
            {"role": "user", "content": f"""
            We are dealing with survey questions. You will be given a `question_text` and a user-provided `instructions` specifying a correction, along with a `selected_question_text` where the correction applies. Your task is to:
            - Update the `question_text` according to the `instructions` and provide the full revised text in `corrected_question`.
            - Include a brief conversational `chat` line to start the response and make it specific to the question, maybe add the question label too?.
            - Optionally, If the `instructions` are unclear or invalid, reflect this in `corrected_question` and use `chat` to ask clarifying questions only if genuinely confused.
            - You will also be receiving a `question_type` which will be one of the following: single-select
                multi-select
                single-text
                multi-text
                grid
                number
                currency
                year
                percentage
                percent-sum
                transition
                notes
                nps
                hidden_variable
                maxdiff
                contact-form
                ranking
                multi-percentage
                van-westendorp
                zipcode
                ai-chat
                multi-select-grid
           
            - Ensure strings are clear and readable. Apply Markdown formatting within strings only if specified in `instructions`.
            - Previous conversation is for you to refer the user's conversation and what and how he wants to edit the question: {previous_conversation if previous_conversation else "No previous conversation"}
            - If you're adding any options, please make sure to add them like a linear list, just what we have in a survey question. donot create multiple lists.
            - If the user asks to add a terminate or a skip logic to any option, please write it next to the option in the same line. But, if the the question does not have any option, then please add it as a new line with the logic. 
            - when adding options, please add them in new lines. 
            Inputs:
            - question text: {question_text}
            - instructions: {instructions}
            Follow this output schema strictly:
            {json.dumps(output_schema)}

            Return a valid JSON object with the full corrected question text in `corrected_question`.
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result