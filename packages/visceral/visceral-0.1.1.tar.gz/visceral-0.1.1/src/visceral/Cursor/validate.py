import json
from utils import retry_on_json_error

@retry_on_json_error
def validate_survey(openai_model, user_objective, survey):
    
    output_schema = {       
    "status": "string",  # must be one of 'Red', 'Yellow', 'Green'
    "objective_alignment_review":"string", # strengths of the survey but in terms of tick marks
    "editable_suggestions":"string", # weak points of the survey in terms of tick marks
    
    }  
    
    
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4.1",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": "You are an expert in survey design and evaluation with a deep understanding of research methodology, human behavior, and data collection techniques."},
                {"role": "user", "content": f"""
I want you to evaluate a survey based on its ability to fulfill a specific objective. Please assess the survey against the following key dimensions and provide detailed feedback on each. After the evaluation, include a summary with a score (1–10) for how well the survey aligns with the objective and actionable suggestions for improvement.
Objective of the Survey: {user_objective}
Evaluation Criteria:
1. Objective Alignment
Do the questions clearly relate to the stated objective?
Are there any questions that are irrelevant or off-topic?

2. Clarity and Language
Are the questions easy to understand?
Is there any ambiguity or use of technical jargon?
Are any questions double-barreled (asking two things at once)?

3. Validity
Does the survey comprehensively cover the topic it claims to measure?
Are the constructs being measured well represented by the questions?

4. Reliability
Could the same results be expected if the survey was repeated with a similar population?
Are there any questions that may result in inconsistent answers?

5. Bias and Neutrality
Are questions phrased in a neutral way?
Is there any leading or suggestive language?

6. Question Type and Balance
Is there a good mix of question types (Likert scale, multiple choice, open-ended)?
Are response options balanced and exhaustive?

7. Length and Flow
Is the survey too long, too short, or appropriate in length?
Does the question order make logical sense and flow well?

8. Respondent Engagement
Is the survey engaging enough to keep the respondent interested?
Are there questions that might cause fatigue or confusion?

9. Representativeness Potential
Based on the survey content, is it likely to collect data that is representative of the intended population?

10. Actionability of Responses
Will the collected responses provide actionable insights aligned with the stated objective?

based on the above criteia please give me :
1. the overall status of the survey ->  must be one of 'Red', 'Yellow', 'Green' donot use any emojis
2. Objective Alignment Review ( How well do the questions serve the stated objective? )
3. Editable Suggestions (For questions that are ambiguous or misaligned, show:
Suggested Rewrite: “Q3. What features of our product do you find most valuable?”

Donot scrutinize the questions in depth, No need to focus on wording, just see the flow and if there's anything very odd. 
Make sure you properly format your response using markdown. keep your responses terse and to the point. please have new lines in your sugggestions to make it more readable.
all your suggestions, if any should be complete.
if you are changing any grid type, make sure to add rows and columns to the grid. with the options in rows and columns.
for editing just give me the questions that can be edited, dont tell me to delete or add any questions.
We support Markdown formatting, so make sure to use it properly to make it more readable.
Keep all your responses extra small, crisp, concise and to the point. Be extremely terse.
please give me a valid response in a json format.

please follow this output schema strictly:
{json.dumps(output_schema)}

the survey to be evaluated is:
```
{survey}
```
                """
                }
            ]
        )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result



