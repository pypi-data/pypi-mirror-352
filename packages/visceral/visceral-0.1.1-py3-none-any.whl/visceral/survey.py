# from typing import Optional
# import json
# import modal
# import pydantic  # for typing, used later
# from typing import Optional, Dict, List, Union, Any
# import uuid
# import os
# from fastapi import FastAPI, WebSocket
# import random
# import string
# import re
# from typing import Dict, Any
# import asyncio
# from pydantic import BaseModel, Field
# import time
# import httpx
# from fastapi import Request, HTTPException
# from openai import OpenAI
# from Functions.helper import log_time
# from Functions.process_single_question_wrapper import *
# from Question_TypesV2.number_of_question import *
# from Question_TypesV2.split_questions import split_questions
# import httpx
# from Functions.images import Input_FE
# from asyncio import to_thread
# from concurrent.futures import ProcessPoolExecutor
# from Functions.images import *
# from Functions.check_user_status import check_user_status
# from Functions.accept_suggestion import accept_suggestion
# from typing import List, Optional, Literal
# import asyncio
# import time
# import pydantic
# from modal import web_endpoint, Secret, app
# from fastapi import Request
# from Functions.router import router_prompt
# from Cursor.general_chat import general_chat
# from Cursor.add_question import add_question
# from Cursor.add_section import add_section
# from Cursor.delete_a_question import delete_question
# from Cursor.find_question_text_from_label import find_question_text_by_label
# from CreateSection.Functions.annotation import annotation
# from CreateSection.Functions.process_questions_in_parallel import process_questions_parallel
# from CreateSection.Functions.transform_survey_data import *
# from CreateSection.Functions.image import survey_generator
# from CreateSection.Functions.identify_questions import SurveyGen
# from CreateSection.Functions.identify_questions import *
# from Cursor.generate_new_label import generate_next_question_label
# from Cursor.delete_question_from_payload import delete_question_by_label
# from CreateSection.Functions.extract_survey_questions import extract_survey_questions
# from Edit_Selection.prompts.correction import correction_prompt
# from CreateSection.Functions.get_block_names import get_block_names
# from Functions.get_complete_questions import generate_complete_questions
# from Cursor.finalize_objective import finalize_survey_objective
# from Cursor.objective import determine_objective
# from Functions.create_conversation import extract_conversation_from_metadata
# from Cursor.recommend_sections import recommend_sections
# from Functions.extract_question_labels import extract_question_labels
# from Cursor.edit_from_chat import correction_prompt_via_chat
# from Functions.get_question_data_from_label import find_question_by_label
# import requests

# from Functions.recommend_provider_segments import recommend_provider_segments
# import websockets
# from starlette.websockets import WebSocketState
# from Cursor.budget_details import budget_details
# from Functions.router_publshed import router_prompt_published
# from Functions.extract_block_names import extract_block_names
# from Functions.delete_sections import delete_sections
# from Functions.optimize_survey_instructions import optimize_survey_instructions
# from Functions.get_complete_payload import generate_complete_questions_payload
# from Cursor.recommed_sections_to_optimize import recommend_sections_to_optimize
# from Cursor.add_section_for_optimize import add_section_for_optimize
# from Functions.estimate_time import estimate_time
# from Functions.request_bid import request_bid
# from Cursor.validate import validate_survey
# from Functions.get_raw_data import get_raw_data
# from Cursor.fix_post_validation import fix_post_validation
# from Functions.finalize_bid import finalize_bid
# from Functions.extract_first_section import extract_first_section
# from Cursor.quota import quota_creator

# app = modal.App("Create Survey")


# with open("CreateSection/Functions/screener_section.json", "r") as f:
#     readymade_screener_section = json.load(f)

# @app.cls(
#     image=categorizer,
#     secrets=[modal.Secret.from_name("openai-secret")]
#     # enable_memory_snapshot=True
# )
# class OpenAIModel:

#     def __init__(self):
#         self.client_open_ai = OpenAI()
 
        
        

# @app.function(image=testing_image, secrets=[modal.Secret.from_name("openai-secret")], timeout=2000, min_containers=1)
# @modal.asgi_app(label="create-survey")
# def create_survey():
#     fastapi_app = FastAPI()
#     client = OpenAI()
#     survey_gen = SurveyGen()
    

#     @fastapi_app.websocket("/ws")
#     async def new_text_editor_v2(websocket: WebSocket):
#         await websocket.accept()
#         objective_finalized = False
#         current_chances = 1
#         final_user_objective = None
#         refined_user_objective = None
#         change_in_sample_specs = False
#         openai_model = OpenAIModel()

#         sample_specs={
#                         "target_audience": "",
                        
