import json
from utils import retry_on_json_error

@retry_on_json_error
def recommend_sections_to_optimize(openai_model, previous_conversation, complete_questions_payload, instructions, block_names):
        
    output_schema = {         
    "recommend_sections_schema": [          
    {"section_name":"string", # Unique name for the new section. Should not duplicate any existing section name.
    "number_of_questions":"integer", # the number of questions we will have post optimizing the survey
    "details_about_section":"string"  #Detailed description of what this section should cover, including specific focuses, terminologies, or considerations post optimizing the survey.
    },
    {"section_name":"string",
    "number_of_questions":"integer", 
    "details_about_section":"string" 
    } ]
    }

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content":  "You are an expert in creating high-quality survey sections and questions. You assist users by recommending new sections to add to their surveys, ensuring that the survey accomplishes the user's research objective."},
                {"role": "user", "content": f"""
                 
You represent Visceral, an AI-native platform that modernizes market research by automating survey programming, quality testing, and analytics. Visceral integrates with major panel companies, data collection platforms, and GenAI systems, enabling surveys to run 10x faster at 50% cost, while maintaining high-quality standards. The platform offers drag-and-drop and API capabilities for rapid adoption without disrupting existing workflows.
Your task:
- You are bascically optimizing the survey based on the user's instructions. (make it longer, shorter , more specific, more general, etc)
- Recommend one or more new **survey sections** based on the user's research objective.
- Focus on **high-quality**, **unbiased** questions that **help achieve the user's objective**.

Important guidelines:
- **Section names must be unique** and should not duplicate existing sections. (Existing sections: {block_names if block_names else "No sections yet."})
- If the user specifies a number of sections or questions, **follow it exactly**.
- You haev to abide by the user's instructions strictly to optimize the survey.
- Be thoughtful about how each section relates to the objective.
- **Maximum per section: 100 questions**.



Your task is to determine the ideal number of questions for each section of the survey we are creating, based on the user's instructions and the current survey structure. 
Important: You are optimizing the current survey based on the user's instructions.
The current survey looks like: 
```
{complete_questions_payload}
```

- **Critical Thinking Required:**  
Design each section thoughtfully to genuinely accomplish the user's objective. Prioritize **quality and focus**.
Rememeber you are an expert in survey design and you have to create a survey that can accomplish the users objective.

General advice:
- Prioritize quality 
- Avoid any bias in questions.
- Think critically about how the sections together will accomplish the objective.
- You are basically helping to optimize the current survey based on the user's instructions and you are an expert at it.


- If previous conversation history provides useful context, **incorporate it thoughtfully**: 
``` 
Previous conversation: {previous_conversation}
```

The user's instructions are: 
```
{instructions}
```
Please give me a valid response in a json format.
follow this output schema strictly:
{json.dumps(output_schema)}


                """
                }
            ]
        )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result