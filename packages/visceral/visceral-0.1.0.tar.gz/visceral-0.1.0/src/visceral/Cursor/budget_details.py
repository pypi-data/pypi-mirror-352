import json
from utils import retry_on_json_error
from typing import List

@retry_on_json_error
def budget_details(openai_model, prompt):
        
    output_schema = {
        "top_recommendation": {"name of the company":"string","details":"details about the budget"},
        "alternatives": [{"alternative_1":"name of the company","details":"details about the budget"},{"alternative_2":"name of the company","details":"details about the budget"}] #list of dictionaries
    }
    
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": "You spceialise in properly giving the output in a json format."},
                {"role": "user", "content": f"""
You represent Visceral, a cutting-edge AI-native platform that modernizes market research by automating survey programming, quality testing, and analytics. Visceral integrates with major panel companies, data collection platforms, and GenAI systems, enabling surveys to run 10x faster at 50% cost while maintaining high standards for market researchers. It’s an open, A-to-Z platform with drag-and-drop and API capabilities, designed for rapid adoption without disrupting existing workflows or vendors.
You will be receving an input text, your goal is to correclty give me the output in markdown format. dont make headings etc. Focus more on the details using markdown formatting. like bold, italics, underline, bullet points, etc.
Please dont follow the same format as input text. make it better and dont keep everything in bold. a small starting line..
Also, for now we dont want to provide all the detials, but focus only on details like, based on your budget we have some panel companies that can help you collect the data and reach out to the audience. Then we maybe list the details and in the end we should also tell them that they can publish the survey themsleves if they want to. all this in a professional way. 
please give me a valid response in a json format.
keep the details short and concise. keep the values of number of completes and the budget in bold.
we support markdown formatting.
Also, in the end in small and italics add that this is a rough estimate and the actual cost may vary..
follow this output schema strictly:
{json.dumps(output_schema)}
The input text is: {prompt}
                """
                }
            ]
        )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result


