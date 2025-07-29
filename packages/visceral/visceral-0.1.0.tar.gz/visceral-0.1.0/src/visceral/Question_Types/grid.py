import json

def grid_question(openai_model, prompt,keymap_name):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears, even is there's any text till we start the options, should be captured as it is. we dont want to lose any text at all, not even a single dot or bracket.
            "question": "string",  # Full question text with any logic in `{ logic: None }` format . YOU ARE NOT SUPPOSED TO DELETE ANYTHING COPY IT AS IT IS. 
            "columns": [{"column_text": "None"}],
            "rows": [{"row_text": "None"}]
            "extra_text": "string", # Any text that does not fit into the specified categories should be captured here. The purpose of "extra_text" is to ensure no data is lost, allowing us to retain every detail from the input text, including any text or symbols that fall outside the defined structure. (if there's any logic in then make sure to wrap it in `{logic: None}`)
            "type":"grid",
            "keymap": "string" 

        }
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information. The most important thing is that we should not delete even a single dot. You are dealing with multi_select question type"},
                {"role": "user", "content": f"""
                You are a detailed survey question parser. Your task is to analyze survey questions and capture EVERY piece of text while structuring them into a specific JSON format. Follow these guidelines:

                CORE PRINCIPLES:
                1. Never delete or modify any text. WE SHOULD NOT LOSE EVEN A SINGLE DOT. we cannot delete any text at any cost.
                2. Preserve the exact structure and formatting
                3. DONOT EVEN DELETE A SINGLE BRACKET.

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

                3. columns/rows:
                - Be smart enough the understand the rows/columns from the text.
                - Create a list of dictionaries where each option is a key and value as None
                - example {{"Option text": None}}
                - example {{"Option text (Skip to Q4)": None}}
                - example: {{"Option text Terminate": None}}
                Important: If options have numbers in front of them, use the order the numbers indicate:

                For 04. a 03. b 02. c 01. d, capture the order as (d, c, b, a) (descending).
                For 01. a 02. b 03. c 04. d, capture the order as (a, b, c, d) (ascending).

                Make sure to follow the order as mentioned in the input text if it has the numbering in front of it.

                4. extra_text:
                - Capture any text that appears after the options list
                - Wrap any logic in `{{"text": None}}` format
                - Important: Text after options will exist even if there are no options, it there to capture the ending text. so that we dont lose any text.
    
                 
                5. 5.Keymap: Identify and capture any exact matches of keymap variable names when they appear in the user's input text. These variables serve as predefined references within our platform.
                Important: you dont have to mention the keymap in the question text then.
                
                A keymap will always be from {keymap_name if keymap_name is not None else ": User doesnt have any keymaps defined"}
                If the user explicitly mentions the variable, it should be recognized and captured accurately.
                This behavior is distinct from "piping" and specifically focuses on detecting variable names.
                Some of the user defined key map names are : {keymap_name} and you dont have to add that variable separately in the options if given additional options.
                
                The schema is : {schema}
                
                
                Capture any ask if logic in the ask_logic variable. By 'ask if' logic, I mean any statement that determines when a question should be asked.
                
                SPECIAL INSTRUCTIONS:
                
                - All logic must be wrapped in `{{}}` and quoted properly
                - Keep all original spacing and formatting
                - Never remove any text, even if it seems redundant, we should be capturing each and every detail. we should not delete even a single dot.
                - Capture ALL parenthetical or bracketed instructions in dictionary format

                Important: if you come across any question, which asks to fill it's options from previous question it means it is a a piping question. then please add a field piping with a dictionary where the  key is the questionLabel from which we have to fetch responses. and value could be any from these 4: [show selected, show not selected, hide selected, hide not selected].
                for example . you see something like this in a text: "Show all selected in QM. " then your json will have a field like : piping : {{"QM":"show selected" }}
                Important:  piping is used when the text clearly states to fill options from previous question and the question label is not in {keymap_name} if you see {keymap_name} in the text then in clearly means that it is keymap and not piping.
                

                Examples:

                Input:
                ```
                QM. Demo Question  (Disqualify if <1) Randomize \n random text
                Columns : a,b,c
                Rows : x,y,z
                Must select one option
                ```

                Output:
                {{
                    "ask_logic":"",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"Disqualify if <1": None}}` `{{"Randomize": None}}` \n random text",
                    "columns": [
                        {{"a ": None}},
                        {{"b ": None}},
                        {{"c ": None}}
                    ],
                    "rows": [
                        {{"x ": None}},
                        {{"y ": None}},
                        {{"z ": None}}
                    ],
                    "extra_text":"Must select one option",
                    "type":"grid"
        
                }}


                important: donot add unncessary text and redundant stuff in extra_text. only add stuff if you feel its something important that we are missing. like donot add Horizontal options/ vertical options in the extra_text
                important: make sure to capture logics in the `{{}}`
                Important: the text of the options will have the complete text and the value of the options will always be None. in the options you dont need to capture any logic separately. just capture the entire text as it is without deleting anything. we should not delete anything.
                Important : the value in the options will always be None
                Important: a question will be until the options start. so if there's anything till the options start should be captured in the question.
                Important : The logics that we support are :  dropdown, randomize, terminate, skips. (It is possible that they can be written in some other way, for example : end also means termination) Be smart to identify.
                Important: Dont change the formatting. (It should be the same as it was in the input data. not even a dot should be lost.) 
                
                CORE PRINCIPLES and MOST IMPORTANT:

                Never delete or modify any text: Every part of the input must be accounted for. Missing even one word is a critical error.
                Preserve structure and format: The output must follow the specified JSON schema exactly.
                
                The most important thing is that we should not lose any text!!
                Most important: Dont get stuck, if by any chance you're confused give me whatever you understand. just dont delete anything and dont be stuck
                Finally, ensure that every piece of text from the input has been captured in the JSON without any loss. If any part of the text does not fit into the defined schema, it should be included in the extra_text field. The goal is to retain all input text in its entirety.
                
                Parse the following survey question according to these rules: 
                 
                {prompt}
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result



def grid_logic(openai_model, input_json,user_logic):
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
            {"role": "user", "content": f"""
            



            You will be receving a json which has grid question , your task is to understand any logics if they exist and put it in the bucket of logics we currently support.
            
            for the columns/rows  : please update the values with the appropriate logic
            
            We currently support :
            Any termination logic should be marked as : "THANK AND END" 
            Any Skip logic should be marked as : "SKIP TO [qstnLabel]" 
            Any logic which EXPLICITLY SAYS to finish if not selected then it should be marked as : "NOT SELECTED". for example : Skip to Term if not Q2=2  (if it is explicitly mentioned only then )
            Any option which has "none of the above" : "nota" 
            any option which has "specify" or any option which says "please specify" :  "other" 
            if an option has (prefer not to answer ) : "optout"
            if an option has "not applicable": "notapplicable"
            None (if no logic associated) with the option.
            

            
            important : you will have to update the key and value of the rows/columns dictionary 
            for exmaple: if you received this as an option text :  {{'None allenSir': None}} and we know that the user writes allennSir as Disqualify then the option text in the new json will be {{None `allenSir`: "Terminate"}} this means that in the new json we will wrap that particular logic in backticks and in the value of the dictionary we will put the logic from our bucket. Donot delete any text.
            in the key, make sure to put the logic in the backticks, even if the logic is in brackets. put the enitre logic incuding any brackets etc. in the backticks.
            
            important: if you see anything related to randomize. please create a new field called {{"randomize":True}} 
            important: if you see anything related to dropdown, please create a new field called {{"dropdown":True}}
            important: if you see anything related to ranges, please create a new field called {{"data_range":[min,max]}}
            also, please update the dictionary to True where the logic was intially mentioned.
            for example : input: {{"question" : "demo question `{{Randomize:None}}`"}}
            then you will give me : {{"question":"demo question `{{Randomize:True}}`", "randomize":True }}, so basically we created a new field and also updated the logic in the question to True.
                
            
            be sure to smartly understand what the user is trying to mean with that option. There can be multiple ways to say all these logics.
            Important : Apart from that: Ill be sharing with you the users way of writing a logic for the survey. So you should be smart enough to understand what the user is trying to say and then make our json.
            Important : The users way of writing the logic is : {user_logic} make sure to only use the words as logics which are explicitly mentioned
            please pay special attention while assigning logics. 

            example input option: {{"pizza (loppy)":None}} and the user marks loppy as disqualify then your output will be : {{"pizza `(loppy)`:"THANK AND END"}}. in the key, you only have to wrap the logic in backticks if you can identify it. otherwise no need for example: {{"pizza (choppy)":None}} and we dont identify any logic here so we will not wrap the logic with backticks. the output will be  {{"pizza (choppy)":None}}
            
         
            Be sure to understand how a user writes the logic. 
            Use you general understanding and the user_logic way of writing the logic. 
            Also, if the logic is not in english. please understand it properly
        
            Very Important: You are not supposed to add any new options on your own, just deal with whatever you have.
            
            for example if you get an input that has only one option like 'options': {{'una ..1': None}} then you are not supposed to add any new options. 
            Most Important: No data should be deletd, not even a single dot.
            Important : you are not supposed to change the logic field in the json.

            
            important: "Did not vote" or "None" ,"exclusive" anything like that doesnt always mean disqualified. until it is explicitly mentiond..
            Please pay special attention to the instructions for logics and make sure you mark it correctly, double check it. 
            Most Important: No data should be deletd, not even a single dot.
            The json is :{input_json}      


                    
            please give me the correct json. 
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result

