import json

def generate_sync(openai_model, prompt, question_type, user_logic):
    schema = """
    {
        "question_text": "",
        "options": [],  
        "logics": [] 
    }
    """

    #  Define supported logics correctly as lists
    QUESTION_TYPE_LOGICS = {
        "single-select": ["Ask If", "Terminate", "Skip", "Randomize", "Dropdown", "Range"],
        "multi-select": ["Ask If", "Terminate", "Skip", "Randomize", "Dropdown", "Range"],
        "single-text": ["Ask If", "Terminate", "Skip"],
        "multi-text": ["Ask If"],
        "grid": ["Ask If"],
        "nps": ["Ask If", "Terminate", "Skip"],
        "ranking": ["Ask If", "Randomize", "Dropdown"],
        "zipcode": ["Ask If", "Terminate", "Skip", "Range"],
        "percentage": ["Ask If", "Terminate", "Skip", "Range"],
        "currency": ["Ask If", "Terminate", "Skip", "Range"],
        "year": ["Ask If", "Terminate", "Skip", "Range"],
        "percent-sum": ["Ask If"],
        "multi-percentage": ["Ask If"],
        "max-diff": ["Ask If"],
        "van-westendorp": ["Ask If"],
        "contact-form": [],
        "notes": ["Ask If"],
        "number": ["Ask If", "Terminate", "Skip", "Range"],
        "terminate": ["Ask If"],
        "variable": ["Ask If", "T"],
        "ai-chat": ["Ask If"]
    }

    #  Get relevant logics or return an empty list if not found
    supported_logics = QUESTION_TYPE_LOGICS.get(question_type, [])

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.1,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are acting as a sync layer that standardizes survey questions before passing them to the next two layers."},
            {"role": "user", "content": f"""

                Role & Purpose:  
                You ensure consistent extraction of key details from survey questions for the next two processing layers that run in parallel. Your task is to synchronize their outputs by structuring data accurately.
                You are basically a layer that decides which text will be shown to the users taking the survey.

                Key Extraction Rules:  
                1. Main Question (`question_text`) – Extract the survey question to be displayed to users. Do not capture any programmer notes unless explicitly tagged with <> </>. Only include content that will be shown to survey participants. Do not delete anything; capture everything as it is, including formatting like <lbr />. Even if there are <lbr />, do not assume the question is finished—use your judgment to identify the complete question text. <lbr /> is just for formatting.
                2. Options (`options`) – If the question has multiple choices, capture them.  (give me the list)
                3. Logics (`logics`) – Normalize logic terms based on the predefined list for this question type.  Again logics can be written in multiple ways so you have to make sure you accurately capture them.
                4. Explicit Tags (<> </>) – Any content inside < > must be preserved and categorized correctly. This layer exists to ensure that if we couldn't capture something accurately, the user has tagged it to guide us in picking up the text correctly.
                5. Custom Logic Alignment – If user-defined logic exists in our database, ensure alignment: `{user_logic if user_logic else "No custom logic provided"}`.  

                Supported Logics for {question_type if question_type else "Unknown Question Type"}:  
                {", ".join(supported_logics) if supported_logics else "No specific logics applicable."}

                example input: 
                ```
                Q3. Main Question? some random text not assocaited with main question <lbr />
                1. Op1 2. Op2
                3. Op3 (some termination logic)
                again some random text
                ```

                expected output:
                {{'question_text': 'Main Question?', 'options': ['Op1', 'Op2', 'Op3'], 'logics': ["some termination logic"]}}

                Processing Schema:  
                Donot lose any formatting including any <lbr />
                You must follow this schema to ensure consistency:  {schema}  
                Our goal is to correctly idenitfy: question_text, logics, and options. Give me a valid json
                Survey Question Input:  {prompt}  
            """}
        ]
    )

    
    
    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    print("the sync output is : ", result)
    return result
