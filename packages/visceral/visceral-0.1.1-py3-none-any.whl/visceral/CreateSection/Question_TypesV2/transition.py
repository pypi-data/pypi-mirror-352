import json
from utils import retry_on_json_error

@retry_on_json_error
def transition_question(openai_model, prompt):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears.
            "question": "string",   # Capture the main question text that we will be showing to the user taking the survey.
            type="message"
        }
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information. The most important thing is that we should not delete even a single dot. You are dealing with transition question type"},
                {"role": "user", "content": f"""
                 
                
                You are a detailed survey question parser. 

                The schema to be used is: {schema}
          
                
                Parsing Rules:
                
                1. Question Label:  
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.).  
                - Keep it exactly as written.  

                2. Question Text:  
                - The question_text in sync_json should be used in the question field of the json.   

                3. Ask If Logic:  
                - Capture any "ask if" condition that determines when a question should be asked.  
                - Store this in the `ask_logic` field.  
               
                 Examples:

                Input:
                ```
                Ask if Q3==0 \n
                QM. Demo Question? Disqualify if QM=="XYZ" \n random text
                ```

                Output:
                {{
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question?",
                    "type":"message",
                   
                 
                }}

              
                Important: please give me a valid json.
      
                Parse the following survey question according to these rules: 
                 
                {prompt}
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result



# def single_text_logic(self, input_json,user_logic):
    

#     parsed_text = self.client_open_ai.chat.completions.create(
#         model="gpt-4o",
#         temperature=0.0000000001,
#         response_format={ "type": "json_object" },
#         messages=[
#             {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
#             {"role": "user", "content": f"""
            



#             You will be receving a json which has single_text question , your task is to understand any logics if they exist and put it in the bucket of logics we currently support.
#             we currently just support termination and skip logics on single_text questions.
                
            
#             be sure to smartly understand what the user is trying to mean with that option. There can be multiple ways to say all these logics.
#             Important : Apart from that: Ill be sharing with you the users way of writing a logic for the survey. So you should be smart enough to understand what the user is trying to say and then make our json.
#             Important : The users way of writing the logic is : {user_logic} make sure to only use the words as logics which are explicitly mentioned
#             please pay special attention while assigning logics. 

#             For complete and disqualify -> we will use "THANK AND END" in our final json that we produce and for skip we use "SKIP TO [qstnLabel]" . 

#             In the question if you observe any logic associated with it. please add another field saying text_logic and for the key,value pair. For terminating the key should be Terminating and the value should be conditon but the condition will only be " [logical operator] [value]" and for skip conditions the key would be [ SKIP TO [qstnLabel] value would be " [logical operator] [value] " . 
#             The logical operator that you use should be like QuestionLabel ==, >=, <=, != , or whatever the option logic says. every opertor should have questionLabel in front of it. give me the exact logic that you get. you dont have to change any logic. make it both for Terminating or SKIP questions. Important: give me the exact logic but with questionLabel (pick it up from json) in front of every operator. keep the operators in capital like "OR"."AND". also by questionLabel : I mean the questionLabel of the question. and not "questionLabel".
                
#             Be sure to understand how a user writes the logic. 
#             Use you general understanding and the user_logic way of writing the logic. 
#             Also, if the logic is not in english. please understand it properly
        
#             Very Important: You are not supposed to add any new options on your own, just deal with whatever you have.
             
#             Most Important: No data should be deletd, not even a single dot.
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

