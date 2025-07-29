import time
import requests
from Functions.helper import *
from fastapi import Request, HTTPException
from Question_TypesV2.categorizer import categorizer_for_questions
from Question_TypesV2.single_select import single_select_question, single_select_logic
from Question_TypesV2.nps import nps_question, nps_logic
from Question_TypesV2.contact_form import contact_form_question
from Question_TypesV2.currency import currency_question, currency_logic
from Question_TypesV2.year import year_question, year_logic
from Question_TypesV2.number import number_question, number_logic
from Question_TypesV2.ranking import ranking_question, ranking_logic
from Question_TypesV2.transition import transition_question
from Question_TypesV2.single_text import single_text_question, single_text_logic
from Question_TypesV2.grid import grid_question, grid_logic
from Question_TypesV2.percentage import percentage_question, percentage_logic
from Question_TypesV2.percent_sum import percent_sum_question, percent_sum_logic
from Question_TypesV2.notes import notes_question
from Question_TypesV2.maxdiff import maxdiff_question
from Question_TypesV2.multi_text import multi_text_question, multi_text_logic
from Question_TypesV2.multi_select import multi_select_question, multi_select_logic
from Question_TypesV2.ask_if import ask_if_logic
from Question_TypesV2.hidden_variable import hidden_variable_question
from Question_TypesV2.multi_percentage import multi_percentage_question, multi_percentage_logic
from Question_TypesV2.van_westendorp import van_westerndorp_question
from Question_TypesV2.unknown import unknown_question
from Question_TypesV2.zip_code import zip_code_question, zip_code_logic
from Question_TypesV2.terminate import terminate_question
from Question_TypesV2.multi_select_grid import multi_select_grid_question, multi_select_grid_logic
from Question_TypesV2.clean_json import clean_json_with_backticks
from Question_TypesV2.ai_chat import ai_question
from Question_TypesV2.annotation import annotation, annotation_transition
from Question_TypesV2.categorizer_v2 import categorizer_for_questions_v2
from Question_TypesV2.sync import generate_sync
from Functions.post_learning import send_to_ingest_api
from Functions.get_learning import get_learning
from Question_TypesV2.split_questions import split_questions
from Functions.process_single_question import *
from Functions.get_learning import get_learning
import asyncio


from American_Directions.single_select import single_select_question_AMI, single_select_logic_AMI
from American_Directions.nps import nps_question_AMI, nps_logic_AMI
from American_Directions.contact_form import contact_form_question_AMI
from American_Directions.currency import currency_question_AMI, currency_logic_AMI
from American_Directions.year import year_question_AMI, year_logic_AMI
from American_Directions.number import number_question_AMI, number_logic_AMI
from American_Directions.ranking import ranking_question_AMI, ranking_logic_AMI
from American_Directions.transition import transition_question_AMI
from American_Directions.single_text import single_text_question_AMI, single_text_logic_AMI
from American_Directions.grid import grid_question_AMI, grid_logic_AMI
from American_Directions.percentage import percentage_question_AMI, percentage_logic_AMI
from American_Directions.percent_sum import percent_sum_question_AMI, percent_sum_logic_AMI
from American_Directions.notes import notes_question_AMI
from American_Directions.maxdiff import maxdiff_question_AMI
from American_Directions.multi_text import multi_text_question_AMI
from American_Directions.multi_select import multi_select_question_AMI, multi_select_logic_AMI
from American_Directions.hidden_variable import hidden_variable_question_AMI
from American_Directions.multi_percentage import multi_percentage_question_AMI, multi_percentage_logic_AMI
from American_Directions.van_westendorp import van_westerndorp_question_AMI
from American_Directions.unknown import unknown_question_AMI
from American_Directions.zip_code import zip_code_question_AMI, zip_code_logic_AMI
from American_Directions.terminate import terminate_question_AMI
from American_Directions.multi_select_grid import multi_select_grid_question_AMI, multi_select_grid_logic_AMI
from American_Directions.clean_json import clean_json_with_backticks
from American_Directions.ai_chat import ai_question_AMI
from American_Directions.annotation import annotation
from American_Directions.sync import generate_sync





