# import json
# from utils import retry_on_json_error

# @retry_on_json_error
# def recommend_sections(openai_model, user_objective, block_names, previous_conversation):
        
#     output_schema = {         
#     "recommend_sections_schema": [          
#     {"section_name":"string", # recommend me the name of the section we are creating, keep in mind that the name should be unique and not repeated. I am sharing with you a list of sections names that already exist in the survey.
#     "number_of_questions":"integer", # the number of questions we are creating, example 10
#     "details_about_section":"string" # Add as many details as possible about the section we are creating, including any specific focuses or terminologies we should pay attention to. 
#     },
#     {"section_name":"string", #add this section only if required based on the user's objective.
#     "number_of_questions":"integer", 
#     "details_about_section":"string" 
#     } ]
#     }

#     parsed_text = openai_model.client_open_ai.chat.completions.create(
#         model="gpt-4o",
#         temperature=0.0000000001,
#         response_format={ "type": "json_object" },
#         messages=[
#                 {"role": "system", "content": "You are an expert in creating survey questions and sections. You are given a user's objective and you have to create a section of questions that can be used to accomplish the objective."},
#                 {"role": "user", "content": f"""
# You are an expert in creating survey questions and sections. You are given a user's objective and you have to create a section of questions that can be used to accomplish the objective, You represent Visceral a cutting-edge AI-native platform that modernizes market research by automating survey programming, quality testing, and analytics. Visceral integrates with major panel companies, data collection platforms, and GenAI systems, enabling surveys to run 10x faster at 50% cost while maintaining high standards for market researchers. It’s an open, A-to-Z platform with drag-and-drop and API capabilities, designed for rapid adoption without disrupting existing workflows or vendors.
# Your role is to assist users in adding new sections to a survey within Visceral’s platform. Our main  goal is to create a survey that can accomplish the user's objective. Visceral helps market researchers reach their objective.
# You can currently help with:
# 1. Adding a new sections with questions in it. (we can support upto  100 questions in a section for now)
# your goal is to determine how many questions you think will be best fit for each section we are creating. add it in the number_of_questions field. keep in mind that you are making a professional survey. if the objective or conversation explictly says to create long or short surveys then your response should be based on that. Short surveys are just 1 seciton with maximum 10 questions or based on user's input. 
# the list of sections names that already exist in the survey are: {block_names if block_names else "No sections exist in the survey"}
# The user's objective for making the survey is: {user_objective}
# if the user explicitly mentions the number of section, question etc. please follow it strictly. 
# on an average if nothing is mentioned about the lenght of the survey, you should create a survey with 3 sections and roughly 10 questions per section.
# change if the user explicitly mentions the number of sections, questions or talks about a longer survey.
# Also, the user's conversation history is, please make sure you understand what the user wants. the previous conversation is: {previous_conversation}
# please give me a valid response in a json format.
# Please pay special attention to the user's objective and if it states the number of question, or short or long and the number of sections. be sma
# The most important thing to keep in mind is that the survey should be able to accomplish the objective. You have to think critically aboout the sections and questions we are creating.
# You should focus on creating quality questions that can be used to accomplish the objective. we have to absolutely avoid any bias in the questions. and make sure we are able to accomplish the objective. Dont focus on longer surveys(until the user explicitly mentions it). Focus on quality.
# follow this output schema strictly:
# {json.dumps(output_schema)}


#                 """
#                 }
#             ]
#         )

#     content = parsed_text.choices[0].message.content
#     result = json.loads(content)
#     return result




import json
from utils import retry_on_json_error

@retry_on_json_error
def recommend_sections(openai_model, user_objective):
        
    output_schema = {         
        "recommend_sections_schema": [          
            {
                "section_name": "string",  # Unique name for the new section. Should not duplicate any existing section name.
                "number_of_questions": "integer",  # Number of questions in this section. Example: 10
                "details_about_section": "string"  # Detailed description of what this section should cover, including specific focuses, terminologies, or considerations.
            },
            {
                "section_name": "string",  # Include a second section only if needed based on the user's objective.
                "number_of_questions": "integer",
                "details_about_section": "string"
            }
        ]
    }

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert in creating high-quality survey sections and questions. "
                    "You assist users by recommending new sections to add to their surveys, ensuring that the survey accomplishes the user's research objective."
                )
            },
            {
                "role": "user",
                "content": f"""
You represent Visceral, an AI-native platform that modernizes market research by automating survey programming, quality testing, and analytics. Visceral integrates with major panel companies, data collection platforms, and GenAI systems, enabling surveys to run 10x faster at 50% cost, while maintaining high-quality standards. The platform offers drag-and-drop and API capabilities for rapid adoption without disrupting existing workflows.

Your task:
- Recommend one or more new **survey sections** based on the user's research objective.
- Focus on **high-quality**, **unbiased** questions that **help achieve the user's objective**.
- Follow the provided output schema strictly: {json.dumps(output_schema)}.

Important guidelines:
- **Section names must be unique** and should not duplicate existing sections. 
- If the user specifies a number of sections or questions, **follow it exactly**.
- If the user requests a "short survey", create **only 1 section** with **up to 8 questions** (unless specified otherwise).
- If nothing is mentioned about survey length, **default** to creating **2 sections** with about **8 questions** each.
- You may recommend a second section **only if it helps accomplish the objective**.
- **Maximum per section: 100 questions**.
- Be thoughtful about how each section relates to the objective.

Some rules to follow:
1. First section usually should be a screener section.
2. Organize questions into clear, thematic sections.
3. Avoid overusing MaxDiff, grid question- use sparingly. max of 1 max-diff and a couple of grid questions in the survey




- **Critical Thinking Required:**  
Design each section thoughtfully to genuinely accomplish the user's objective. Prioritize **quality and focus** over quantity.
Rememeber you are an expert in survey design and you have to create a survey that can accomplish the users objective.

General advice:
- Prioritize quality and relevance over quantity.
- Avoid any bias in questions.
- Think critically about how the sections together will accomplish the objective.

The user's objective is: {user_objective}

Please return the response **strictly as a valid JSON object** matching the output schema.
                """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result
