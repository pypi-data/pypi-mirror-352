import json

def ask_if_logic(openai_model,json_data):

        
        # print("we are int he logical set now ")
        # parsed_text = self.client_open_ai.chat.completions.create(
        parsed_text = openai_model.client_open_ai.chat.completions.create(
           
            model="gpt-4o",
            response_format={ "type": "json_object" },
            temperature=0.00000001,
            messages=[
                {"role": "system", "content": "You are an agent spcialising in understanding the survey logics"},
                {"role": "user", "content": f"""

                Analyze this JSON and transform the ask_logic field . 
                Important: you are not supposed to change anything other than "ask_logic"

                The input json is :  {json_data}

                Instructions:
    
                We basically want to convert the ask_logic statement into something which our backend code can understand.
                you have to understand the statement in the ask_logic and convert it into a string.
                
                Transform the ask_logic as follows:
                1. Simple OR conditions: "ask_logic": "Qx ==`1` OR Qx ==`2`"
                2. AND conditions: "ask_logic": ""Qx ==`1` OR Qx ==`2`" 
                3. Combined AND/OR: "ask_logic": "Qx ==`1` OR Qx == `2` AND ( "Qy" == `1`)" 

                Important: The key will always be 1 and the value would be the logic.
                Here Qx or Qy are the question Labels

                Important: If you come across anything that doesnt look like option but is a variable or a text then rather than using backticks , please use : ' ' 
                for example "ask Q3 if Q2 == polsjr" then "ask_logic" : "Q2=='polsjr'". Understand in general what the user is trying to say.
                
               

                Examples:
                1. "ask Q3 if Q2 is 1 or 2" → "ask_logic": "Q2 == `1` OR  Q2==`2`"
                2. "ask Q4 if Q2 is 1 and Q3 is 2" → "ask_logic": "Q2 == `1` AND Q3==`2`"
                3. "ask Q5 if Q2 is 1 or 2, and Q3 is 3" → "ask_logic": "Q2==`1` OR Q2==`2` AND (Q3 ==`3`) "

                important: for the values please donot use double digits. use single digits like 1,2,3,4..10,11,12...
                
                
                
                important: donot include ask if in the value, like "ask_logic":"ask if Q2==`01`" this si wrong. it should just contain the condition like: "ask_logic":"Q2==`01`"

                if we have option number and text together then just use the option number : for example ['Ask if Q3= 01 Adidas'] then ask_logic: "Q3==`1`"
               
            
                
                make sure to convert the statement into logical way.
                Important: you are not supposed to change anything other than "ask_logic".
                Return the valid JSON.

                
                
                """ }
            ],
        )



        
        content = parsed_text.choices[0].message.content
        result=json.loads(content)
        # print (result)

        return result