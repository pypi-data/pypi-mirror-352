import json
from utils import retry_on_json_error


@retry_on_json_error
def maxdiff_question(openai_model, prompt,sync_layer, general_tagged):
    schema = """
    {
        "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
        "questionLabel": "string",  # Capture the label exactly as it appears.
        "question": "string",  # Capture the main question text that we will be showing to the user taking the survey.
        "options": 
            {"full_option_text": "None"}
        ,
        "type":"max_diff"
        "keymap": "string"
    }
    """

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are processing survey questions and will receive raw question text. Your task is to structure the question into a JSON format"},
            {"role": "user", "content": f"""
                You are a detailed survey question parser. 
                
                The schema is : {schema}
                
                Sync_json guides you on capturing question_text (which maps to question in our JSON), logics, and options. Use the provided output as a reference to ensure proper mapping. Your output must align with it, especially for question, options, and logics. sync_json is : {sync_layer}.
                
                PARSING RULES:

                1. Question Label:
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.)
                - Keep it exactly as written

                2. Question Text:  
               - The question_text in sync_json should be used in the question field of the json. 

                3. Options:
                - Be smart enough to understand the options from the text.
                - Create a list of dictionaries where each option is a key and value as None
                - example {{"Option text": None}}
                - example {{"Option text (Skip to Q4)": None}}
                - example: {{"Option text Terminate": None}}
                
               
                Capture any ask if logic in the ask_logic variable. By 'ask if' logic, I mean any statement that determines when a question should be asked.
                Important: please capture "sets" which is how many times we need to show them this question, "features" which means how many options will be shows at one screen, "upperText" is the text user wants to show on screen for upper limit, "lowerText" is the text user wants to show for lower limit. If not given it will be "Most Important" and "Least Important", Capture the number of "designs" if not given it will be 1 and capture all the options.
                
                
                5. Piping Logic

                If a question explicitly references options from a previous question, add a "piping" field. any question, which asks to fill it's options from previous question it means it is a a piping question. then please add a field piping with a dictionary where the  key is the questionLabel from which we have to fetch responses. and value could be any from these 4: [show selected, show not selected, hide selected, hide not selected].
                for example . you see something like this in a text: "Show all selected in QM. " then your json will have a field like : piping : {{"QM":"show selected" }}
                
                Examples:

                Input:
                ``` Ask Qm if QN==01 \n
                QM. Demo Question (Disqualify if <1) Randomize \n (Create 5 screens with 3 benefits listed per screen)
                1. option a 
                2. option b 
                3. option c 
                Must select one option 
                ```
             
                
                for the option you dont have to use backticks.it will be dictionary.
                Output:
                {{
                    "ask_logic"="Ask Qm if QN==01",
                    "questionLabel": "QM",
                    "question": "Demo Question? ",
                    "options": [
                        {{"option a": None}},
                        {{"option b": None}},
                        {{"option c": None}}
                    ],
                    "extra_text": "Must select one option",
                    "sets": 5,
                    "features":3,
                    "upperText": "Most Important",
                    "lowerText": "Least Important",
                    "type":"max_diff"
                    
                }}
                
                 
               
                Important: there can be multiple ways of writing a logic, you have to understand if it means terminate, skip to.. , randomize or if the user wants to show the question as dropdown.
              
                Important: please give me a valid json.
                Also, here are some special mentions by the user: pay special attention and include them as well: {general_tagged}.
                
                Parse the following survey question according to these rules: {prompt}
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result




# def maxdiff_logic(openai_model, input_json,user_logic):
    

#     parsed_text = openai_model.client_open_ai.chat.completions.create(
#         model="gpt-4o",
#         temperature=0.0000000001,
#         response_format={ "type": "json_object" },
#         messages=[
#             {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
#             {"role": "user", "content": f"""


#             You will be receving a json which has max_diff question , your task is to understand any logics if they exist and put it in the bucket of logics we currently support.
             

            
#             be sure to smartly understand what the user is trying to mean with that option. There can be multiple ways to say all these logics.
#             Important : Apart from that: Ill be sharing with you the users way of writing a logic for the survey. So you should be smart enough to understand what the user is trying to say and then make our json.
#             Important : The users way of writing the logic is : {user_logic} make sure to only use the words as logics which are explicitly mentioned
#             please pay special attention while assigning logics. 

#             example input option: {{"pizza (loppy)":None}} and the user marks loppy as disqualify then your output will be : {{"pizza `(loppy)`:"THANK AND END"}}. in the key, you only have to wrap the logic in backticks if you can identify it. otherwise no need for example: {{"pizza (choppy)":None}} and we dont identify any logic here so we will not wrap the logic with backticks. the output will be  {{"pizza (choppy)":None}}
            
#             For complete and disqualify -> we will use "THANK AND END" in our final json that we produce and for skip we use "SKIP TO [qstnLabel]" . 
#             Be sure to understand how a user writes the logic. 
#             Use you general understanding and the user_logic way of writing the logic. 
#             Also, if the logic is not in english. please understand it properly
        
#             Very Important: You are not supposed to add any new options on your own, just deal with whatever you have.
            
#             for example if you get an input that has only one option like 'options': {{'una ..1': None}} then you are not supposed to add any new options. 
#             Most Important: No data should be deletd, not even a single dot.
#             Important : you are not supposed to change the logic field in the json.

            
#             important: "Did not vote" or "None" ,"exclusive" anything like that doesnt always mean disqualified. until it is explicitly mentioned.
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