#                     }
#         try:
#             # Infinite loop to keep the connection alive
#             while True:
#                 # Wait for incoming messages
#                 try:
#                     data = await websocket.receive_json()
#                     data_from_api = Input_FE(**data)

#                     objective=data_from_api.objective
                    
#                     create_survey=True

#                     if create_survey == True:
#                         response = recommend_sections(openai_model, objective)
#                         section_recommendations = response["recommend_sections_schema"]
                        
#                         # Get the existing complete_survey_data ONCE before the loop
                        
#                         # Set up the complete_survey_data structure ONCE before the loop
#                         complete_survey_data = {
#                             "blocks": [],
#                             "annotated_data": []
#                         }
                        
                        
#                         overall_section_index = len(complete_survey_data["blocks"])
                        
#                         # Refresh questions_list from the initial complete_survey_data
                        
#                         # Process each section
#                         for section_idx, section in enumerate(section_recommendations):
#                             section_name = section["section_name"]
#                             question_count = section["number_of_questions"]
#                             section_details = section["details_about_section"]
                            
#                             response = add_section(openai_model, section_details)
#                             section_name = response.get("section_name")
#                             number_of_questions = response.get("number_of_questions")
#                             text = response.get("details_about_section")
                            
#                             request = {"blocks": [{"type": section_name, "number_of_questions": number_of_questions, "text": text}]}
                            
#                             # Process each block for this section
#                             all_blocks = []
#                             annotated_data_entries = []
                            
#                             for block_index, block in enumerate(request.get("blocks")):
#                                 block_type = block.get("type")
#                                 objective = block.get("text")
#                                 number_of_questions = block.get("number_of_questions")
                                
#                                 payload = {
#                                     "action": "SHOW_LOADER",
#                                     "loader_text": f"Now generating: {section_name}. This may take a few moments."
#                                 }
#                                 await websocket.send_json(payload)
#                                 await asyncio.sleep(0.2)

#                                 # Create a block-specific questions dictionary
#                                 block_questions = {}
#                                 question_index = 1  # Reset for each block
                                
#                                 # Generate questions based on block type using the current questions_list
#                                 result = survey_gen.generate_raw_data_for_questions(
#                                     objective=objective,
#                                     number_of_questions=number_of_questions,
#                                     details=objective, 
#                                 )
                                
#                                 if "questions" in result:
#                                     for question in result["questions"]:
#                                         key = f"{question_index}_d"
#                                         block_questions[key] = question
#                                         question_index += 1
                                
#                                 # Process the block questions
#                                 processed_block_questions = await process_questions_parallel(
#                                     SurveyGen,
#                                     block_questions,
#                                 )
                                
#                                 # Update block_questions with processed results
#                                 block_questions.update(processed_block_questions)
                                
#                                 # Transform block questions to structured data
#                                 processed_blocks = process_new_format_data(block_questions)
                                
#                                 # Use the existing transformation with only this block
#                                 transformed_block_data = transform_new_survey_data(processed_blocks)
                                
#                                 # If there's any data from transformation, update the name property
#                                 if transformed_block_data and len(transformed_block_data) > 0:
#                                     for block_data in transformed_block_data:
#                                         # Set block name to the current block type
#                                         block_data["name"] = block_type
                                        
#                                         # Calculate the block index based on existing blocks plus current section
#                                         current_block_index = overall_section_index + section_idx
#                                         block_data["label"] = chr(65 + current_block_index)  # A, B, C, ...
                                    
#                                     # Add the transformed data to our blocks list
#                                     all_blocks.extend(transformed_block_data)
                            
#                             # Extract annotated data for this section
#                             for block in all_blocks:
#                                 if "questions" in block:
#                                     for question in block["questions"]:
#                                         if "annotated_text" in question:
#                                             # Create properly structured annotated_data entry
#                                             annotated_entry = {
#                                                 "id": question["id"],
#                                                 "nodes": question["annotated_text"]["nodes"],
#                                                 "questionType": question["annotated_text"]["questionType"]
#                                             }
#                                             annotated_data_entries.append(annotated_entry)
                            
#                             # Add this section's blocks to the complete survey data
#                             complete_survey_data["blocks"].extend(all_blocks)
#                             complete_survey_data["annotated_data"].extend(annotated_data_entries)
                            
#                             # Create the payload for this section
#                         payload = {
#                             "meta": {
#                                 "action": "FINAL_SURVEY"    
#                             },
#                             "complete_survey_data": complete_survey_data
#                         }
                        
#                         # Add the complete_survey_data to the payload
#                         payload["complete_survey_data"] = complete_survey_data
                        
#                         # Send the response for this section
#                         await websocket.send_json(payload)

#                         # try:
#                         #     await websocket.close()
#                         # except Exception as e:
#                         #     pass
                        
                    
                
