import json
from utils import retry_on_json_error

@retry_on_json_error
def categorizer_for_questions(openai_model, prompt):
        

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "you are a specialised agent which can categorize a given question into a type."},
                {"role": "user", "content": f"""
                
              The categories that we support are:
              single_select
              multi_select
              single_text
              multi_text
              grid
              number
              currency
              year
              percentage
              percent_sum
              message
              notes
              nps
              hidden_variable
              maxdiff
              contact_form
              ranking
              multi_percentage
              van_westerndorp
              zip_code
              ai_chat
            
                
              
              Guidelines:
              
              Determine the question type based on the provided options.
              Net Promoter Score (NPS): If the question is a "Net Promoter Score" question, mark its type as nps.
              numbers: Questions like "How old are you?" should be classified as number.
              
              Message vs Notes:
              message: Text intended to be shown to the user, such as introductions or filler questions.
              Notes: Programmer notes intended for creating the survey.
                 

             
              If the question type is not in the supported categories, tag it as unknown.
              
                 
              Output Format:
              Provide the response as a JSON object with a single key-value pair:

              Key: "type"
              Value: The identified type.
              Example Output:

                {{
                  "type": "single_select"
                }}
                
                The question text is : {prompt}

                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result


