# import json
# from utils import retry_on_json_error


# @retry_on_json_error
# def determine_objective(openai_model, prompt, chance, previous_conversation):
#     initial_template = f"""
#     {"objective":"string",
#      "general_chat_response":"string"}
#     """
   
#     parsed_text = openai_model.client_open_ai.chat.completions.create(
#         model="gpt-4o",
#         temperature=0.0000000001,
#         response_format={ "type": "json_object" },
#         messages=[
#             {"role": "system", "content": "You are an expert in refining survey objectives. Your task is to analyze the given objective, ask clarifying questions if needed, and ensure all key details are covered before generating a final structured survey plan."},
#             {"role": "user", "content": f"""
            

#             {f"The user has provided the following initial objective for the survey: {prompt}" if chance == 1 else ""}
#             {f"This is a refined objective after the fisrt chance and now the refined objective is: {prompt}" if chance == 2 else ""}
#             {f"This is a refined objective after the second chance and now the refined objective is: {prompt}" if chance == 3 else ""}
#             Your task is to: 
#             1. Analyze this objective and determine if it is clear and complete. 
#             2. If important details are missing (such as target audience, key themes, or purpose), ask follow-up questions to gather that information. 
#             3. You have **three chances** to refine the objective by engaging with the user. and this is your "{chance}" chance.

#             {"I am also attaching the previous conversation history to give you an idea of the previous conversation. The previous conversation is as follows: " + previous_conversation if previous_conversation else ""}
#             {"This is your last chance to understand the objective. Please make the best use of it and ask appropriate questions to the user." if chance == 3 else ""}
#             {"This is your second chance out of three to understand the objective. Please make the best use of it and ask appropriate questions to the user." if chance == 2 else ""}
#             {"This is your first chance out of three to understand the objective. Please make the best use of it and ask appropriate questions to the user." if chance == 1 else ""}
#             {f"Start by analyzing the given objective and, if necessary, ask the + {chance} + follow-up question." if chance <= 3 else ""}
#             {f"in the general_chat_response, please give the initial response to the user and ask your corresponding questions to get down all the details." if chance <=3 else " in the general_chat_response, please give the final response to the user and state that you've understood the user's objective and you will now proceed to generate appropriate sections for the survey. this is just a message you dot have to generate any sections, you just have to professionaly convey the message to the user, donot include the objective in the general_chat_response"}
#             please follow the following format for the response, please keep refining the objective until you get the best possible objective, i will reshare this objective till three chances are over: and you should keep refining the objective or maybe keep adding on to it: {initial_template}

#             """}
#         ]
#     )

#     content = parsed_text.choices[0].message.content
#     result = json.loads(content)
#     return result





import json
from utils import retry_on_json_error

@retry_on_json_error
def determine_objective(openai_model, prompt, chance, previous_conversation):
    initial_template = """
{"objective":"string",
"general_chat_response":"string"}
    """
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are an expert in refining survey objectives. Your task is to analyze the given objective, ask clarifying questions if needed, and ensure all key details are covered before generating a final structured survey plan."},
            {"role": "user", "content": f"""
{f"The user has provided the following initial objective for the survey: {prompt}" if chance == 1 else ""}
{f"This is a refined objective after the fisrt chance and now the refined objective is: {prompt}" if chance == 2 else ""}
{f"This is a refined objective after the second chance and now the refined objective is: {prompt}" if chance == 3 else ""}
Your task is to:
1. Analyze this objective and determine if it is clear and complete.
2. If important details are missing (such as target audience, key themes, or purpose), ask follow-up questions to gather that information.
3. You have **three chances** to refine the objective by engaging with the user. and this is your "{chance}" chance.
{"I am also attaching the previous conversation history to give you an idea of the previous conversation. The previous conversation is as follows: " + previous_conversation if previous_conversation else ""}
{"This is your last chance to understand the objective. Please make the best use of it and ask appropriate questions to the user." if chance == 3 else ""}
{"This is your second chance out of three to understand the objective. Please make the best use of it and ask appropriate questions to the user." if chance == 2 else ""}
{"This is your first chance out of three to understand the objective. Please make the best use of it and ask appropriate questions to the user." if chance == 1 else ""}
{f"Start by analyzing the given objective and, if necessary, ask the {chance} follow-up question." if chance <= 3 else ""}
{f"in the general_chat_response, please give the initial response to the user and ask your corresponding questions to get down all the details." if chance <=3 else "in the general_chat_response, please give the final response to the user and state that you've understood the user's objective and you will now proceed to generate appropriate sections for the survey. this is just a message you dot have to generate any sections, you just have to professionaly convey the message to the user, donot include the objective in the general_chat_response"}
please follow the following format for the response, and give me a valid json object, please keep refining the objective until you get the best possible objective, i will reshare this objective till three chances are over: and you should keep refining the objective or maybe keep adding on to it: {initial_template}
            """}
        ]
    )
    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result