#                 except Exception as e:
#                     exception_name = type(e).__name__
#                     if any(name in exception_name for name in ["WebSocketDisconnect", "ConnectionClosed", "WebSocketError"]):
#                         print(f"Client disconnected: {str(e)}")
#                         break
#                     elif "ValueError" in exception_name:
#                         # Handle JSON parsing errors
#                         print(f"Invalid JSON received: {str(e)}")
#                         try:
#                             await websocket.send_json({"error": "Invalid data format"})
#                         except Exception:
#                             # If sending fails, client likely disconnected
#                             print("Failed to send error response, client likely disconnected")
#                             break
#                     else:
#                         # Handle other errors during processing
#                         print(f"Error processing request: {str(e)}")
#                         try:
#                             await websocket.send_json({"error": str(e)})
#                         except Exception:
#                             # If sending fails, client likely disconnected
#                             print("Failed to send error response, client likely disconnected")
#                             break
            
#         except Exception as e:
#         # This catches any exceptions not caught in the inner try-except
#             print(f"Outer exception in WebSocket handler: {str(e)}")
        
#         finally:
#             # Always execute this when the loop exits for any reason
#             print("WebSocket handler exiting, cleaning up...")
#             try:
#                 # Check if we can access the client_state property
#                 if hasattr(websocket, "client_state"):
#                     # Check if we should compare against a constant
#                     if hasattr(WebSocketState, "DISCONNECTED"):
#                         if websocket.client_state != WebSocketState.DISCONNECTED:
#                             await websocket.close(code=1000)
#                     # Otherwise use a string or other comparison
#                     else:
#                         if getattr(websocket.client_state, "DISCONNECTED", None) is not True:
#                             await websocket.close(code=1000)
#                 else:
#                     # Fallback - try to close anyway with exception handling
#                     try:
#                         await websocket.close(code=1000)
#                     except Exception:
#                         pass
#                 print("WebSocket connection closed gracefully")
#             except Exception as e:
#                 print(f"Error during WebSocket cleanup: {str(e)}")


#     return fastapi_app





from typing import Optional
import json
import modal
import pydantic  # for typing, used later
from typing import Optional, Dict, List, Union, Any
import uuid
import os
from fastapi import FastAPI, WebSocket
import random
import string
import re
from typing import Dict, Any
import asyncio
from pydantic import BaseModel, Field
import time
import httpx
from fastapi import Request, HTTPException
from openai import OpenAI
from Functions.helper import log_time
from Functions.process_single_question_wrapper import *
from Question_TypesV2.number_of_question import *
from Question_TypesV2.split_questions import split_questions
import httpx
from Functions.images import Input_FE
from asyncio import to_thread
from concurrent.futures import ProcessPoolExecutor
from Functions.images import *
from Functions.check_user_status import check_user_status
from Functions.accept_suggestion import accept_suggestion
from typing import List, Optional, Literal
import asyncio
import time
import pydantic
from modal import web_endpoint, Secret, app
from fastapi import Request
from Functions.router import router_prompt
from Cursor.general_chat import general_chat
from Cursor.add_question import add_question
from Cursor.add_section import add_section
from Cursor.delete_a_question import delete_question
from Cursor.find_question_text_from_label import find_question_text_by_label
from CreateSection.Functions.annotation import annotation
from CreateSection.Functions.process_questions_in_parallel import process_questions_parallel
from CreateSection.Functions.transform_survey_data import *
from CreateSection.Functions.image import survey_generator
from CreateSection.Functions.identify_questions import SurveyGen
from CreateSection.Functions.identify_questions import *
from Cursor.generate_new_label import generate_next_question_label
from Cursor.delete_question_from_payload import delete_question_by_label
from CreateSection.Functions.extract_survey_questions import extract_survey_questions
from Edit_Selection.prompts.correction import correction_prompt
from CreateSection.Functions.get_block_names import get_block_names
from Functions.get_complete_questions import generate_complete_questions
from Cursor.finalize_objective import finalize_survey_objective
from Cursor.objective import determine_objective
from Functions.create_conversation import extract_conversation_from_metadata
from Cursor.recommend_sections import recommend_sections
from Functions.extract_question_labels import extract_question_labels
from Cursor.edit_from_chat import correction_prompt_via_chat
from Functions.get_question_data_from_label import find_question_by_label
import requests

from Functions.recommend_provider_segments import recommend_provider_segments
import websockets
from starlette.websockets import WebSocketState
from Cursor.budget_details import budget_details
from Functions.router_publshed import router_prompt_published
from Functions.extract_block_names import extract_block_names
from Functions.delete_sections import delete_sections
from Functions.optimize_survey_instructions import optimize_survey_instructions
from Functions.get_complete_payload import generate_complete_questions_payload
from Cursor.recommed_sections_to_optimize import recommend_sections_to_optimize
from Cursor.add_section_for_optimize import add_section_for_optimize
from Functions.estimate_time import estimate_time
from Functions.request_bid import request_bid
from Cursor.validate import validate_survey
from Functions.get_raw_data import get_raw_data
from Cursor.fix_post_validation import fix_post_validation
from Functions.finalize_bid import finalize_bid
from Functions.extract_first_section import extract_first_section
from Cursor.quota import quota_creator

