from CreateSection.Functions.processor_map_sync import *
import json
from CreateSection.Question_TypesV2.format import format_text
import requests
from CreateSection.Question_TypesV2.categorizer_v2 import categorizer_for_questions_v2
from CreateSection.Functions.annotation import annotation




def process_single_question_wrapper(openai_model_class, question_data):
    """Process a single question in a separate process"""
    
    
    key, original_value = question_data
    cleaned_original_value = original_value
    annotation_result = {"nodes": []} 
    
    try:
        openai_model = openai_model_class()
        
        if not key.endswith('_d'):
            if key.endswith('_Section'):
                return key, str(original_value)
            
            return key, original_value

 
        processor_map = get_processor_map_sync()
        question_type_identified= categorizer_for_questions_v2(openai_model,original_value)
        
        print("the question type identified is : ",question_type_identified)
        question_type = question_type_identified.get("type", "unknown")
        
        if question_type in processor_map:
            
            
            
            # if use_ami:
            #     annotation_result= annotation_ami(openai_model,cleaned_original_value,keymap_names,question_type)   
            # else:
            annotation_result= annotation(openai_model,original_value,question_type)    
      
            annotation_result["nodes"].extend([
                {'type': 'linebreak'},
                {'type': 'linebreak'},
                {'type': 'linebreak'}
            ])
      
            question_func, logic_func = processor_map[question_type]

            
            one = question_func(openai_model, original_value)
            
            if logic_func:
                final_json= logic_func(openai_model, one, original_value)
            else:
                final_json=one
            
            if final_json.get("ask_logic"):
                print("the input for ask if logic is :",final_json)
                final_json = ask_if_logic(openai_model, final_json)
            
        else:
            final_json = {
                "question": original_value,
                "questionLabel": "",
                "type": "unknown"
            }

        final_json['raw_data'] = cleaned_original_value
        final_json['annotated_text'] = annotation_result
        return key, final_json

    except Exception as e:
        print(f"Error processing question haha {key}: {str(e)}")
        return key, {
            "questionLabel": f"Unknown_{key}",
            "question": str(original_value) if isinstance(original_value, str) else json.dumps(original_value),
            "type": "unknown",
            "options": {},
            "columns": {},
            "rows": {},
            "logic": [],
            "Randomize": False,
            "raw_data": str(original_value)
        }
