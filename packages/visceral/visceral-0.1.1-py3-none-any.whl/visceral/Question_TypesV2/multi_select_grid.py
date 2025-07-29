import json
from utils import retry_on_json_error

@retry_on_json_error
def multi_select_grid_question(openai_model, prompt,sync_layer, general_tagged):
        schema = """
        {
        "ask_logic": "", 
        "questionLabel": "string", # Capture the label exactly as it appears.
        "question": "string", # Capture the main question text that we will be showing to the user taking the survey.
        "columns": { 
            "column_text": "None"
        },
        "rows": { 
            "row_text": "None"
        },
        "type": "multi-select-grid",
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
                You are a **detailed survey question parser** responsible for structuring survey questions into **JSON format**.

     
                The schema is : {schema}
                Sync_json guides you on capturing question_text (which maps to question in our JSON), logics, and options. Use the provided output as a reference to ensure proper mapping. Your output must align with it, especially for question, options, and logics. sync_json is : {sync_layer}.
                
                Parsing Rules:
                1. Question Label**  
                - Extract the exact identifier at the start (e.g., `"Q1."`, `"5Kn."`, etc.).
                - Keep it **exactly as written** in the original text.

                2. Question Text
                - The question_text in sync_json should be used in the question field of the json. 

                3. Columns & Rows 
                - Identify **columns and rows** from the text and structure them properly.  
                - Each **option should be captured exactly** as written, preserving any logic associated with it.  
                - Example format: 


                ```json
                "columns": {{
                    "Option A": None,
                    "Option B": "(Skip to Q4)",
                    "Option C": "Terminate"
                }},
                "rows": {{
                    "Row 1": None,
                    "Row 2": None,
                    "Row 3": None
                }}
                 

                Important: If options have numbers in front of them, use the order the numbers indicate:

                For 04. a 03. b 02. c 01. d, capture the order as (d, c, b, a) (descending).
                For 01. a 02. b 03. c 04. d, capture the order as (a, b, c, d) (ascending).

                If numeric prefixes indicate order, maintain the correct sequence.
                
                
                Capture any ask if logic in the ask_logic variable. By 'ask if' logic, I mean any statement that determines when a question should be asked.
                

                5. Piping Logic

                If a question explicitly references options from a previous question, add a "piping" field. any question, which asks to fill it's options from previous question it means it is a a piping question. then please add a field piping with a dictionary where the  key is the questionLabel from which we have to fetch responses. and value could be any from these 4: [show selected, show not selected, hide selected, hide not selected].
                for example . you see something like this in a text: "Show all selected in QM. " then your json will have a field like : piping : {{"QM":"show selected" }}
                

                Examples:

                Input:
                ```
                QM. Demo Question? (Disqualify if <1) Randomize  
                Columns: a. op1, b. op2, c. op3  
                Rows: r1, r2, r3  
                Must select one option.


                Output:
                {{
                    "ask_logic": "",
                    "questionLabel": "QM",
                    "question": "Demo Question?",
                    "columns": {{
                        "op1": None,
                        "op2": None,
                        "op3": None
                    }},
                    "rows": {{
                        "r1": None,
                        "r2": None,
                        "r3": None
                    }},
                    "type": "multi-select-grid",
                    "keymap": ""
                }}
                important: Do not include option numbers in the/labels in the column and row labels. Intelligently determine which options should be assigned to rows and which should be assigned to columns.
                Important: A grid question will always have the rows and columns. 
                Ensure every item in the JSON includes a "type" field.
                Do not remove any special markdown characters used in Markdown formatting, and ensure it is correctly formatted.
                If any option requires inserting a list of states or countries, include the full list of states/countries for the respective country.
                Also, here are some special mentions by the user: pay special attention and include them as well: {general_tagged}.
                Now, parse the following survey question according to these rules: {prompt}
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result


@retry_on_json_error
def multi_select_grid_logic(openai_model, input_json,user_logic, input_text, logic_tagged):
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a precise survey question parser that deals with the logic evaluation."},
            {"role": "user", "content": f"""
            


            You will receive a JSON containing a grid question constructed from raw text, along with the original raw text itself.  
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

            Do Not Introduce Logics on Your Own
            Only add logic if it is explicitly mentioned in the text.
            Handling Special Keywords:
            If the text contains "randomize", add a new field: {{"randomize": true}}
            

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
            Make sure to properly tag all special instructions without missing any. These instructions are crucial and must always be categorized correctly. Here are the instructions: {logic_tagged}
            The json is :{input_json}      
            Raw input text is : {input_text}


                    
            please give me the correct json. 
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result