app = modal.App("Create Survey")


with open("CreateSection/Functions/screener_section.json", "r") as f:
    readymade_screener_section = json.load(f)

@app.cls(
    image=categorizer,
    secrets=[modal.Secret.from_name("openai-secret")]
    # enable_memory_snapshot=True
)
class OpenAIModel:

    def __init__(self):
        self.client_open_ai = OpenAI()
 
        



@app.function(image=testing_image, secrets=[modal.Secret.from_name("openai-secret")], timeout=2000, min_containers=1)
@modal.web_endpoint(method="POST")
async def create_survey(data: Input_FE):
    fastapi_app = FastAPI()
    client = OpenAI()
    survey_gen = SurveyGen()
    objective = data.objective
    openai_model = OpenAIModel()

    response = recommend_sections(openai_model, objective)
    section_recommendations = response["recommend_sections_schema"]
    
    # Get the existing complete_survey_data ONCE before the loop
    
    # Set up the complete_survey_data structure ONCE before the loop
    complete_survey_data = {
    "blocks": [],
    "annotated_data": []
}


    overall_section_index = len(complete_survey_data["blocks"])

    # Refresh questions_list from the initial complete_survey_data

    # Process each section
    for section_idx, section in enumerate(section_recommendations):
        section_name = section["section_name"]
        question_count = section["number_of_questions"]
        section_details = section["details_about_section"]
        
        response = add_section(openai_model, section_details)
        section_name = response.get("section_name")
        number_of_questions = response.get("number_of_questions")
        text = response.get("details_about_section")
        
        request = {"blocks": [{"type": section_name, "number_of_questions": number_of_questions, "text": text}]}
        
        # Process each block for this section
        all_blocks = []
        annotated_data_entries = []
        
        for block_index, block in enumerate(request.get("blocks")):
            block_type = block.get("type")
            objective = block.get("text")
            number_of_questions = block.get("number_of_questions")
            
            payload = {
                "action": "SHOW_LOADER",
                "loader_text": f"Now generating: {section_name}. This may take a few moments."
            }
            

            # Create a block-specific questions dictionary
            block_questions = {}
            question_index = 1  # Reset for each block
            
            # Generate questions based on block type using the current questions_list
            result = survey_gen.generate_raw_data_for_questions(
                objective=objective,
                number_of_questions=number_of_questions,
                details=objective, 
            )
            
            if "questions" in result:
                for question in result["questions"]:
                    key = f"{question_index}_d"
                    block_questions[key] = question
                    question_index += 1
            
            # Process the block questions
            processed_block_questions =  await process_questions_parallel(
                SurveyGen,
                block_questions,
            )
            
            # Update block_questions with processed results
            block_questions.update(processed_block_questions)
            
            # Transform block questions to structured data
            processed_blocks = process_new_format_data(block_questions)
            
            # Use the existing transformation with only this block
            transformed_block_data = transform_new_survey_data(processed_blocks)
            
            # If there's any data from transformation, update the name property
            if transformed_block_data and len(transformed_block_data) > 0:
                for block_data in transformed_block_data:
                    # Set block name to the current block type
                    block_data["name"] = block_type
                    
                    # Calculate the block index based on existing blocks plus current section
                    current_block_index = overall_section_index + section_idx
                    block_data["label"] = chr(65 + current_block_index)  # A, B, C, ...
                
                # Add the transformed data to our blocks list
                all_blocks.extend(transformed_block_data)
        
        # Extract annotated data for this section
        for block in all_blocks:
            if "questions" in block:
                for question in block["questions"]:
                    if "annotated_text" in question:
                        # Create properly structured annotated_data entry
                        annotated_entry = {
                            "id": question["id"],
                            "nodes": question["annotated_text"]["nodes"],
                            "questionType": question["annotated_text"]["questionType"]
                        }
                        annotated_data_entries.append(annotated_entry)
        
        # Add this section's blocks to the complete survey data
        complete_survey_data["blocks"].extend(all_blocks)
        complete_survey_data["annotated_data"].extend(annotated_data_entries)
        
        # Create the payload for this section
    payload = {
        "meta": {
            "action": "FINAL_SURVEY"    
        },
        "complete_survey_data": complete_survey_data
    }

    # Add the complete_survey_data to the payload
    payload["complete_survey_data"] = complete_survey_data

    return payload

