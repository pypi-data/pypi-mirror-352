import json
from utils import retry_on_json_error

@retry_on_json_error
def add_section(openai_model, prompt):
        
    output_schema = {         
    "section_name":"string", # recommend me the name of the section we are creating, keep in mind that the name should be unique and not repeated. I am sharing with you a list of sections names that already exist in the survey.
    "number_of_questions":"integer", # the number of questions we are creating, example 7
    "details_about_section":"string" # detailed information about the section we are creating, include as many details as possible including any terminates we should focus on etc.
    }
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": "You are an expert in creating survey questions and sections. You are given a user's objective and you have to create a section of questions that can be used to accomplish the objective."},
                {"role": "user", "content": f"""
you have to critically think about the questions you are creating, if they are able to accomplish the objective. The survey should be able to accomplish the objective.
You represent Visceral, a cutting-edge AI-native platform that modernizes market research by automating survey programming, quality testing, and analytics. Visceral integrates with major panel companies, data collection platforms, and GenAI systems, enabling surveys to run 10x faster at 50% cost while maintaining high standards for market researchers. It’s an open, A-to-Z platform with drag-and-drop and API capabilities, designed for rapid adoption without disrupting existing workflows or vendors.
Your role is to assist users in creating a section of questions that can be used to accomplish the objective.
You can currently help with:
1. Adding a new section with questions in it. (we can support upto  100 questions in a section for now)

Some rules to follow:
1. Keep the introduction(if any) minimal and high-level.
2. First section usually should be a screener section.
3. Each question should focus on one topic only (no double-barreled questions)
4. Avoid Yes/No questions unless asking about factual information (to reduce bias).
5. Use response options that are mutually exclusive and exhaustive.
6. Avoid jargon or technical terms — keep language simple and clear.
8. Randomize list options when appropriate (not for items that follow a natural sequence).
9. Avoid overusing MaxDiff, grid question- use sparingly. max of 1 max-diff and a couple of grid questions in the survey
10. When appropriate, ask about both current behavior/perceptions and future expectations.
                 
your goal is to tell how many questions you think will be best fit for the section we are creating (If not explicitly mentioned by the user). mention the number of questions in the number_of_questions field. keep in mind that you are making a professional survey and we have to think critically about the questions we are creating.

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


