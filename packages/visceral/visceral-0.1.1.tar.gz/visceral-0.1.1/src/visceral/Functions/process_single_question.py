from Functions.helper import clean_config_text, clean_option_text, format_label, map_config_ui, map_subtype, map_type, extract_logic_from_backticks
from Functions.process_logics import *
from Functions.nano_id import *
from Functions.maxdiff import *
import time
from Functions.dependencies import extract_dependencies
from Functions.process_text_for_ami_dir import process_text
def convert_lbr_to_newline(text):
    return text.replace('<lbr />', '\n')


def process_single_question(question_data: dict, raw_data:str, key_id=None, variable_list_keyword=None, use_ami=None, openai_model=None) -> dict:
    try:
        if not isinstance(question_data, dict):
            raise ValueError("Question data must be a dictionary")
        
        # Get basic question properties

        print("Value of use_ami: ",use_ami)

        if use_ami:
            label = question_data.get('Ref', '')
            if not label:
                label = format_label(question_data.get('questionLabel', '') or question_data.get('qstnLabel', ''))
        else:
            label = format_label(question_data.get('questionLabel', '') or question_data.get('qstnLabel', ''))



        # Don't clean the question text - preserve original
        # question_text, extracted_logic = extract_logic_from_backticks(question_data.get('question', ''), clean_text=True)
        print("the value of use_ami is ", use_ami)
        raw_question = question_data.get('question', '')

        # question_text_uncleaned = clean_question_text(raw_question)
        # question_text=clean_config_text(question_text_uncleaned)

        # question_text_uncleaned = clean_question_text(raw_question)
        question_text=clean_config_text(raw_question)

        
        question_type = question_data.get('type', '')
        if use_ami:
            question_text=process_text(openai_model, question_text, question_type)
        
        options = question_data.get('options', [])
        extra_text = question_data.get('extra_text', '')
        # extra_text=clean_question_text(text_after_options_uncleaned)
        dependencies = extract_dependencies(question_data)
        ask_logic = question_data.get('ask_logic', '')
        condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else None
        
        # Initialize processed question
        current_time = int(time.time() * 1000)
        has_options = bool(options)

        # Create base structure for extra_text
        base_structure = {
            "raw_data": raw_data,
            "dependencies":dependencies

        }

        if 'piping' in question_data and question_data['piping']:
            piping_config = {}
            
            for prev_question_label, pipe_type in question_data['piping'].items():
                current_question_label = label
                piping_filter = ""
                
                if pipe_type == 'show selected':
                    piping_filter = f"FILTER_X(OPTIONS({prev_question_label}), X IN {prev_question_label})"
                elif pipe_type == 'show not selected':
                    piping_filter = f"FILTER_X(OPTIONS({prev_question_label}), X NOT IN {prev_question_label})"
                elif pipe_type == 'hide selected':
                    piping_filter = f"FILTER_X(OPTIONS({current_question_label}), X IN {prev_question_label})"
                elif pipe_type == 'hide not selected':
                    piping_filter = f"FILTER_X(OPTIONS({current_question_label}), X NOT IN {prev_question_label})"
                
                if piping_filter:
                    piping_config["piping"] = piping_filter
            
            # Add piping_config to base_structure if it's not empty
            if piping_config:
                base_structure["optionConfig"] = piping_config



        if question_type == 'hidden_variable':
            definitions = []
            hidden_var_data = question_data.get('hidden_variable', {})
            
            # Process hidden_variable dictionary to create definitions
            # Instead of using enumerate, we'll use the value_label directly
            for value_label, condition in hidden_var_data.items():
                definitions.append({
                    "value": value_label,  # Use the year range as the value instead of sequential numbers
                    "condition": condition
                })
            
            return {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "variable",
                "issue": None,
                "label": label,
                "config": {},
                "mdText": convert_lbr_to_newline(question_text),
                "optout": {
                    "text": None,
                    "allowed": False
                },
                "created": current_time,
                "dynamic": False,
                "options": [],
                "updated": current_time,
                "condition": None,
                "confidence": 0.9,
                "definitions": definitions,
                **base_structure
            }


        if question_type in ['van_westendorp', 'van_westerndorp']:
            # Get the label from question data
            label = format_label(question_data.get('questionLabel', '') or question_data.get('qstnLabel', ''))
            
            # Initialize config with inputs array and currency from input data
            van_westendorp_config = {
                "inputs": [],
                "currency": question_data.get('currency', 'USD')  # Get currency from input, default to USD
            }
            
            # Process van_westendorp questions into inputs
            for i, question_text in enumerate(question_data.get('van_westerndorp', []), start=1):
                van_westendorp_config["inputs"].append({
                    "id": generate_nano_id(),
                    # "label": f"{i:02d}",
                    "label": str(i),
                    "helper": question_text
                })

            question_text_for_van_westerndorp=question_data.get("question","At what price do you think the product is too expensive?")
            
            # Get ask_logic condition if it exists
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            return {
                "id": key_id or generate_nano_id(),
                "text": question_text_for_van_westerndorp,
                "type": "van-westendorp",
                "label": label,
                "config": van_westendorp_config,
                "mdText": convert_lbr_to_newline(question_text_for_van_westerndorp),
                "created": current_time,
                "subtype": "",
                "updated": current_time,
                "condition": condition,
                **base_structure
            }



        if question_type == 'multi_percentage':
            # Get the label from question data
            
            label = format_label(question_data.get('questionLabel', '') or question_data.get('qstnLabel', ''))
            
            # Initialize config with inputs array
            multi_percentage_config = {
                "inputs": []
            }
            
            # Process options into inputs
            for i, option_dict in enumerate(question_data.get('options', []), start=1):
                for option_text, _ in option_dict.items():
                    multi_percentage_config["inputs"].append({
                        "id": generate_nano_id(),
                        # "label": f"{i:02d}",
                        "label":str(i),
                        "helper": option_text
                    })
            
            # Get ask_logic condition if it exists
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            return {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "multi-percentage",
                "label": label,
                "config": multi_percentage_config,
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "subtype": "",
                "updated": current_time,
                "condition": condition,
                **base_structure
            }

        if question_type == 'ranking':

            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            processed_options = []
            for i, option_dict in enumerate(options, start=1):
                for option_text, option_logic in option_dict.items():
                    # Determine option type
                    option_type = "user"
                    if "specify" in option_text.lower():
                        option_type = "other"
                        
                    processed_option = {
                        "id": generate_nano_id(),
                        "text": option_text,
                        "type": option_type,
                        "label": str(i),
                        "order": i - 1,
                        "mdText": convert_lbr_to_newline(option_text)
                    }
                    processed_options.append(processed_option)

            return {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "ranking",
                "label": label,
                "config": {
                    "randomize": question_data.get('randomize', False)
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "linked_options": variable_list_keyword if variable_list_keyword else None,
                "options": processed_options,
                "subtype": "",
                "updated": current_time,
                "condition":condition,
                **base_structure
            }
        
        if question_type == 'single_text':
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            processed_question = {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "text",
                "label": label,
                "config": {
                    "ui": None,
                    "randomize": False
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "updated": current_time,
                "skips": [],
                "optout": {"text": None, "allowed": False},
                "dynamic": False,
                "options": [],
                "condition": condition,
                "subtype": "single",
                "confidence": 0.9,
                **base_structure
            }

            
            
            # Process text logic if present
            if 'single_text_logic' in question_data:
                process_text_logic(question_data, processed_question, label)
                
            return processed_question
        
        if question_type == 'zip_code' or question_type =='zipcode':
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            processed_question= {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "zipcode",
                "label": label,
                "config": {
                    "country": question_data.get('country', None)
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "options": [],
                "updated": current_time,
                "httpStatus": 200,
                "condition":condition,
                **base_structure
            }

            if 'zip_code_logic' in question_data:
                process_zip_code_logic(question_data, processed_question, label)
                
            return processed_question
        

      

        if question_type == 'multi_text' or question_type=="multi-text":
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic

            options = question_data.get('options', [])
            config_inputs = []
            
            for index, option_dict in enumerate(options, 1):
                # Get the first (and only) key from each dictionary in the list
                option_name = next(iter(option_dict.keys())) if option_dict else ''
                # Check if option_name starts with NA
                helper_text = "" if option_name.startswith("NA") else option_name
                
                input_config = {
                    "id": generate_nano_id(),
                    "label": str(index),
                    "helper": helper_text
                }
                config_inputs.append(input_config)
            
            processed_question = {
                    "id": key_id or generate_nano_id(),
                    "text": question_text,
                    "type": "text",
                    "label": label,
                    "config": {
                        "inputs": config_inputs
                    },
                    "mdText": convert_lbr_to_newline(question_text),
                    "created": current_time,
                    "updated": current_time,
                    "skips": [],
                    "optout": {"text": None, "allowed": False},
                    "dynamic": False,
                    "options": [],
                    "condition": condition,
                    "subtype": "multi",
                    "confidence": 0.9,
                    **base_structure
                }
            
            
            # Process text logic if present
            if 'multi_text_logic' in question_data:
                process_text_logic(question_data, processed_question, label)
                
            return processed_question
        
        if question_type == 'ai-chat':
            # Get ask_logic condition if it exists
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            # Build the chat configuration structure directly from the input fields
            ai_chat_config = {
                "chat": {
                    "objective": question_data.get("objective",question_text),  # The objective comes from the question field
                    "openingMessage": question_data.get('opening_message', ''),
                    "closingMessage": question_data.get('closing_message', ''),
                    "questionLimit": question_data.get('questions_limit', 6),
                    "timeLimit": "",  # Default empty string as per example
                }
            }
            
            return {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "ai-chat",
                "label": label,
                "config": ai_chat_config,
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "subtype": "",
                "updated": current_time,
                "condition": condition,
                **base_structure
            }
            

    


        if question_type == 'contact_form':
            # Get the label from question data first
            label = format_label(question_data.get('questionLabel', '') or question_data.get('qstnLabel', ''))
            
            contact_config = {
                "inputs": []
            }
            
            default_fields = [
                ("firstname", "First Name"),
                ("lastname", "Last Name"),
                ("phone", "Phone Number"),
                ("email", "Email")
            ]
            
            # Use default fields if contact_form is empty
            if not question_data.get('contact_form'):
                for label_field, helper in default_fields:
                    contact_config["inputs"].append({
                        "id": generate_nano_id(),
                        "label": label_field,  # Changed from label to label_field to avoid confusion
                        "helper": helper
                    })
            else:
                # Keep the same field labels regardless of user input text
                for field in question_data['contact_form']:
                    if 'first' in field.lower():
                        contact_config["inputs"].append({
                            "id": generate_nano_id(),
                            "label": "firstname",
                            "helper": field
                        })
                    elif 'last' in field.lower():
                        contact_config["inputs"].append({
                            "id": generate_nano_id(),
                            "label": "lastname",
                            "helper": field
                        })
                    elif 'email' in field.lower():
                        contact_config["inputs"].append({
                            "id": generate_nano_id(),
                            "label": "email",
                            "helper": field
                        })
                    elif 'phone' in field.lower():
                        contact_config["inputs"].append({
                            "id": generate_nano_id(),
                            "label": "phone",
                            "helper": field
                        })
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic

            return {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "contact-form",
                "label": label,
                "config": contact_config,
                "mdText": convert_lbr_to_newline(question_text),
                "optout": {
                    "text": "I do not want to provide my information",
                    "allowed": True
                },
                "allowed": True,
                "created": current_time,
                "subtype": "",
                "updated": current_time,
                "condition":condition,
                **base_structure
            }
        

        if question_type == 'currency':
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            processed_question = {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "currency",
                "label": label,
                "config": {
                    "currency": "USD",  # Default currency
                    "ui": "input",
                    "randomize": False
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "updated": current_time,
                "skips": [],
                "optout": {"text": None, "allowed": False},
                "dynamic": False,
                "options": [],
                "condition": condition,
                "subtype": "",
                "confidence": 0.9,
                **base_structure  # Include any base structure elements
            }

            # Set currency if specified (only allow USD or CNY)
            if 'currency' in question_data:
                specified_currency = question_data['currency']
                processed_question["config"]["currency"] = specified_currency if specified_currency in ["USD", "CNY"] else "USD"

            # Handle data range if present
            if 'data_range' in question_data:
                processed_question["config"]["datarange"] = question_data['data_range']

            # Process currency logic if present
            if 'currency_logic' in question_data:
                process_currency_logic(question_data, processed_question, label)

            return processed_question
            



        


        if question_type == 'max_diff':
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            result = process_max_diff_question(question_data, label, current_time,raw_data)
            result["linked_options"] = variable_list_keyword if variable_list_keyword else None
            result["condition"]=condition
            if extra_text:
                result.update(base_structure)
            return result

        if question_type == 'unknown':
            return {
                "id": key_id or generate_nano_id(),
                "created": int(uuid.uuid1().time * 1e-3),
                "type": "unknown",
                "text": question_text,
                "mdText": convert_lbr_to_newline(question_text),
                "label": label,
                "options": [],
                "updated": current_time,
                "subtype": None,
                **base_structure
            }
        

        if question_type == 'multi-select-grid' or question_type=="multi_select_grid":
            print("asljndaskjdnaksj was called")
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            processed_question = {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "grid",
                "label": label,
                "config": {
                    "ui": None,
                    "randomize": question_data.get('randomize', False)
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "updated": current_time,
                "skips": [],
                "optout": {"text": None, "allowed": False},
                "dynamic": False,
                "linked_options": variable_list_keyword if variable_list_keyword else None,
                "options": {"vertical": {"options": []}, "horizontal": {"options": []}},
                "condition": condition,
                "subtype": "multi",
                "confidence": 0.9,
                **base_structure
            }
            
            grid_options, skips = process_grid_question(question_data, label)
            processed_question["options"] = grid_options
            processed_question["skips"].extend(skips)
            return processed_question
        

        if question_type == 'grid':
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            processed_question = {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "grid",
                "label": label,
                "config": {
                    "ui": None,
                    "randomize": question_data.get('randomize', False)
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "updated": current_time,
                "skips": [],
                "optout": {"text": None, "allowed": False},
                "dynamic": False,
                "linked_options": variable_list_keyword if variable_list_keyword else None,
                "options": {"vertical": {"options": []}, "horizontal": {"options": []}},
                "condition": condition,
                "subtype": "",
                "confidence": 0.9,
                **base_structure
            }
            
            grid_options, skips = process_grid_question(question_data, label)
            processed_question["options"] = grid_options
            processed_question["skips"].extend(skips)
            return processed_question

        if question_type == 'percentage_sum':
            processed_inputs = []
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            for i, option_dict in enumerate(options, start=1):
                for option_text, option_data in option_dict.items():
                    # We no longer need to process input_format since it's not used in the new structure
                    processed_input = {
                        "id": generate_nano_id(),
                        "label": str(i),  # Changed from f"{i:02d}" to match the desired format
                        "helper": option_text  # The option text becomes the helper text
                    }
                    processed_inputs.append(processed_input)
            
            return {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "percent-sum",
                "label": label,
                "config": {
                    "inputs": processed_inputs  # Put the processed inputs here instead of at root level
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "updated": current_time,
                "condition":condition,
                "subtype": ""  ,
                **base_structure
            }

        if question_data['type'] == 'nps':
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            processed_question = {
                "id": key_id or generate_nano_id(),
                "created": int(uuid.uuid1().time * 1e-3),
                "type": "nps",
                "text": question_text,
                "mdText": convert_lbr_to_newline(question_text),
                "label": label,
                "options": [],
                "updated": current_time,
                "subtype": None,
                "condition": condition,
                "skips": [],  # Add this for skip logic
                **base_structure
            }
            
            # Process NPS logic if present
            if 'nps_logic' in question_data:
                process_nps_logic(question_data, processed_question, label)
            
            return processed_question
        
        if question_data['type'] == 'message' or question_data["type"]=="transition":
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            return {
                "id": key_id or generate_nano_id(),
                "created": int(uuid.uuid1().time * 1e-3),
                "type": "transition",
                "text": question_text,
                "mdText": convert_lbr_to_newline(question_text),
                "label": label,
                "options": [],
                "updated": current_time,
                "subtype": None,
                "condition":condition,
                **base_structure
            }
        
        if question_data['type'] == 'terminate':
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            return {
                "id": key_id or generate_nano_id(),
                "created": int(uuid.uuid1().time * 1e-3),
                "type": "terminate",
                "text": question_text,
                "mdText": convert_lbr_to_newline(question_text),
                "label": label,
                "options": [],
                "updated": current_time,
                "subtype": None,
                "condition":condition,
                **base_structure
            }
        
        # Add this inside process_single_question function, with other if conditions
        if question_type == 'single_select' or question_type=="single-select":
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            processed_question = {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "select",
                "label": label,
                "config": {
                    "ui": "dropdown" if question_data.get('dropdown', False) else "radio",
                    "randomize": question_data.get('randomize', False)
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "updated": current_time,
                "skips": [],
                "optout": {"text": None, "allowed": False},
                "dynamic": False,
                "linked_options": variable_list_keyword if variable_list_keyword else None,
                "options": [],
                "condition": condition,
                "subtype": "single",
                "confidence": 0.9,
                **base_structure
            }

            if 'randomize_group' in question_data and isinstance(question_data['randomize_group'], list) and question_data['randomize_group']:
                processed_question["config"]["options"] = {
                    "groups": [
                        {
                            "id": generate_nano_id(),
                            "labels": [str(i) for i in question_data['randomize_group']],
                            "randomize": True
                        }
                    ]
                }

            # Process options if present
            if 'options' in question_data:
                for i, option_dict in enumerate(question_data['options'], start=1):
                    for option_text, option_logic in option_dict.items():
                        # option_label = f"{i:02d}"
                        option_label = str(i)
                        
                        # Extract backtick content and clean text
                        cleaned_text, backtick_value = extract_logic_from_backticks(option_text)

                        if use_ami:
                            cleaned_text=process_text(openai_model,cleaned_text,question_type=question_type)
                        if use_ami:
                            if option_logic == "other":
                                if "please specify" not in option_text.lower():
                                    option_logic = None
                        # Determine option type
                        option_type = "user"

                        option_type = "user"  # default type
                        if option_logic == "dontknow":
                            option_type = "dontknow"
                        elif option_logic == "notapplicable":
                            option_type = "notapplicable"
                        elif option_logic == "optout":
                            option_type = "optout"
                        elif option_logic == "nota":
                            option_type = "nota"
                        elif option_logic == "other":
                            option_type = "other"
                        elif "prefer not to answer" in cleaned_text.lower():
                            option_type = "optout"
                        elif "not applicable" in cleaned_text.lower():
                            option_type = "notapplicable"
                        
                        
                        
                        # Initialize skip dictionary if there's a backtick value
                        skip_dict = {backtick_value: None} if backtick_value else None
                        
                        # Create option
                        processed_option = {
                            "id": generate_nano_id(),
                            "text": cleaned_text,
                            "type": option_type,
                            "label": option_label,
                            "order": i - 1,
                            "mdText": convert_lbr_to_newline(cleaned_text),
                            "skip": skip_dict
                        }
                        
                        processed_question["options"].append(processed_option)
                        
                        # Process skip logic if present
                        if option_logic and option_logic != 'None':
                            if option_logic == 'THANK AND END':
                                skip = create_skip(f"{label} == `{option_label}`", "DISQUALIFY")
                                processed_question["skips"].append(skip)
                                # Update the skip ID in the option
                                if backtick_value:
                                    processed_option["skip"][backtick_value] = skip["id"]
                            elif option_logic.startswith('SKIP TO '):
                                skip_to = option_logic.replace('SKIP TO ', '').strip()
                                if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                                    skip_to = skip_to[1:]
                                skip = create_skip(f"{label} == `{option_label}`", "skip", skip_to)
                                processed_question["skips"].append(skip)
                                # Update the skip ID in the option
                                if backtick_value:
                                    processed_option["skip"][backtick_value] = skip["id"]

            return processed_question
        

        if question_type == 'year':
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            processed_question = {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "year",
                "label": label,
                "config": {
                    "ui": None,
                    "randomize": False
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "updated": current_time,
                "skips": [],
                "optout": {"text": None, "allowed": False},
                "dynamic": False,
                "options": [],
                "condition": condition,
                "subtype": "",
                "confidence": 0.9,
                **base_structure
            }

            # Handle data range if present
            if 'data_range' in question_data:
                processed_question["config"]["datarange"] = question_data['data_range']

            # Process year logic if present
            if 'year_logic' in question_data:
                process_year_logic(question_data, processed_question, label)

            return processed_question
        

        if question_type == 'percentage':
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            processed_question = {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "percentage",
                "label": label,
                "config": {
                    "ui": None,
                    "randomize": False
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "updated": current_time,
                "skips": [],
                "optout": {"text": None, "allowed": False},
                "dynamic": False,
                "options": [],
                "condition": condition,
                "subtype": "",
                "confidence": 0.9,
                **base_structure
            }

            # Handle data range if present
            if 'data_range' in question_data:
                processed_question["config"]["datarange"] = question_data['data_range']

            # Process percentage logic if present
            if 'percentage_logic' in question_data:
                process_percentage_logic(question_data, processed_question, label)

            return processed_question
        

        if question_type == 'multi_select' or question_type=="multi-select":
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            processed_question = {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "select",
                "label": label,
                "config": {
                    "ui": "dropdown" if question_data.get('dropdown', False) else "checkbox",
                    "randomize": question_data.get('randomize', False)
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "updated": current_time,
                "skips": [],
                "optout": {"text": None, "allowed": False},
                "dynamic": False,
                "linked_options": variable_list_keyword if variable_list_keyword else None,
                "options": [],
                "condition": condition,
                "subtype": "multi",
                "confidence": 0.9,
                **base_structure
            }

            if 'randomize_group' in question_data and isinstance(question_data['randomize_group'], list) and question_data['randomize_group']:
                processed_question["config"]["options"] = {
                    "groups": [
                        {
                            "id": generate_nano_id(),
                            "labels": [str(i) for i in question_data['randomize_group']],
                            "randomize": True
                        }
                    ]
                }

            # Process options if present
            if 'options' in question_data:
                for i, option_dict in enumerate(question_data['options'], start=1):
                    for option_text, option_logic in option_dict.items():
                        # option_label = f"{i:02d}"
                        option_label = str(i)

                        
                        # Extract backtick content and clean text
                        cleaned_text, backtick_value = extract_logic_from_backticks(option_text)

                        if use_ami:
                            cleaned_text=process_text(openai_model,cleaned_text,question_type=question_type)
                        
                        # Determine option type
                        if use_ami:
                            if option_logic == "other":
                                if "please specify" not in option_text.lower():
                                    option_logic = None
                        # Determine option type
                        option_type = "user"
                        
                        
                        option_type = "user"  # default type
                        if option_logic == "dontknow":
                            option_type = "dontknow"
                        elif option_logic == "notapplicable":
                            option_type = "notapplicable"
                        elif option_logic == "optout":
                            option_type = "optout"
                        elif option_logic == "nota":
                            option_type = "nota"
                        elif option_logic == "other":
                            option_type = "other"
                        elif "prefer not to answer" in cleaned_text.lower():
                            option_type = "optout"
                        elif "not applicable" in cleaned_text.lower():
                            option_type = "notapplicable"
                        elif "other" in cleaned_text.lower():
                            option_type = "other"
                        
                        # Initialize skip dictionary if there's a backtick value
                        skip_dict = {backtick_value: None} if backtick_value else None
                        
                        # Create option
                        processed_option = {
                            "id": generate_nano_id(),
                            "text": cleaned_text,
                            "type": option_type,
                            "label": option_label,
                            "order": i - 1,
                            "mdText": convert_lbr_to_newline(cleaned_text),
                            "skip": skip_dict
                        }
                        
                        processed_question["options"].append(processed_option)
                        
                        # Process skip logic if present
                        if option_logic and option_logic != 'None':
                            if option_logic == 'THANK AND END':
                                skip = create_skip(f"{label} == `{option_label}`", "DISQUALIFY")
                                processed_question["skips"].append(skip)
                                # Update the skip ID in the option
                                if backtick_value:
                                    processed_option["skip"][backtick_value] = skip["id"]
                            elif option_logic.startswith('SKIP TO '):
                                skip_to = option_logic.replace('SKIP TO ', '').strip()
                                if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                                    skip_to = skip_to[1:]
                                skip = create_skip(f"{label} == `{option_label}`", "skip", skip_to)
                                processed_question["skips"].append(skip)
                                # Update the skip ID in the option
                                if backtick_value:
                                    processed_option["skip"][backtick_value] = skip["id"]

            return processed_question

        if question_data['type'] == 'notes':
            return {
                "id": generate_nano_id(),
                "created": int(uuid.uuid1().time * 1e-3),
                "type": "notes",
                "text": question_text,
                "mdText": convert_lbr_to_newline(question_text),
                "label": label,
                "options": [],
                "updated": current_time,
                "subtype": None,
                **base_structure
            }

        mapped_type = map_type(question_type, has_options)

        processed_question = {
            "id": key_id or generate_nano_id(),
            "text": question_text,
            "type": mapped_type,
            "label": label,
            "config": {
                "ui": "dropdown" if question_data.get('dropdown', False) else map_config_ui(question_type),
                "randomize": question_data.get('randomize', False)
            },
            "mdText": convert_lbr_to_newline(question_text),
            "created": current_time,
            "updated": current_time,
            "skips": [],
            "optout": {"text": None, "allowed": False},
            "dynamic": False,
            "options": [],
            "condition": condition,
            "subtype": map_subtype(question_type),
            "confidence": 0.9,
            **base_structure
        }

        if question_type == 'number':
            ask_logic = question_data.get('ask_logic', '')
            condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic
            
            processed_question = {
                "id": key_id or generate_nano_id(),
                "text": question_text,
                "type": "number",
                "label": label,
                "config": {
                    "ui": None,
                    "randomize": False
                },
                "mdText": convert_lbr_to_newline(question_text),
                "created": current_time,
                "updated": current_time,
                "skips": [],
                "optout": {"text": None, "allowed": False},
                "dynamic": False,
                "options": [],
                "condition": condition,
                "subtype": "",
                "confidence": 0.9,
                **base_structure
            }

            # Handle data range if present
            if 'data_range' in question_data:
                processed_question["config"]["datarange"] = question_data['data_range']

            # Process number logic if present 
            if 'number_logic' in question_data:
                for action, condition in question_data['number_logic'].items():
                    if action == 'Terminating':
                        skip = create_skip(f"{condition}", "DISQUALIFY")
                        processed_question["skips"].append(skip)
                    elif action.startswith('SKIP TO '):
                        skip_to = action.replace('SKIP TO ', '').strip()
                        if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                            skip_to = skip_to[1:]
                        skip = create_skip(f"{condition}", "skip", skip_to)
                        processed_question["skips"].append(skip)

            return processed_question

        
        return processed_question

    except Exception as e:
        print(f"Warning: Error processing question: {str(e)}")
        return {
            "id": key_id or generate_nano_id(),
            "created": int(uuid.uuid1().time * 1e-3),
            "type": "unknown",
            "text": question_data.get('question', ''),
            "mdText": convert_lbr_to_newline(question_data.get('question', '')),
            "label": label,
            "options": [],
            "updated": current_time,
            "subtype": None,
            **base_structure
        }

def process_option_texts(processed_question):
    updated_question = processed_question.copy()

    if 'options' not in updated_question:
        
        return updated_question

    if updated_question.get('type') == 'grid':
        return updated_question
        
    
    for option in updated_question['options']:
        if option.get('skip'):
            for key, value in option['skip'].items():
                if value is None:
                    option['text'] = f"{option['text']} {key}"
                    option['mdText'] = convert_lbr_to_newline(option['text'])
    
    return updated_question