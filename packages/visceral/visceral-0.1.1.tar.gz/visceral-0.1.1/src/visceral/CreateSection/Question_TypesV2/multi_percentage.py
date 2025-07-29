import json
from utils import retry_on_json_error


@retry_on_json_error
def multi_percentage_question(openai_model, prompt):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears.
            "question": "string",   # Capture the main question text that we will be showing to the user taking the survey.
            "options": [  # List of options (if any) with their associated logic if any
                {"option_text": "None"}
            ],
            type="multi_percentage"
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
                

    
                
                
                Important: Capture any ask if logic in the ask_logic variable. By 'ask if' logic, I mean any statement that determines when a question should be asked.
                
                5. Piping Logic

                If a question explicitly references options from a previous question, add a "piping" field. any question, which asks to fill it's options from previous question it means it is a a piping question. then please add a field piping with a dictionary where the  key is the questionLabel from which we have to fetch responses. and value could be any from these 4: [show selected, show not selected, hide selected, hide not selected].
                for example . you see something like this in a text: "Show all selected in QM. " then your json will have a field like : piping : {{"QM":"show selected" }}
               
                

                Examples:

                Input:
                ``` Ask Qm if QN==01 \n
                QM. Demo multi percentage Question (Disqualify if <1) Randomize \n random text
                1. option a asjkdn
                2. option b Skip to Q3
                3. option c Terminate
                Must select one option
                ```
                
                Output:
                {{
                    "ask_logic"="Ask Qm if QN==01",
                    "questionLabel": "QM",
                    "question": "Demo multi percentage Question?",
                    "options": [
                        {{"option a asjkdn": None}},
                        {{"option b ": "Skip to Q3"}},
                        {{"option c ": "Terminate"}}
                    ],
                    "type":"multi_percentage",
                }}
                
                 
                Important: The spelling may be incorrect, but you must focus on understanding the user's intent and the logic they are trying to express rather than just the exact words.
                Important: There are multiple ways to express a logic condition. You must identify whether the user intends "Terminate," "Skip to...," "Randomize," or "Show as Dropdown" based on the context.
                Important: please give me a valid json.
                Parse the following survey question according to these rules: {prompt}
                 
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result


@retry_on_json_error
def multi_percentage_logic(openai_model, input_json,user_logic,input_text):
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a precise survey question parser that deals with the logic evaluation."},
            {"role": "user", "content": f"""
            

            You will receive a JSON containing a multi_percentage question constructed from raw text, along with the original raw text itself.  
            Your task is to analyze any logic present and categorize it based on the predefined logic types we support. (Refer to both the raw text and the provided JSON.)  

            Logic Rules:
            - Any termination logic should be marked as: "THANK AND END".  
            - Any skip logic should be marked as: "SKIP TO [qstnLabel]", where qstnLabel represents the question label.  
            - If a question explicitly states to finish if an option is not selected, mark it as "NOT SELECTED".  
            - Example: "Skip to Term if not Q2=2" → "NOT SELECTED" (Only if explicitly mentioned.)  
            - Any option that includes "None of the above" should be marked as: "nota".  
            - Any option that includes "specify" or phrases like "please specify" should be marked as: "other".  
            - Any option that includes "(Prefer not to answer)" should be marked as: "optout".  
            - Any option that includes "Not applicable" should be marked as: "notapplicable".
            - Any optiom that includes "Dont' know" should be marked as "dontknow"  
            - If an option has no associated logic, mark it as None.  
             
            All these logic rules should be associated with the values of the options.
            If the raw text contains logic statements like:
            "Disqualify IF Q2 == '02'" or "Disqualify IF Q2 == '04'", then follow these rules:

            Apply the logic only to the specific option mentioned in the statement.
            Be smart in identifying which options are being referenced and update their values accordingly.
            Example:
            If Q2 has an option 02 and the text states: "Disqualify if Q2 == 02", assign "THANK AND END" to this option.
            You do not need to modify the key, just update the values of the relevant options.
            Similarly, handle "Skip to..." logic the same way—apply it only to the specified option and link it to the corresponding question label (qstnLabel).
            
             
            {{
                "ask_logic": "",
                "questionLabel": "Q1.",
                "question": "What do you like?",
                "options": [
                    {{"Apple": null}},
                    {{"Pineapple": null}},
                    {{"Mango": null}},
                    {{"Kiwi": null}}
                ],
                "type": "multi_percentage"
            }}
             

            Raw Text has : Disqualify IF Q3 == `01` Disqualify IF Q1 == `02` Disqualify IF Q1 == `04`
             
            Logic Applied:
            "Disqualify IF Q3 == '01'" → Ignored (since Q3 ≠ Q1)
            "Disqualify IF Q1 == '02'" → Matches Q1 → Pineapple → "THANK AND END"
            "Disqualify IF Q1 == '04'" → Matches Q1 → Kiwi → "THANK AND END"
             
            {{
                "ask_logic": "",
                "questionLabel": "Q1.",
                "question": "What do you like?",
                "options": [
                    {{"Apple": null}},
                    {{"Pineapple": "THANK AND END"}},
                    {{"Mango": null}},
                    {{"Kiwi": "THANK AND END"}}
                ],
                "type": "multi_percentage"
            }}

             
            
            
            Do Not Introduce Logics on Your Own
            Only add logic if it is explicitly mentioned in the text.
            Handling Special Keywords:
            If the text contains "randomize", add a new field: {{"randomize": true}}
            If the text contains "dropdown", add a new field: {{"dropdown": true}}
            If the text mentions a range, add a new field in the format: {{"data_range": [min, max]}} -> Ensure min and max values are correctly extracted.
        
                
            
            Understanding User Logic & Smart Interpretation:
            The user may write logic in different ways, so interpret their intent carefully.
            Use general understanding and the user-defined way of writing logic ({user_logic if user_logic else "User hasnt mentioned any specific logic of his own"} ) to assign values correctly.
            Use your general understanding and if provided usere's way of writing a logic
            Assigning Logics Based on User Input:
            Disqualify or Complete & Disqualify → "THANK AND END"
            Skip to a specific question → "SKIP TO [qstnLabel]"
            Do not change or introduce logic unless explicitly mentioned.
            Handling Option Formatting:
            Example Input:
            {{pizza (loppy)": None}}
            If "loppy" is marked as disqualify, Output:
            {{"pizza": "THANK AND END"}}
  
            
            Handling Non-English Logics:
            If the logic is written in another language,  interpret it correctly.

            
            Do not assume "Did not vote", "None", "exclusive", etc., mean disqualified unless clearly specified.
            Double-check all logic assignments before finalizing the output.
            please give me the correct json.
            The json is :{input_json}      
            and input raw text is: {input_text}
            
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result