async def process_single_question_wrapper(question_data, key_id, user_id, headers, openai_model, main_team_id, workspace_id,  use_ami,is_single_question=False, is_first_question=False):
        wrapper_start = time.perf_counter()
        print(f"Task started at {time.time()}")
        question_id = str(id(question_data))
        print(f"\n[Question {question_id}] Starting processing at {wrapper_start:.2f}s")
    
        

        if is_single_question or is_first_question:
            if '<lbr />' in question_data:
                first_part, input_text = question_data.split('<lbr />', 1)
                print("the first part is :", first_part)
                print("the input text is:",input_text)
                
            else:
                first_part = "unknown"
                input_text = question_data 
        else:
            # For subsequent questions in a batch, don't split
            first_part = "unknown"
            input_text = question_data
        
        
        
        

        # Get keymap data
        # keymap names are 
        keymap_names = []
        if headers and 'authorization' in headers and 'team_id' in headers:
            auth_token = headers.get('authorization')
            team_id = headers.get('team_id')
            api_headers = {
                'authorization': auth_token,
                'team_id': team_id
            }
            try:
                response = requests.get(
                    'https://visceralos.com/survey_variables_keymap',
                    headers=api_headers
                )
                response.raise_for_status()
                keymap_data = response.json()
                keymap_names = list(keymap_data['keymap'].keys())
            except requests.RequestException as e:
                print(f"HTTP error occurred: {e}")
                raise HTTPException(status_code=500, detail="Failed to fetch keymap data")

        # Get result dict
        print("keymap_names are ",keymap_names)

       
        
        # Process tags
        user_changes=False
        input_text_for_annotation, user_changes = remove_tags(input_text)
        input_text_for_annotation = input_text_for_annotation.replace("\n", "<lbr />")
        tags = extract_and_generate_prompts(input_text)
        variable_list_keyword, variable_name=check_keywords_and_create_prompt(input_text_for_annotation,keymap_names)
        # print("the variable lsit is :",variable_list_keyword)
        general_tagged = tags.get("general",None)
        logic_tagged = tags.get("logic", None)
       

        # learning=await get_learning(input_text_for_annotation,user_id,main_team_id,1)
        # print("the learning is :", learning)

        result_dict, has_data = process_survey_learning(user_id)
        
        
        # Identify question type
        if "undefined" in first_part.lower().lstrip() or "unknown" in first_part.lower().lstrip():
            identified_type = categorizer_for_questions_v2(openai_model, input_text_for_annotation)
            identified_type_of_question = identified_type.get("type")

        else:
            identified_type_of_question = first_part
        print("question type identified is :", identified_type_of_question)

        

        async def get_annotation(question_type):
            start_time = time.perf_counter()
            
            
            if use_ami:
                if question_type in ["transition", "notes"]:
                    result = await annotation_transition(openai_model, input_text_for_annotation, keymap_names, identified_type_of_question,general_tagged,  variable_list_keyword=variable_list_keyword)
                    print("output from annotation layer is: ",result)
                    result["nodes"].extend([
                        {'type': 'linebreak'},
                        {'type': 'linebreak'},
                        {'type': 'linebreak'}
                    ])
                else:
                    result = await annotation(openai_model, input_text_for_annotation, keymap_names, identified_type_of_question,general_tagged, variable_list_keyword=variable_list_keyword)
                    print("output from annotation layer is: ",result)
                    result["nodes"].extend([
                        {'type': 'linebreak'},
                        {'type': 'linebreak'},
                        {'type': 'linebreak'}
                    ])
                
            else:
                
                result = await annotation(openai_model, input_text_for_annotation, keymap_names, identified_type_of_question,general_tagged, variable_list_keyword=variable_list_keyword)
                print("output from annotation layer is: ",result)
                result["nodes"].extend([
                        {'type': 'linebreak'},
                        {'type': 'linebreak'},
                        {'type': 'linebreak'}
                    ])
            
            end_time = time.perf_counter()
            print(f"├── Total time for annotation: {end_time - start_time:.3f}s")
            
            return result
        

        async def process(sync_instructions):
            
            start_time_process = time.perf_counter()


            if identified_type_of_question=="single-select":
                print("we are in single select block")

                if use_ami:
                    one=single_select_question_AMI(openai_model,input_text_for_annotation,sync_instructions, general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=single_select_logic_AMI(openai_model,one,result_dict, input_text_for_annotation, logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                else:

                    one=single_select_question(openai_model,input_text_for_annotation,sync_instructions, general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=single_select_logic(openai_model,one,result_dict, input_text_for_annotation, logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)



            
            elif identified_type_of_question=="nps":
                print("we are in nps block")
                
                if use_ami:
                    one=nps_question_AMI(openai_model,input_text_for_annotation,sync_instructions, general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=nps_logic_AMI(openai_model,one,result_dict,input_text_for_annotation, logic_tagged)
                    print("LLM Layer 2 Output : : ",two)
                
                else:

                    one=nps_question(openai_model,input_text_for_annotation,sync_instructions, general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=nps_logic(openai_model,one,result_dict,input_text_for_annotation, logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            


            elif identified_type_of_question=="ai-chat":
                print("we are in ai_chat block")

                if use_ami:

                    one=ai_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=one

                else:

                    one=ai_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                
                    two=one

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="contact-form":
                print("we are in contact-form block")

                if use_ami:
                    one=contact_form_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=one
                    print("LLM Layer 2 Output : : ",two)

                else:
                    one=contact_form_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=one
                    print("LLM Layer 2 Output : : ",two)
                
                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)
                

            elif identified_type_of_question=="currency":

                print("we are in currency block")

                if use_ami:
                    one=currency_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=currency_logic_AMI(openai_model,one,result_dict, input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)
                
                else:

                    one=currency_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=currency_logic(openai_model,one,result_dict, input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="terminate":

                print("we are in transition block")

                if use_ami:

                    one=terminate_question_AMI(openai_model,input_text_for_annotation)
                    print("LLM Layer 1 Output : : ",one)

                    two=one
                    print("LLM Layer 2 Output : : ",two)
                
                else:


                    one=terminate_question(openai_model,input_text_for_annotation)
                    print("LLM Layer 1 Output : : ",one)

                    two=one
                    print("LLM Layer 2 Output : : ",two)


                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="year":

                print("we are in year block")
                
                if use_ami:
                    one=year_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=year_logic_AMI(openai_model,one,result_dict,input_text_for_annotation, logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                else:


                    one=year_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=year_logic(openai_model,one,result_dict,input_text_for_annotation, logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="number":

                print("we are in number block")

                if use_ami:

                    one=number_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=number_logic_AMI(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)
                
                else:


                    one=number_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=number_logic(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)


            elif identified_type_of_question=="ranking":

                print("we are in ranking block")

                if use_ami:

                    one=ranking_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=ranking_logic_AMI(openai_model,one,result_dict,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                else:
                    one=ranking_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=ranking_logic(openai_model,one,result_dict,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="transition":

                print("we are in transition block")
                
                if use_ami:
                    one=transition_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=one
                    print("LLM Layer 2 Output : : ",two)
                
                else:
                    one=transition_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                
                    two=one
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)


            elif identified_type_of_question=="single-text":

                print("we are in single text block")

                if use_ami:
                    one=single_text_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=single_text_logic_AMI(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                else:
                

                    one=single_text_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=single_text_logic(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="grid":

                print("we are in grid block")

                if use_ami:
                    one=grid_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=grid_logic_AMI(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)
                
                else:
                    

                    one=grid_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=grid_logic(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="multi-select-grid" or identified_type_of_question=="multi_select_grid" or identified_type_of_question=="multi-grid" or identified_type_of_question=="multi_grid":

                print("we are in multi select grid block")

                if use_ami:
                    one=multi_select_grid_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=multi_select_grid_logic_AMI(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)
                
                else:
                
                    one=multi_select_grid_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=multi_select_grid_logic(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            
            elif identified_type_of_question=="percentage":

                print("we are in percentage block")

                if use_ami:
                    one=percentage_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=percentage_logic_AMI(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                else:
                    one=percentage_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=percentage_logic(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="percent-sum":

                print("we are in percent-sum block")

                if use_ami:
                    one=percent_sum_question_AMI(openai_model,input_text_for_annotation,sync_instructions, general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=percent_sum_logic_AMI(openai_model,one,result_dict,input_text_for_annotation, logic_tagged)
                    print("LLM Layer 2 Output : : ",two)
                
                else:


                    one=percent_sum_question(openai_model,input_text_for_annotation,sync_instructions, general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=percent_sum_logic(openai_model,one,result_dict,input_text_for_annotation, logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="notes":

                print("we are in notes block")

                if use_ami:
                    one=notes_question_AMI(openai_model,input_text,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    two=one
                
                else:
                    one=notes_question(openai_model,input_text,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=one

            elif identified_type_of_question=="maxdiff":

                print("we are in maxdiff block")

                if use_ami:
                    one=maxdiff_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    # two=maxdiff_logic(openai_model,one,result_dict)
                    two=one
                    print("LLM Layer 2 Output : : ",two)

                else:


                    one=maxdiff_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    # two=maxdiff_logic(openai_model,one,result_dict)
                    two=one
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="multi-text" or identified_type_of_question=="multi_text" :

                print("we are in multi_text block")

                if use_ami:

                    one=multi_text_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    # two=multi_text_logic(openai_model,one,result_dict,input_text_for_annotation, logic_tagged)
                    # print("LLM Layer 2 Output : : ",two)
                    two=one
                
                else:


                    

                    one=multi_text_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    # two=multi_text_logic(openai_model,one,result_dict,input_text_for_annotation, logic_tagged)
                    # print("LLM Layer 2 Output : : ",two)
                    two=one
                

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="multi-select":

                print("we are in multi_select block")

                if use_ami:
                    one=multi_select_question_AMI(openai_model,input_text_for_annotation,sync_instructions, general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=multi_select_logic_AMI(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                else:

                    one=multi_select_question(openai_model,input_text_for_annotation,sync_instructions, general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=multi_select_logic(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="variable" or identified_type_of_question=="hidden_variable":

                print("we are in hidden variable block")

                if use_ami:

                    one=hidden_variable_question_AMI(openai_model,input_text_for_annotation,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    two=one

                else:


                    one=hidden_variable_question(openai_model,input_text_for_annotation,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    two=one
                    
                # two=multi_select_logic(openai_model,one,result_dict)
                # print("LLM Layer 2 Output : : ",two)

                    

            elif identified_type_of_question=="multi-percentage":

                print("we are in multi_percentage block")

                if use_ami:
                    one=multi_percentage_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=multi_percentage_logic_AMI(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)
                    two=one

                else:

                    one=multi_percentage_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=multi_percentage_logic(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)
                    two=one

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            elif identified_type_of_question=="van-westendorp":

                print("we are in Van Westerndorp block")
                
                if use_ami:

                    one=van_westerndorp_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    # two=multi_select_logic(openai_model,one,result_dict)
                    # print("LLM Layer 2 Output : : ",two)
                    two=one

                else:

                    one=van_westerndorp_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    # two=multi_select_logic(openai_model,one,result_dict)
                    # print("LLM Layer 2 Output : : ",two)
                    two=one

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)


            elif identified_type_of_question=="unknown":
                print("this is an unknown question, we will print out the entire question as it is , saying we dont understand this questions")
                one=unknown_question(openai_model,input_text_for_annotation,general_tagged)
                two=one

            elif identified_type_of_question=="zip_code" or identified_type_of_question=="zipcode":

                print("we are in zip code block")

                if use_ami:
                    one=zip_code_question_AMI(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=zip_code_logic_AMI(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                else:


                    one=zip_code_question(openai_model,input_text_for_annotation,sync_instructions,general_tagged)
                    print("LLM Layer 1 Output : : ",one)
                    
                    two=zip_code_logic(openai_model,one,result_dict,input_text_for_annotation,logic_tagged)
                    print("LLM Layer 2 Output : : ",two)

                if two.get("ask_logic",""):
                    print("we are processing ask if logic now:")
                    two=ask_if_logic(openai_model,two)
                    print("Answer after Ask if : ",two)

            else:
                print("Error in understanding the question")
                two={"questionLabel":"",
                    "question":input_text_for_annotation,
                    "type":"unknown"}
                
        


            extended_keys = ["number_logic", "currency_logic", "year_logic", "percentage_logic", 
                            "single_text_logic", "nps_logic", "zip_code_logic"]
            two = clean_dictionary_values(two, extended_keys)
            two = process_question_json(openai_model, two)
            two = clean_extra_text(two)



            print("this is before processing : ", two)
            processed=  process_single_question(two,input_text_for_annotation,key_id, variable_name, use_ami, openai_model)
            end_time_process = time.perf_counter()
            
            print(f"├── Total time for process: {end_time_process - start_time_process:.3f}s")
            
            return processed
        
        
        
        

        annotated_text=await get_annotation(question_type=identified_type_of_question)

        input_for_parser=filter_nodes(annotated_text)
        
        print("Input for parser is : ", input_for_parser)
        processed_question= await process(input_for_parser)

        try:
            if not use_ami: 
                extracted_text = extract_question_text(annotated_text)
                print("the extarcted text is : ", extracted_text)
                if extracted_text:
                    processed_question["question"] = extracted_text
                    processed_question["mdText"] = extracted_text
                else:
                    print("No question text nodes found in the input")
        except KeyError:
            print("Could not find 'nodes' in the input data")
        except Exception as e:
            print(f"Could not convert the nodes to question text: {str(e)}")


       

        # processed_question=convert_line_breaks(processed_question)
        
    
        
        
        process_end = time.perf_counter()
        print(f"[Question {question_id}] Main processing completed in {process_end - wrapper_start:.2f}s")

        question_uuid=processed_question.get("id",generate_nano_id())

        asyncio.create_task(send_to_ingest_api( annotated_text=annotated_text, processed_question=processed_question, raw_text=input_text_for_annotation, workspace_id=workspace_id, main_team_id=main_team_id,  question_id=question_uuid, user_id=user_id , user_changes=user_changes))

        print(f"Task ended at {time.time()}")
        return [{
            "annotated_data": annotated_text,
            "survey_data": processed_question
        }]
