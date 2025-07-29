import json

def maxdiff_question(openai_model, prompt,keymap_name):
    schema = """
    {
        "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
        "questionLabel": "string",  # Capture the label exactly as it appears, even is there's any text till we start the options, should be captured as it is. we dont want to lose any text at all, not even a single dot or bracket.
        "question": "string",  # Full question text with any logic in `{logic: None}` format . YOU ARE NOT SUPPOSED TO DELETE ANYTHING COPY IT AS IT IS. 
        "options": [  # List of options (if any) with their associated logic if any
            {"full_option_text": "None"}
        ],
        "extra_text": "string", # Any text that does not fit into the specified categories should be captured here. The purpose of "extra_text" is to ensure no data is lost, allowing us to retain every detail from the input text, including any text or symbols that fall outside the defined structure. (if there's any logic, then make sure to wrap it in `{logic: None}`)
        "type":"max_diff"
        "keymap": "string"
    }
    """

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information. The most important thing is that we should not delete even a single dot"},
            {"role": "user", "content": f"""
            You are a detailed survey question parser. Your task is to analyze survey questions and capture EVERY piece of text while structuring them into a specific JSON format. Follow these guidelines:

                CORE PRINCIPLES:
                1. Never delete or modify any text. WE SHOULD NOT LOSE EVEN A SINGLE DOT. we cannot delete any text at any cost.
             
                The schema is : {schema}
                

                PARSING RULES:

                1. Question Label:
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.)
                - Keep it exactly as written

                2. Question Text:
                - Include everything from the start of the question to just before the options start. anything and everything, even if it doent make sense will be a part of the question text.
                - Even random or unrelated text must be part of the question.
                - For any logic/instructions in parentheses or brackets, wrap them in backticks like `{{"text": None}}` format
                - Example: "How old are you? (Disqualify if <18)" becomes:
                "How old are you? `{{"Disqualify if <18": None}}`"

                3. Options:
                - Be smart enough to understand the options from the text.
                - Create a list of dictionaries where each option is a key and value as None
                - example {{"Option text": None}}
                - example {{"Option text (Skip to Q4)": None}}
                - example: {{"Option text Terminate": None}}
                

                4. Text After Options:
                - Capture any text that appears after the options list
                - Wrap any logic in `{{"text": None}}` format
                - Important: Text after options will exist even if there are no options, it there to capture the ending text. so that we dont lose any text.

                
                5.Keymap: Identify and capture any exact matches of keymap variable names when they appear in the user's input text. These variables serve as predefined references within our platform.
                Important: you dont have to mention the keymap in the question text then.
                
                A keymap will always be from {keymap_name if keymap_name is not None else ": User doesnt have any keymaps defined"}
                If the user explicitly mentions the variable, it should be recognized and captured accurately.
                This behavior is distinct from "piping" and specifically focuses on detecting variable names.
                Some of the user defined key map names are : {keymap_name} and you dont have to add that variable separately in the options if given additional options.
                
                 
                
                
                Capture any ask if logic in the ask_logic variable. By 'ask if' logic, I mean any statement that determines when a question should be asked.
                please capture "sets" which is how many times we need to show them this question, "features" which means how many options will be shows at one screen, "upperText" is the text user wants to show on screen for upper limit, "lowerText" is the text user wants to show for lower limit. If not given it will be "Most Important" and "Least Important", Capture the number of "designs" if not given it will be 1 and capture all the options.
                
                SPECIAL INSTRUCTIONS:
                
                - All logic must be wrapped in backticks `{{}}` 
                - Important : The logics that we support are :  dropdown, randomize, terminate, skips. (It is possible that they can be written in some other way, for example : end also means termination) Be smart to identify.
                - Keep all original spacing and formatting
                - Never remove any text, even if it seems redundant, we should be capturing each and every detail. we should not delete even a single dot.
                

                Important: if you come across any question, which asks to fill it's options from previous question it means it is a a piping question. then please add a field piping with a dictionary where the  key is the questionLabel from which we have to fetch responses. and value could be any from these 4: [show selected, show not selected, hide selected, hide not selected].
                for example . you see something like this in a text: "Show all selected in QM. " then your json will have a field like : piping : {{"QM":"show selected" }}
                Important:  piping is used when the text clearly states to fill options from previous question and the question label is not in {keymap_name} if you see {keymap_name} in the text then in clearly means that it is keymap and not piping.
                

                Examples:

                Input:
                ``` Ask Qm if QN==01 \n
                QM. Demo Question (Disqualify if <1) Randomize \n (Create 5 screens with 3 benefits listed per screen)
                1. option a 
                2. option b 
                3. option c 
                Must select one option 
                ```
             
                IMPORTANT: If you've captured the sets, features, upperText, and lowerText then just turn the value to True in the dict. 
                for the option you dont have to use backticks.it will be dictionary.
                Output:
                {{
                    "ask_logic"="Ask Qm if QN==01",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"Disqualify if <1": None}}` `{{"Randomize": None}}` \n `{{"(Create 5 screens with 3 benefits listed per screen)":True}}`",
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
                
                 
                Important: the spellings can we wrong, but you have to see the bigger picture of what the user is trying to say or what kind of logic is the user trying to write.
                Important: there can be multiple ways of writing a logic, you have to understand if it means terminate, skip to.. , randomize or if the user wants to show the question as dropdown. 
                Important: the text of the options will have the complete text and the value of the options will always be None. in the options you dont need to capture any logic separately. just capture the entire text as it is without deleting anything. we should not delete anything.
                Important : the value in the options will always be None
                Important: a question will be until the options start. so if there's anything till the options start should be captured in the question.
             
             
                
                CORE PRINCIPLES and MOST IMPORTANT:
                
                
                Never delete any text: Every part of the input must be accounted for. Missing even one word is a critical error.
                The most important thing is that we should not lose any text!!
                Important: please give me a valid json.
                you just have to wrap the logic in `{{}}` , if you are confused about any text if it is a logic or not, then you can just keep it in the text without wwapping it in `{{}}`
                important: if there's any logic you dont understand, just keep it as a part of the question text.
                Finally, ensure that every piece of text from the input has been captured in the JSON without any loss. If any part of the text does not fit into the defined schema, it should be included in the extra_text field. The goal is to retain all input text in its entirety.
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