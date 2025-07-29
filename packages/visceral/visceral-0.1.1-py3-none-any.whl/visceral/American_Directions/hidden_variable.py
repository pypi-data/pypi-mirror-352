import json
from utils import retry_on_json_error

@retry_on_json_error
def hidden_variable_question_AMI(oepnai_model, prompt, general_tagged):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears, even is there's any text till we start the options, should be captured as it is. we dont want to lose any text at all, not even a single dot or bracket.
            "question": "string",  # Full question text with any logic in `{ logic: None }` format . YOU ARE NOT SUPPOSED TO DELETE ANYTHING COPY IT AS IT IS. 
            "type"="hidden_variable",
            "extra_text": "string", # Any text that does not fit into the specified categories should be captured here. The purpose of "extra_text" is to ensure no data is lost, allowing us to retain every detail from the input text, including any text or symbols that fall outside the defined structure. (if there's any logic, then make sure to wrap it in `{logic: None}`)

        }
        """

        parsed_text = oepnai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information. The most important thing is that we should not delete even a single dot. You are dealing with nps question type"},
                {"role": "user", "content": f"""
                You are a detailed survey question parser. Your task is to analyze survey questions and capture EVERY piece of text while structuring them into a specific JSON format. Follow these guidelines:

                CORE PRINCIPLES:
                1. Never delete or modify any text. WE SHOULD NOT LOSE EVEN A SINGLE DOT. we cannot delete any text at any cost.
                2. Preserve the exact structure and formatting
                3. DONOT EVEN DELETE A SINGLE BRACKET.
                 
                The schema is : {schema}

                PARSING RULES:

                1. Question Label:
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.)
                - Keep it exactly as written

                2. Question Text:
                - Include everything from the start of the question to just before the options start (if they exist). anything and everything, even if it doent make sense will be a part of the question text.
                - Even random or unrelated text must be part of the question.
                - For any logic/instructions in parentheses or brackets, wrap them in `{{"text": None}}` format
                - Example: "On a scale of 0 to 10, how likely are you to recommend our product/service to a friend or colleague? (Skip to Q3 if ==3)" becomes:
                "On a scale of 0 to 10, how likely are you to recommend our product/service to a friend or colleague? `{{"(Skip to Q3 if ==3)":None}}"

                

                3. Text After Options:
                - Capture any text that appears after the options list
                - Wrap any logic in `{{"text": None}}` format
                - Important: Text after options will exist even if there are no options, its there to capture the ending text. so that we dont lose any text.


                Important: please identify the logic (it is majoryly as a grouping logic), give me a dictionary "hidden_variable" that has key as the name of the bucket like "18-34"  (keep the name of the bucket as it is.) and value as the logic "Q5 IN [`01`,`02`] where 01 and 02 are the options labels and Q5 would be the qquestion label of that question.(assign option numbers in a serial way 01, 02 to the options accordingly.) if not the option type logic then it can be something like "Q5 > 30" where Q5 is the question Label. 
                make sure the values in the hidden_variable follow the pattern of "Q5 IN [`01`,`02`]" where we basically tell them that it belong to the group if in Q5 we selected 01 or 02. using this: "Q5 IN [`01`,`02`]"
          
                
                SPECIAL INSTRUCTIONS:
                
                - All logic must be wrapped in `{{}}` and quoted properly
                - Keep all original spacing and formatting
                - Never remove any text, even if it seems redundant, we should be capturing each and every detail. we should not delete even a single dot.

                
                important: make sure to capture logics in the `{{}}`
                Important: the text of the options will have the complete text and the value of the options will always be None. in the options you dont need to capture any logic separately. just capture the entire text as it is without deleting anything. we should not delete anything.
                Important : the value in the options will always be None
                Important: a question will be until the options start. so if there's anything till the options start should be captured in the question.
 
                
                CORE PRINCIPLES and MOST IMPORTANT:

                Never delete or modify any text: Every part of the input must be accounted for. Missing even one word is a critical error.
                Preserve structure and format: The output must follow the specified JSON schema exactly.
                
                The most important thing is that we should not lose any text!!
                Most important: Dont get stuck, if by any chance you're confused give me whatever you understand. just dont delete anything and dont be stuck
                Finally, ensure that every piece of text from the input has been captured in the JSON without any loss. If any part of the text does not fit into the defined schema, it should be included in the extra_text field. The goal is to retain all input text in its entirety.
                Also, here are some special mentions by the user: pay special attention and include them as well: {general_tagged}.
                Parse the following survey question according to these rules:  {prompt}
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result



# def hidden_variable_logic(openai_model, input_json,user_logic):
    

#     parsed_text = openai_model.client_open_ai.chat.completions.create(
#         model="gpt-4o",
#         temperature=0.0000000001,
#         response_format={ "type": "json_object" },
#         messages=[
#             {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
#             {"role": "user", "content": f"""
            



#             You will be receving a json which has nps question , your task is to understand any logics if they exist and put it in the bucket of logics we currently support.
                
            
#             be sure to smartly understand what the user is trying to mean with that option. There can be multiple ways to say all these logics.
#             Important : Apart from that: Ill be sharing with you the users way of writing a logic for the survey. So you should be smart enough to understand what the user is trying to say and then make our json.
#             Important : The users way of writing the logic is : {user_logic} make sure to only use the words as logics which are explicitly mentioned
#             please pay special attention while assigning logics. 
#             Be sure to understand how a user writes the logic. 
#             Use you general understanding and the user_logic way of writing the logic. 
#             Also, if the logic is not in english. please understand it properly
        
#             Very Important: You are not supposed to add any new options on your own, just deal with whatever you have.
#             Most Important: No data should be deletd, not even a single dot.
#             Important : you are not supposed to change the logic field in the json.
            
#             In the question if you observe any logic associated with it. please add another field saying nps_logic and for the key,value pair. For terminating the key should be Terminating and the value should be conditon but the condition will only be " [logical operator] [value]" and for skip conditions the key would be [ SKIP TO [qstnLabel] value would be " [logical operator] [value] " . 
#             The logical operator that you use should be like QuestionLabel ==, >=, <=, != , or whatever the option logic says. every opertor should have questionLabel in front of it. give me the exact logic that you get. you dont have to change any logic. make it both for Terminating or SKIP questions. Important: give me the exact logic but with questionLabel (pick it up from json) in front of every operator. keep the operators in capital like "OR"."AND". also by questionLabel : I mean the questionLabel of the question. and not "questionLabel".
                
#             Please pay special attention to the instructions for logics and make sure you mark it correctly, double check it. 
#             Important: Donot even delete a single bracket.
#             Most Important: No data should be deletd, not even a single dot.
#             The json is :{input_json}      

#             please give me the correct json. 
#             """
#             }
#         ]
#     )

#     content = parsed_text.choices[0].message.content
#     result = json.loads(content)
#     return result

