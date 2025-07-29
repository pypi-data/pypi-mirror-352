
import json
from utils import retry_on_json_error

@retry_on_json_error
def van_westerndorp_question(openai_model, prompt,sync_layer, general_tagged):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the main question text that we will be showing to the user taking the survey.
            "question": "string",  # Capture the label exactly as it appears. 
            "van_westerndorp":[],
            "type":"van_westerndorp",
            "currency":"" #capture the currency from the text if given, defualt is "USD"
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

                The schema to be used is: {schema}

                Parsing Rules:
                Sync_json guides you on capturing question_text (which maps to question in our JSON), logics, and options. Use the provided output as a reference to ensure proper mapping. Your output must align with it, especially for question, options, and logics. sync_json is : {sync_layer}.
                
                1. Question Label:  
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.).  
                - Keep it exactly as written.  

                2. Question Text:  
                - The question_text in sync_json should be used in the question field of the json. 

                3. Ask If Logic:  
                - Capture any "ask if" condition that determines when a question should be asked.  
                - Store this in the `ask_logic` field.  


                4. currency: Capture the currency as a 3-letter code (e.g., USD). The default will be USD. If a different currency is provided, capture it accordingly
                 

                please give me a field called van_westerndorp which is a list of the items  required by van westerndorp question. such as : ['At what price do you think the product is priced so low that it makes you question its quality?', 'At what price do you think the product is a bargain?', 'At what price do you think the product begins to seem expensive?', 'At what price do you think the product is too expensive?']
                Let's suppose the user has mentioned these options, then we will use them. If not then we will use the one provided above. Because we need these for a van_westerndorp question.


                Examples:

                Input:
                ``` (Ask if Qn=03) \n
                QM. Demo Question for contact form ? (Disqualify if name=="XYZ") \n random text \n Email id
                ```

                Output:
                {{
                
                    "ask_logic"="Ask if Qn=03",
                    "questionLabel": "QM",
                    "question": "Demo van westerndorp Question?",
                    "van_westerndorp":['At what price do you think the product is priced so low that it makes you question its quality?', 'At what price do you think the product is a bargain?', 'At what price do you think the product begins to seem expensive?', 'At what price do you think the product is too expensive?']
                    "type":"van_westerndorp"
                 
                }}
                 
                Examples:

                Input:
                ```
                QM. Demo Question? Skip if name=='XYZ' \n random text
                ```

                Output:
                {{ååå
                    "questionLabel": "QM",
                    "question": "Demo Question?",
                    "type":"van_westerndorp",
                    "van_westerndorp":['At what price do you think the product is priced so low that it makes you question its quality?', 'At what price do you think the product is a bargain?', 'At what price do you think the product begins to seem expensive?', 'At what price do you think the product is too expensive?']
                    
                  

                }}
                
                
                
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

