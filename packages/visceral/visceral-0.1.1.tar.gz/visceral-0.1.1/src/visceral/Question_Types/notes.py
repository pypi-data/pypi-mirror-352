import json

def notes_question(openai_model, prompt):
        schema = """
        {
            "questionLabel": "string",  # Capture the label exactly as it appears, even is there's any text till we start the options, should be captured as it is. we dont want to lose any text at all, not even a single dot or bracket.
            "question": "string",  # Capture the entire input question text as it is . YOU ARE NOT SUPPOSED TO DELETE ANYTHING COPY IT AS IT IS. 
            type="notes"
        }
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information. The most important thing is that we should not delete even a single dot. You are dealing with notes question type"},
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
                
                 
                 The schema is : {schema}


                
                SPECIAL INSTRUCTIONS:
                
   
                - Keep all original spacing and formatting
                - Never remove any text, even if it seems redundant, we should be capturing each and every detail. we should not delete even a single dot.
                - Capture ALL parenthetical or bracketed instructions in dictionary format.

                the text should be captured as it is, we should not change even a single dot.
                
                CORE PRINCIPLES and MOST IMPORTANT:

                Never delete or modify any text: Every part of the input must be accounted for. Missing even one word is a critical error.
                Preserve structure and format: The output must follow the specified JSON schema exactly.
                
                The most important thing is that we should not lose any text!!
                Most important: Dont get stuck, if by any chance you're confused give me whatever you understand. just dont delete anything and dont be stuck
                Parse the following survey question according to these rules: {prompt}
                 
                
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result
