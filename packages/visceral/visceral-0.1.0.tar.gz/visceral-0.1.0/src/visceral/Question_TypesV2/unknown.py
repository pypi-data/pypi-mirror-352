import json
from utils import retry_on_json_error


@retry_on_json_error
def unknown_question(openai_model, prompt, general_tagged):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears, even is there's any text till we start the options, should be captured as it is. we dont want to lose any text at all, not even a single dot or bracket.
            "question": "string",  # Capture the full question text as it is.
            "type"="unknown"
        }
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information. The most important thing is that we should not delete even a single dot. You are dealing with unknown question type"},
                {"role": "user", "content": f"""
                You are a detailed survey question parser. Your task is to analyze survey questions and capture EVERY piece of text while structuring them into a specific JSON format. Follow these guidelines:

                CORE PRINCIPLES:
                1. Never delete any text. WE SHOULD NOT LOSE EVEN A SINGLE DOT. we cannot delete any text at any cost.
                 
                The schema to be used is : {schema}


                PARSING RULES:

                1. Question Label:
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.)
                - Keep it exactly as written

                2. Question Text:
                - Include everything from the start of the question to the end.
                
        
                
                SPECIAL INSTRUCTIONS:
                
                - Keep all original spacing and formatting
                - Never remove any text, even if it seems redundant, we should be capturing each and every detail. we should not delete even a single dot.
                


                Examples:

                Input:
                ```
                Ask if Q3==0 \n QM. Demo unknown Question? Disqualify if QM=="XYZ" \n random text
                ```

                Output:
                {{
                    "questionLabel": "QM",
                    "question": " Ask if Q3==0 \n QM. Demo unknown Question? Disqualify if QM=="XYZ" \n random text",
                    "type":"unknown",
                 
                }}
                
          
                CORE PRINCIPLES and MOST IMPORTANT:

                Never delete any text: Every part of the input must be accounted for. Missing even one word is a critical error.
                The most important thing is that we should not lose any text!!
                Important: please give me a valid json.
                Also, here are some special mentions by the user: pay special attention and include them as well: {general_tagged}.
                Parse the following survey question according to these rules: 
                 
                {prompt}
                """
                }
            ]
        )
       
        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result


