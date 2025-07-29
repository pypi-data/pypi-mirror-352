
import modal
import json
from openai import OpenAI
from CreateSection.Functions.image import survey_generator


app = modal.App()


@app.cls(
    image=survey_generator,
    secrets=[modal.Secret.from_name("openai-secret")]
    # enable_memory_snapshot=True
)
class SurveyGen:
    
    def __init__(self):
       
        openai_client = OpenAI(api_key="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")
        self.client_open_ai=OpenAI(api_key="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")
        

    def generate_raw_data_for_questions(self,objective, number_of_questions, details):



        # parsed_text = self.client_open_ai.chat.completions.create(
        parsed_text = self.client_open_ai.chat.completions.create(
           
            model="gpt-4.1",
            # max_tokens=4000,
            response_format={ "type": "json_object" },
            temperature=0.00000001,
            messages=[
                {"role": "system", "content": "You are an expert AI agent that creates one of the best survey questionnaire in the world, you specialize in creating questions that can be used to build a survey to accomplish the objective. You are also an expert in creating questions that can be used to screen out or terminate the survey based on some condiiton given the objective"},
                {"role": "user", "content": f"""
The objective from the user is: {objective},
your task is to generate a JSON containing {number_of_questions} questions that can be used to build a survey to accomplish the objective. 
Following are some intructions on how to create the questions: {details}
I am also sharing you the questions which are already present in the survey (it's just the question labels and the main question text). please keep them in reference while creating the questions. (the question labels should be unique and not repeated). 
You have to generate me the raw text of the question, along with their options in any: The questions could be of type: single-select, multi-select, single-text, multi-text, grid (questions with rows/groups and columns/items), number, currency, year, percentage, percentage_sum, nps, message {", maxdiff" if number_of_questions >7 else ""}
message type is "the introductory or concluding text we see on the survey" and nps is the "net promoter score"
{"try to create 1 maxdiff, for max diff please add in the raw data of the question - number of screens and number of tasks per screen" if number_of_questions >7 else ""}
each raw text of data should have questionLabel, question, question_type, options (if any), columns(only for grid type questions), rows (only for grid type questions) and logics if any.
for example:
Q11. This is just a test example
(multi select) (randomize)
Example option 1
Example option 2
Example option 3
Example option 4

Also while creating questions, it is possible that the objective you receive might ask you to screen out or terminate the survey based on some condiiton, so if you come across any question which says to terminate them in the options, right next to the option please have (End Survey) in the text. Along with Terminate we support (Skip to QuestionLabel). If you come across any logic which might need us to skip to next question in order to fulfill the logic. please add (Skip to QuestionLabel) next to the options. Please see the following examples:
example: 
Q2. This is just a test example (single select)
Example option 1 (End Survey)
Example option 2 (Skip to Q3)
Example option 3
Example option 4

some instructions:
1. Keep the introduction (if there is one) minimal and high-level. (we donot want to add any bias)
2. Organize questions properly, make sure the questions are coherent and the flow is proper.
3. Each question should focus on one topic only (no double-barreled questions)
4. Avoid Yes/No questions unless asking about factual information (to reduce bias).
5. Use response options that are mutually exclusive and exhaustive.
6. Avoid jargon or technical terms — keep language simple and clear.
7. Randomize list options when appropriate (not for items that follow a natural sequence).
8. When appropriate, ask about both current behavior/perceptions and future expectations.


When generating questions and answer options, include conditional logic where appropriate.
For example, if a follow-up question (e.g., Q12) only applies if the respondent answered "Yes" to the previous question (e.g., Q11), indicate this explicitly before the question using "Q12. (Ask if Q11==1) Main question....
Q12. (Ask if Q11==1 ) If you like sports..  (here 1 was the option number of the Yes) 
Important: donot use "includes" in the condition, use "==" instead. for example : Ask if Q11 includes "1" is wrong, it should be Ask if Q11=="1".
Use only the option number in the condition and not the option text.
And donot create questions that have "ASK IF !=".. if you have any ask in a question, it should only have "==" in the condition and not "!=" 
Important: any ask if logic should only point to the option number and not the option text.
Then, only include Q12 as a follow-up to "Yes", and continue with Q13 for "No" without asking Q12.
Make sure to add the "(Skip to QXX)" logic consistently wherever needed.
Please make the next set of questions coherent and keeping in mind the previous questions, Remember you create one of the best survey questionnaire in the world. Also, please donot create any logic to a question label which does not exist in the survey yet. (that logic will be invalid). for example. If you ever create a logic which says "skip to Q11" then Q11 should be also there in the questions you generate. 
if there are No previous questions, then make sure to start the survey with a message type question (introduction). If it is a screener section, then please add questions that can be used to screen out or terminate the survey based on some condiiton given the objective.
Very Important: Each option should be added in a new line.
For grid-type questions, options should be replaced with rows and columns instead of using the options dictionary. (make sure to properly assign rows and columns to the options)
If the user objective has any logic for screening out or terminating respondents, please add that logic next to the options. You may use multiple logics like skips and End Survey in the same question.
Please generate me an array containing {number_of_questions} questions raw text in an array.
Try to include a variety of question types in the JSON output.
Each question should be a **raw text string** in the format of a natural question, without structured key-value JSON formatting in the value.
please give me a json with a list of questions.
Format:
{{ "questions": ["Q1. Actual question text in plain English ", "Q2. Actual question text in plain English", "Q3. Actual question text in plain English"] 
}}

Important: Keep in mind, that our end goal is to meet the user's objective. We should critically think about the questions we generate, if they are able to meet the user's objective.
Your survey will be judged on the following criteria:
1. Objective Alignment: Questions must directly support the stated objective and stay on topic.
2. Clarity and Language: Questions should be simple, clear, and free from jargon or confusion.
3. Validity: The survey must fully cover the intended topic and measure the right concepts.
4. Reliability: Questions should produce consistent answers across similar respondents.
5. Bias and Neutrality: Language must be neutral, avoiding any leading or suggestive phrasing.
6. Question Type and Balance: Use a mix of question types and ensure options are balanced and complete.
7. Length and Flow: The survey should have a logical flow and be appropriate in length.
8. Respondent Engagement: Keep the survey interesting and avoid confusing or tiring questions.
9. Representativeness Potential: Questions should help capture data representative of the target group.
10. Actionability of Responses: Responses collected must provide clear, actionable insights.
please give me a valid json.
Please generate the questions for the objective: {objective} 
            """ }
            ],
        )
        

        content = parsed_text.choices[0].message.content
        result=json.loads(content)

        return result
