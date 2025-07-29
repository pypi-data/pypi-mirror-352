import json
import asyncio


def annotation(openai_model,prompt, type_of_question):
    
    template="""
    {
    "nodes": [
        {
            "type": "",
            "text": "",
            "data": {  // Include this field only if the type is "logic"
                "subtype": ""  
            }
        }
    ],
    "questionType": "questionType"
}

# """
#     print("the variable keyword is :", variable_list_keyword)

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        # model="o1",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[ 
            {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
            {"role": "user", "content": f"""
            

                You are a precise survey question annotator. Your task is to tag all parts of a survey question into a JSON structure following a node-based annotation system. 
                The most important rule is to NEVER delete, modify, or rearrange any part of the input text. Each part of the text must be categorized appropriately without loss.
                line breaks should be explicitly captured using {{type: “linebreak”}}. Please introduce linebreaks wherever you feel necessary in order to make it visually correct.
                
                We currently support the following logics: randomize, skips, terminate, range, ask_if, piping. (these will be the values of the subtype in the data)
                If you encounter any of these logics, ensure they are captured under the logic type.
                There may be multiple ways to write a logic. For example:
                Variants such as "End," "Route to terminate," and "Terminate" should all be categorized under Terminate.
             
               
             
             
                Make sure to add the question type in the JSON under a field called questionType, this question has been catrgorized as : {type_of_question}

                Annotation Guidelines:
                - Use the following node types:
                  - {{type: “label”, text: “S5_Q20”}}: Represents a label for the question. (The label is the unique identifier given before the question starts)
                  - {{type: “question_text”, text: “Demo question main text?”}}:  The main text of the question shown to the survey taker. remember that we dont want to show any programmer notes or notes to the user in the question_text, it should only have the main question text which will be shown to the user taking the survey.
                  - {{type: “linebreak”}}: Indicates a line break character in the input. Line breaks in the input will be explicitly marked as <lbr />
                  - {{type: “not_displayed”, text: “any other random text”}}: Any text we wont be showing it to the person taking the survey.  
                  - {{type: “logic”, text: “Any text that shows a logic”, data: {{subtype: ""}} }}:  Represents logical conditions or rules. Include a data field for subtypes. (The subtype can be  : Randomize, Skips, Terminate, Range, Ask if, Piping. )
                  - {{type: “options”, text: “India”}}: For selectable options in the survey.
                {{type: "questionType","text":""}} : the questionType for this question is : {type_of_question}
             
                Each question must have : "label" and "question_text". Always ensure that the label is short and appears before the question starts. like "Qm, Q8, Qnkl." something like this. 
                Important: A question label must be a unique identifier and cannot consist of more than one word. Examples include "Q1.", "5Kn.", etc. Pay close attention to this requirement.
                A label can be followed by instructions and then the question_text. Be thoughtful and precise when choosing the label.
                The “label” may be followed by an instruction, so exercise judgment when determining this.
                Keep in mind that a label cannot be a complete sentence; it is just a concise identifier that precedes the question text.
                - Do not interpret or deduce meaning. Just tag text based on the input.
                - Important: add any linebreaks where needed with {{type: "linebreak"}}.
                - Preserve all formatting from the input.

                - the incoming text can be in any language so please make sure to capture everything accordingly.

                Example Input:
                S5_Q20 <lbr />
                Demo Question Main text? <lbr />
                Any terminate logical statement  for example<lbr />
                op1, op2, op3<lbr />
                random unclear text that we cant understand.

                Example Output:
                {{
                "nodes": [
                {{
                  {{type: "label", text: "S5_Q20 "}},
                  {{type: “linebreak”}}
                  {{type: "question_text", text: "Demo Question Main text? "}},
                  {{type: “linebreak”}}
                  {{type: "logic", text: "Any terminate logical statement  for example", "data" : {{"subtype":"terminate"}}}},
                  {{type: “linebreak”}}
                  {{type: "options", text: "op1"}}
                  {{type: “not_displayed”, text: “, ”}}
                  {{type: "options", text: "op2}}
                  {{type: “not_displayed”, text: “, ”}}
                  {{type: "options", text: "op3}}
                  {{type: “linebreak”}}
                  {{type: “unknown”, text: “random unclear text that we cant understand.”}}
                }}
                ],
                "questionType":"single_select"
                }}

                please follow this template to structure your output: {template}
                Most important: 
            
                1. Preserve all formatting from the input.
                2. you are not supposed to add anything or modify the text. 
                3. imp: you may add linebreaks wherever required to format it correctly.
                5. Make sure to correctly capture the question_text. understand what will be shown to the user as they will be taking that survey question.
                
                you are not supposed to add anything or modify the text. 
                Please give me a valid json
                
                the input text for which you have to create annotations is  : {prompt}
                
                

            """
            }
        ]
    ) 

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result








