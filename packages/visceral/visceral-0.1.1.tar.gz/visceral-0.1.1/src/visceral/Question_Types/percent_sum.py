import json

def percent_sum_question(openai_model, prompt):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears, even is there's any text till we start the options, should be captured as it is. we dont want to lose any text at all, not even a single dot or bracket.
            "question": "string",  # Full question text with any logic in `{ logic: None }` format . YOU ARE NOT SUPPOSED TO DELETE ANYTHING COPY IT AS IT IS. 
            "options": [  # List of options (if any) with their associated logic if any
                {"full_option_text": "None"}
            ],
            "extra_text": "string", # Any text that does not fit into the specified categories should be captured here. The purpose of "extra_text" is to ensure no data is lost, allowing us to retain every detail from the input text, including any text or symbols that fall outside the defined structure. (if there's any logic, then make sure to wrap it in `{logic: None}`)
            type="percentage_sum",
        }
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information. The most important thing is that we should not delete even a single dot. You are dealing with percent_sum question type"},
                {"role": "user", "content": f"""
                You are a detailed survey question parser. Your task is to analyze survey questions and capture EVERY piece of text while structuring them into a specific JSON format. Follow these guidelines:

                CORE PRINCIPLES:
                1. Never delete or modify any text. WE SHOULD NOT LOSE EVEN A SINGLE DOT. we cannot delete any text at any cost.

                The schema to be used is : {schema}

                PARSING RULES:

                1. Question Label:
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.)
                - Keep it exactly as written

                2. Question Text:
                - Include everything from the start of the question to just before the options start (if they exist). anything and everything, even if it doent make sense will be a part of the question text.
                - Even random or unrelated text must be part of the question.
                - For any logic/instructions in parentheses or brackets, wrap them in `{{"text": None}}` format
                - Example: "How old are you? (Disqualify if <18)" becomes:
                "How old are you? `{{"Disqualify if <18": None}}`"

                3. Options:
                - Be smart enough the understand the options from the text.
                - Create a list of dictionaries where each option is a key and value as None
                - example {{"Option text": None}}
                - example {{"Option text (Skip to Q4)": None}}
                - example: {{"Option text Terminate": None}}
                Important: If options have numbers in front of them, use the order the numbers indicate:
                For 04. a 03. b 02. c 01. d, capture the order as (d, c, b, a) (descending).
                For 01. a 02. b 03. c 04. d, capture the order as (a, b, c, d) (ascending).


                4. Text After Options:
                - Capture any text that appears after the options list
                - Wrap any logic in `{{"text": None}}` format
                - Important: Text after options will exist even if there are no options, it there to capture the ending text. so that we dont lose any text.

                Capture any ask if logic in the ask_logic variable. By 'ask if' logic, I mean any statement that determines when a question should be asked
                
                
    
                
                SPECIAL INSTRUCTIONS:
                
                - All logic must be wrapped in `{{}}` and quoted properly
                - Keep all original spacing and formatting
                - Never remove any text, even if it seems redundant, we should be capturing each and every detail. we should not delete even a single dot.

                Important: if you come across any question, which asks to fill it's options from previous question it means it is a a piping question. then please add a field piping with a dictionary where the  key is the questionLabel from which we have to fetch responses. and value could be any from these 4: [show selected, show not selected, hide selected, hide not selected].
                for example . you see something like this in a text: "Show all selected in QM. " then your json will have a field like : piping : {{"QM":"show selected" }}


                Examples:

                Input:
                ```Ask if Qn==1 \n
                QM. Demo Question (Disqualify if <1) Randomize \n random text
                1. option a 
                2. option b 
                3. option c 
                
                ```

                Output:
                {{
                    "ask_logic":"Ask if Qn==1",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"Disqualify if <1": None}}` `{{"Randomize": None}}` \n random text",
                    "options": [
                        {{"option a ": None}},
                        {{"option b ": None}},
                        {{"option c ": None}}
                    ],
                    "extra_text": "",
                    "type":"percentage_sum",
                }}
                
                important: make sure to capture logics in the `{{}}`
                Important: the text of the options will have the complete text and the value of the options will always be None. in the options you dont need to capture any logic separately. just capture the entire text as it is without deleting anything. we should not delete anything.
                Important : the value in the options will always be None
                Important: a question will be until the options start. so if there's anything till the options start should be captured in the question.
                Important: Dont change the formatting. (It should be the same as it was in the input data. not even a dot should be lost.) 
                
                CORE PRINCIPLES and MOST IMPORTANT:

                Never delete any text: Every part of the input must be accounted for. Missing even one word is a critical error.
                important: make sure to capture logics in the `{{}}`
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



def percent_sum_logic(openai_model, input_json,user_logic):
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
            {"role": "user", "content": f"""
            


            
            You will be receving a json which has multi_text question , your task is to understand any logics if they exist and put it in the bucket of logics we currently support. 
            We currently support :
            1. Termination logics (it can be written in any way) , you should be smart enough to understand if that word/sentence means termination
            2. Skip logics (it can be written in any way) , you should be smart enough to understand if that word/sentence means skip.
            3. User defined logics : The user might have different way of writing any logics and we've captured that.
             
            You are not supposed to make any changes in the options.
                
            Important : The users way of writing the logic is : {user_logic} make sure to only use the words as logics which are explicitly mentioned
            please pay special attention while assigning logics. 

            You will primarily see logics captured in `{{}}`. you goal is to understand if that logic falls in the above 3 categories of logics we support for the percentage_sum. 
            If there's no logic that we support. (rememebr there can be mutliple ways of writing any logic, we have to be smart enough to understand the bigger picture). But if we dont support that logic or there is no logic, just return the json as it is. without making any changes.

            But if you see that there's any logic that we support 1. Termination, 2. Skip 3. User defined logics.  then we should follow the below steps.


            In the question if you observe any logic that we support. Then please add another field saying percenatge_sum_logic and the key value pair will be the following. 
            For terminating the key should be "Terminating" and the value should be conditon but the condition will only be " [logical operator] [value]" 
            For skip conditions the key would be "SKIP TO [questionLabel of the question]" value would be " [logical operator] [value] " 
            important: The logical operator that you use should be like QuestionLabel ==, >=, <=, != , or whatever the option logic says. every opertor should have questionLabel in front of it. give me the exact logic that you get. you dont have to change any logic. make it both for Terminating or SKIP questions. follow the convention of writing "==, >=, <=, != " even if the user has just one "=" we should eb using "=="
            Important: Provide the exact logic, but include the questionLabel (retrieved from the JSON) before every operator. Ensure the operators are in uppercase, like OR and AND. By questionLabel, I mean the actual value of the questionLabel field from the JSON, not the literal term questionLabel.
            We also turn the None to True if its the logic we support and we've added a field for it in our json, like we did in the below example. 
            

            example: you got this:

             {{
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"(Disqualify if QM=="XYZ")": None}}` \n random text",
                    "options": [
                        {{"option a ": None}},
                        {{"option b ": None}},
                        {{"option c ": None}}
                    ],
                    "extra_text":"",
                    "type":"percentage_sum",
                    
                 
            }}

            your output will look something like this:

            {{
                "ask_logic":"Ask if Q3==0",
                "questionLabel": "QM",
                "question": "Demo Question? `{{"(Disqualify if QM=="XYZ")": True}}` \n random text",
                "options": [
                            {{"option a ": None}},
                            {{"option b ": None}},
                            {{"option c ": None}}
                        ],
                "extra_text":"",
                "type":"percentage_sum",
                "percentage_sum_logic": {{"Terminating":"QM=="XYZ"}}
            
            
            }}
            

            example of a logic we dont understand.
            {{
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"Some logic I dont know": None}}` \n random text",
                    "options": [
                        {{"option a ": None}},
                        {{"option b ": None}},
                        {{"option c ": None}}
                    ],
                    "extra_text":"",
                    "type":"percentage_sum",
                    
                 
            }}
            we will return it as it :
            {{
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"Some logic I dont know": None}}` \n random text",
                    
                    "options": [
                        {{"option a ": None}},
                        {{"option b ": None}},
                        {{"option c ": None}}
                    ],
                    "extra_text":"",
                    "type":"percentage_sum",
                    
                 
            }}

            Please pay special attention to the instructions for logics and make sure you mark it correctly, double check it. 
            Most Important: No data should be deletd, not even a single dot or a bracket.
            The json is :{input_json}      


                    
            please give me the correct json. 
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result

