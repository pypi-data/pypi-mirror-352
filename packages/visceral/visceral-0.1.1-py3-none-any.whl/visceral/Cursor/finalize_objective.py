# import json
# from utils import retry_on_json_error

# @retry_on_json_error
# def finalize_survey_objective(openai_model, initial_objective,conversation_history):
#     final_objective_template = f"""
#     {   "general_response":"string",
#         "final_objective":"string"
#     }
#     """
#     parsed_text = openai_model.client_open_ai.chat.completions.create(
#         model="gpt-4o",
#         temperature=0.0000000001,
#         response_format={ "type": "json_object" },
#         messages=[
#             {"role": "system", "content": "You are a specialized agent responsible for evaluating and refining survey objectives. Your task is to analyze the past interactions, extract key details, and generate a well-structured final objective for the survey."},
#             {"role": "user", "content": f"""
#             The user has provided the following initial objective for the survey: {initial_objective}
#             {f"Below is the conversation history between the user and the system regarding their survey objective, including the initial objective and some follow-up interactions: {conversation_history}" if conversation_history else ""}

#             Based on this, your task is to:
#             1. Evaluate the conversation history and extract all relevant details.
#             2. Eliminate redundancies and ensure clarity.
#             3. Synthesize a final, well-structured survey objective, which should include:
#                - A clear and concise objective statement
#                - The target audience
#                - The key themes or topics the survey will cover
#                - The expected outcome or insights the survey aims to achieve

#             Your response should be a single refined objective that incorporates all relevant details in a professional and structured manner, if you dont have some information, please make sure to make an objective based on the information you have. you are the expert in this field and you should make the best use of it.
#             give me valid json response.
#             In the general_response, please give the intial response the the user it is just a message stating the user that as per your understanding the user wants to achieve the following objective, please give the final objective.
#             please follow the following format for the response: {final_objective_template}
#             """}
#         ]
#     )

#     content = parsed_text.choices[0].message.content
#     result = json.loads(content)
#     return result



import json
from utils import retry_on_json_error

@retry_on_json_error
def finalize_survey_objective(openai_model, initial_objective, conversation_history):
    final_objective_template = """
{ "general_response":"string",
"final_objective":"string"
}
    """
    
    # Build the conversation history part
    conversation_part = ""
    if conversation_history:
        conversation_part = f"Below is the conversation history between the user and the system regarding their survey objective, including the initial objective and some follow-up interactions: {conversation_history}"
    
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a specialized agent responsible for evaluating and refining survey objectives. Your task is to analyze the past interactions, extract key details, and generate a well-structured final objective for the survey."},
            {"role": "user", "content": f"""
The user has provided the following initial objective for the survey: {initial_objective}
{conversation_part}
Based on this, your task is to:
1. Evaluate the conversation history and extract all relevant details.
2. Eliminate redundancies and ensure clarity.
3. Synthesize a final, well-structured survey objective, which should include:
- A clear and concise objective statement
- The target audience
- The key themes or topics the survey will cover
- The expected outcome or insights the survey aims to achieve
Your response should be a single refined objective that incorporates all relevant details in a professional and structured manner, if you dont have some information, please make sure to make an objective based on the information you have. you are the expert in this field and you should make the best use of it.
give me valid json response.
In the general_response, please give the intial response the the user it is just a message stating the user that as per your understanding the user wants to achieve the following objective, please give the final objective.
please follow the following format for the response: {final_objective_template}
            """}
        ]
    )
    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result