
import time
from Functions.nano_id import *
import re
from typing import Optional, Dict, List, Union, Any
from datetime import datetime
import requests
import json
from Question_Types.clean_json import clean_json_with_backticks

def format_label(label: str) -> str:
    try:
        # Remove the last period if it exists
        if label.endswith('.'):
            label = label[:-1]
        
        # Remove any remaining non-alphanumeric characters except periods
        formatted_label = re.sub(r'[^a-zA-Z0-9._\-#]', '', label)
        
        if not formatted_label:
            raise ValueError(f"Invalid label: {label}")
        
        return formatted_label
    except Exception as e:
        print(f"Warning: Error formatting label '{label}': {str(e)}")
        return generate_nano_id_for_label()  # Use a generated ID as a fallback

def map_type(input_type, has_options=False):
    if input_type == 'multi_text':
        return 'text'
    if has_options and input_type=="number":
        return "number"
    
    if has_options:
        return 'select'
    type_mapping = {
        'single_select': 'select',
        'Single_select': 'select',
        'multi_select': 'select',
        'number entry': 'text',
        'dropdown': 'select',
        'checkbox': 'select',
        'year': 'year',
        'percentage': 'percentage',
        'currency': 'currency',
        'number': 'number',
        'grid': 'grid'
    }
    return type_mapping.get(input_type, 'text')



def map_subtype(input_type, has_options=False):
    if input_type == 'grid':
        return None
    if has_options:
        return 'multi' if input_type in ['multi_select', 'checkbox'] else 'single'
    subtype_mapping = {
        'single_select': 'single',
        'Single_select': 'single',
        'multi_select': 'multi',
        'number entry': 'single',
        'dropdown': 'single',
        'checkbox': 'multi',
        'multi_text': 'multi',
        'year': '',
        'percentage': '',
        'currency': '',
        'number': ''
    }
    return subtype_mapping.get(input_type, 'single')



def map_config_ui(input_type, has_options=False):
    if has_options:
        return 'checkbox' if input_type in ['multi_select', 'checkbox'] else 'radio'
    ui_mapping = {
        'single_select': 'radio',
        'Single_select': 'radio',
        'multi_select': 'checkbox',
        'dropdown': 'dropdown',
        'checkbox': 'checkbox'
    }
    return ui_mapping.get(input_type)
    
    
def create_skip(condition, action_type, skip_to=None):
    skip = {
        "id": generate_nano_id(),
        "condition": condition,
        "action": {
            "type": action_type
        }
    }
    if skip_to:
        skip["action"]["label"] = skip_to
    return skip


def extract_currency_symbol(text):
    # This regex will match any non-alphanumeric character at the start of the string
    match = re.match(r'^[^\w\s]+', text.strip())
    return match.group(0) if match else '$'



def extract_logic_from_backticks(text):
    """Extract any content from backticks in text."""
    # Find content within backticks
    matches = re.findall(r'`([^`]+)`', text)
    if matches:
        # Return the last backticked content
        return re.sub(r'`[^`]+`', '', text).strip(), matches[-1].strip('()')
    return text, None






TAG_TEMPLATES = {
    'not_displayed': 'Please make sure to capture "{value}" in the not_displayed tag',
    'question': 'The question text "{value}" should be captured as a part of question_text',
    'label': 'Use "{value}" as the label',
    'options': 'Include "{value}" as an option too',
    'logic': {
        'skip': '"{value}" in the text is a skip logic',
        'disqualify': '"{value}" in the text is a disqualify/terminate logic',
        'randomize': '"{value}" in the text is a randomize logic',
        'range': '"{value}" in the text is a range logic',
        'piping': '"{value}" in the text is a piping logic',
        'responseRange': '"{value}" in the text is a responseRange logic'
    }
}


def extract_and_generate_prompts(text: str) -> Dict[str, Optional[str]]:
    """
    Extract tags and generate prompts, separating general and logic-specific prompts.
    Always returns a dictionary with 'general' and 'logic' keys, values may be None.
    
    Args:
        text (str): Input text containing tags
        
    Returns:
        Dict[str, Optional[str]]: Dictionary with 'general' and 'logic' prompts
    """
    # Initialize return dictionary with None values
    result_dict = {
        'general': None,
        'logic': None
    }
    
    if not text:
        return result_dict
        
    patterns = {
        'not_displayed': r'<not_displayed>(.*?)</not_displayed>',
        'question': r'<question>(.*?)</question>',
        'label': r'<label>(.*?)</label>',
        'options': r'<options>(.*?)</options>',
        'logic': r'<logic type="(.*?)">(.*?)</logic>'
    }
    
    results = {
        'not_displayed': [],
        'question': [],
        'options': [],
        'label': [],
        'logic': {}
    }
    
    tags_found = False
    
    # Extract values from tags
    for tag, pattern in patterns.items():
        if tag != 'logic':
            matches = list(re.finditer(pattern, text, re.DOTALL))
            if matches:
                tags_found = True
                results[tag].extend(match.group(1).strip() for match in matches)
        else:
            matches = list(re.finditer(pattern, text, re.DOTALL))
            for match in matches:
                tags_found = True
                logic_type = match.group(1)
                logic_value = match.group(2).strip()
                if logic_type not in results['logic']:
                    results['logic'][logic_type] = []
                results['logic'][logic_type].append(logic_value)
    
    if not tags_found:
        return result_dict
    
    # Generate general prompts (including logic)
    general_prompts = []
    
    # Handle standard tags
    for tag_type, values in results.items():
        if tag_type != 'logic':
            if values:
                template = TAG_TEMPLATES.get(tag_type)
                if template:
                    for value in values:
                        general_prompts.append(template.format(value=value))
    
    # Add logic to general prompts
    if results['logic']:
        for logic_type, values in results['logic'].items():
            if logic_type in TAG_TEMPLATES['logic']:
                template = TAG_TEMPLATES['logic'][logic_type]
                for value in values:
                    general_prompts.append(template.format(value=value))
    
    # Generate logic-only prompts
    logic_prompts = []
    if results['logic']:
        for logic_type, values in results['logic'].items():
            if logic_type in TAG_TEMPLATES['logic']:
                template = TAG_TEMPLATES['logic'][logic_type]
                for value in values:
                    logic_prompts.append(template.format(value=value))
    
    # Update result dictionary with generated prompts
    if general_prompts:
        result_dict['general'] = "\n".join(general_prompts)
    if logic_prompts:
        result_dict['logic'] = "\n".join(logic_prompts)
    
    return result_dict



def clean_question_text(question_text):
    """
    Clean question text by removing specific patterns based on conditions.
    """
    def process_backtick_content(match):
        try:
            # Extract content between backticks and strip whitespace
            content = match.group(1).strip()
            
            # Parse the JSON content directly
            json_data = json.loads(content)
            
            # Handle any key with True/False value
            for key, value in json_data.items():
                if isinstance(value, bool):
                    if value is True:
                        return ""
                    else:
                        return f" {key}"
            
            return f"`{content}`"  # Return original if no boolean values found
            
        except Exception as e:
            print(f"Debug - Error processing: {e}")  # For debugging
            return f"`{content}`"  # Return original if any error

    if not isinstance(question_text, str):
        return question_text
    
    # Pattern to match content between backticks
    pattern = r'`([^`]+)`'
    
    # Replace patterns based on conditions
    cleaned_text = re.sub(pattern, process_backtick_content, question_text)
    
    # Clean up any extra whitespace
    return ' '.join(cleaned_text.split())


def extract_logic_from_backticks(text, clean_text=True):
    """Extract any content from backticks in text.
    Args:
        text: The text to process
        clean_text: If True, removes backtick content from text, if False preserves original text
    """
    matches = re.findall(r'`([^`]+)`', text)
    if matches:
        return (re.sub(r'`[^`]+`', '', text).strip(), matches[-1]) if clean_text else (text, matches[-1])
    return text, None


def clean_random_dropdown(data):
    """
    Cleans only extra_text field by removing specific JSON-like configuration strings.
    
    Args:
        data: Dictionary with survey data
        
    Returns:
        Dictionary with cleaned extra_text
    """
    if not isinstance(data, dict):
        return data
        
    if 'extra_text' not in data:
        return data
        
    text = data['extra_text']
    if not isinstance(text, str):
        return data

    # Patterns to match config strings
    patterns = [
        r'\s*`{"Randomize":\s*(?:True|False)}`',
        r'\s*`{"Show as dropdown":\s*(?:True|False)}`',
        r'\s*`{"randomize":\s*(?:True|False)}`',
        r'From frontend: logic:randomize:'
    ]
    
    # Clean the text
    for pattern in patterns:
        text = re.sub(pattern, '', text)
    
    # Update only extra_text field
    data['extra_text'] = text.strip()
    return data


def clean_json_data(data):
    """
    Recursively clean JSON data by removing various frontend logic patterns
    
    Args:
        data: Any JSON-serializable data structure (dict, list, str, etc.)
    
    Returns:
        Cleaned data structure with the same type as input
    """
    def clean_string(s):
        # Define patterns to remove (case insensitive)
        patterns = [
            r'From frontend: logic:disqualify:',
            r'From frontend: logic:DISQUALIFY:',
            r'From frontend: logic:skip:',
            r'From frontend: logic:SKIP:'
        ]
        
        # Apply each pattern
        cleaned = s
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove any extra whitespace that might be left
        cleaned = ' '.join(cleaned.split())
        return cleaned

    if isinstance(data, dict):
        return {clean_json_data(k): clean_json_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_json_data(item) for item in data]
    elif isinstance(data, str):
        return clean_string(data)
    else:
        return data






# def convert_line_breaks(data):
#     """
#     Converts <lbr /> to newline characters (\n) only in the question text fields
#     of a survey question dictionary.
    
#     Args:
#         data (dict): Input dictionary containing survey question data
        
#     Returns:
#         dict: Dictionary with <lbr /> tags replaced with newline characters
#              only in question text fields
#     """
#     if not isinstance(data, dict):
#         return data
        
#     # Create a shallow copy of the input dictionary
#     converted_dict = data.copy()
    
#     # List of fields that contain question text
#     question_text_fields = ['text', 'mdText']
    
#     # Convert line breaks only in question text fields
#     for field in question_text_fields:
#         if field in converted_dict and isinstance(converted_dict[field], str):
#             converted_dict[field] = converted_dict[field].replace('<lbr />', '\n')
    
#     # Handle extra_text field if it exists
#     # if 'extra_text' in converted_dict and isinstance(converted_dict['extra_text'], str):
#     #     converted_dict['extra_text'] = converted_dict['extra_text'].replace('<lbr />', '\n')

    
#     # Handle options list - only convert text and mdText within options
#     if 'options' in converted_dict and isinstance(converted_dict['options'], list):
#         converted_options = []
#         for option in converted_dict['options']:
#             if isinstance(option, dict):
#                 converted_option = option.copy()
#                 for field in question_text_fields:
#                     if field in converted_option and isinstance(converted_option[field], str):
#                         converted_option[field] = converted_option[field].replace('<lbr />', '\n')
#                 converted_options.append(converted_option)
#             else:
#                 converted_options.append(option)
#         converted_dict['options'] = converted_options
    
#     return converted_dict



def clean_config_text(text):
    """
    Removes specific configuration strings from text.
    
    Args:
        text (str): Input text containing configuration strings
        
    Returns:
        str: Text with configuration strings removed
    """
    if not isinstance(text, str):
        return text

    # Remove the specific configuration strings
    patterns = [
        r'`{"Randomize": True}`',
        r'`{"Show as dropdown": True}`'

    ]
    
    for pattern in patterns:
        text = text.replace(pattern, '')
    
    # Clean up any extra whitespace
    return text.strip()

def clean_text(text):
    """
    Clean text by removing specific patterns and formatting it properly
    
    Args:
        text: Input text string with \n and various patterns
    
    Returns:
        Cleaned and properly formatted text
    """
    # First, convert \n to actual newlines if they're string literals
    text = text.replace('\\n', '\n')
    
    # Remove duplicate logic patterns
    text = re.sub(r'From frontend: logic: From frontend: logic:', 'From frontend: logic:', text, flags=re.IGNORECASE)
    
    # Remove various logic patterns
    patterns_to_remove = [
        r'From frontend: logic:disqualify:',
        r'From frontend: logic:DISQUALIFY:',
        r'From frontend: logic:skip:',
        r'From frontend: logic:SKIP:',
        r'From frontend: label:',  # Remove label prefix
        r'From frontend: options:',  # Remove options prefix
        r'From frontend: logic:',
        r'From frontend: logic:randomize:',
        r'From frontend: logic:dropdown:',
        r'From frontend: logic:ask-if:',
        r'ask-if:',
        # r'randomize:'
         # Remove logic prefix
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Clean up the numbered options format (remove leading zeros)
    text = re.sub(r'0(\d+)\.\s+', r'\1. ', text)
    
    # Clean up extra whitespace and empty lines
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Clean up extra whitespace
        line = ' '.join(line.split())
        if line.strip():  # Only keep non-empty lines
            cleaned_lines.append(line)
    
    # Join lines back together
    cleaned_text = '\n'.join(cleaned_lines)
    
    return cleaned_text




# def extract_question_text(input_json):
#     """
#     Extracts question text and preserves exact formatting with proper markdown list formatting.
    
#     Args:
#         input_json (dict): Input JSON containing nodes list.
    
#     Returns:
#         str: Properly formatted markdown text.
#     """
#     result = []
#     prev_was_question = False

#     for node in input_json['nodes']:
#         if node['type'] == 'question_text':
#             current_text = node['text'].strip()
            
#             # Ensure proper list formatting
#             if current_text.startswith(('1.', '2.')):
#                 # Ensure there's a space after the period for markdown list
#                 if not current_text[2:].startswith(' '):
#                     current_text = current_text[:2] + ' ' + current_text[2:]
                
#                 # Ensure there is a newline before numbered lists
#                 if result and not result[-1].endswith('\n\n'):
#                     result.append('\n')  # Ensure separation from previous text
            
#             # Add a newline before a new question text (if not a list item)
#             elif prev_was_question:
#                 result.append('\n')

#             result.append(current_text)
#             prev_was_question = True

#         elif node['type'] == 'linebreak':
#             result.append('\n')
#             prev_was_question = False

#     return ''.join(result)



def extract_question_text(input_json):
    """
    Extracts question text and preserves exact formatting with proper markdown list formatting.
    Only includes linebreaks between question_text nodes, ignoring extra linebreaks after last question.
    Args:
        input_json (dict): Input JSON containing nodes list.
    Returns:
        str: Properly formatted markdown text.
    """
    result = []
    prev_was_question = False
    last_question_index = -1
    
    # First find the index of the last question_text
    for i, node in enumerate(input_json['nodes']):
        if node['type'] == 'question_text':
            last_question_index = i
    
    # Now process nodes only up to the last question
    for i, node in enumerate(input_json['nodes']):
        if i > last_question_index:
            break
            
        if node['type'] == 'question_text':
            current_text = node['text'].strip()
            # Ensure proper list formatting
            if current_text.startswith(('1.', '2.')):
                # Ensure there's a space after the period for markdown list
                if not current_text[2:].startswith(' '):
                    current_text = current_text[:2] + ' ' + current_text[2:]
                # Ensure there is a newline before numbered lists
                if result and not result[-1].endswith('\n\n'):
                    result.append('\n')  # Ensure separation from previous text
            # Add a newline before a new question text (if not a list item)
            elif prev_was_question:
                result.append('\n')
            result.append(current_text)
            prev_was_question = True
        elif node['type'] == 'linebreak':
            result.append('\n')
            prev_was_question = False

    return ''.join(result)

def process_question_json(openai_model,question_data):
    """
    Processes the `question` field of a given dictionary to handle backtick-enclosed content.
    Specifically, it parses JSON strings, evaluates the first key-value pair,
    and modifies the `question` based on specific conditions.
    
    :param question_data: Dictionary containing the question field to be processed
    :return: Modified dictionary with processed `question` field
    """
    def transform_logic(match):
        """Processes the matched backtick-enclosed content."""
        content = match.group(1)
        print(f"Matched content: {content}")  # Debug
        
        try:
            # Replace Python booleans and `None` with JSON equivalents
            content = content.replace("True", "true").replace("False", "false").replace("None", "null")
            logic_dict = json.loads(content)
            print(f"Parsed JSON: {logic_dict}")  # Debug
            
            # Extract the first key-value pair
            key, value = next(iter(logic_dict.items()))
            print(f"Key: {key}, Value: {value}")  # Debug
            
            # If the value is True, remove the key from the output
            if value is True:
                return ""  # Remove the key from the output
            # If the value is False or None, keep the key in the output
            elif value is False or value is None:
                return key
            # For any other value, just remove the value and keep the key
            else:
                return key
        except Exception as e:
            # If there's an error parsing, return the original content with the key
            print(f"Error parsing JSON: {e}")  # Debug
            print("using AI to clean the json")
            cleaned_json = clean_json_with_backticks(openai_model, content)
            if cleaned_json:
                # Process the cleaned JSON
                key, value = next(iter(cleaned_json.items()))
                if value is True:
                    return ""
                elif value is False or value is None:
                    return key
                else:
                    return key
            return match.group(0)  # Fallba)  # Keep the original content (error case)

    processed_data = question_data.copy()
    
    if 'question' in processed_data:
        pattern = r'`(.*?)`'
        matches = re.findall(pattern, processed_data['question'])
        print(f"Matches found: {matches}")  # Debug
        
        # Process each match separately
        processed_text = processed_data['question']
        
        for match in matches:
            # Replace the entire matched content with the processed logic
            processed_text = processed_text.replace(f'`{match}`', transform_logic(re.match(pattern, f'`{match}`')))
        
        # Remove any redundant spaces resulting from replacements
        processed_data['question'] = ' '.join(processed_text.split())
    
    return processed_data



def clean_dictionary_values(question_dict, keys_to_clean):
    """
    Clean dot characters from values in a dictionary based on specified keys.
    
    Args:
        question_dict (dict): Dictionary containing question data
        keys_to_clean (list): List of keys whose values need to be cleaned
        
    Returns:
        dict: Updated dictionary with cleaned values
    """
    result = question_dict.copy()
    
    for key in keys_to_clean:
        if key in result and isinstance(result[key], dict):
            cleaned_dict = {}
            for sub_key, value in result[key].items():
                if isinstance(value, str):
                    # Remove dots from the value
                    cleaned_value = value.replace('.', '')
                    cleaned_dict[sub_key] = cleaned_value
                else:
                    # Keep non-string values unchanged
                    cleaned_dict[sub_key] = value
            
            result[key] = cleaned_dict
            
    return result


def clean_extra_text(question_data):
    if 'extra_text' in question_data and question_data['extra_text']:
        # Updated patterns to match any question label (not just Q)
        patterns = [
            r'Disqualify IF \w+\d* == `\d+`\s*',  # Matches "Disqualify IF" with any label
            r'Skip to \w+\d* IF \w+\d* == `\d+`\s*',
            r'randomize:.*',  # Simply matches 'randomize:' and EVERYTHING after it
            r'\(Randomize\)\s*',
            r'Randomize\s*',
            r'\(dropdown\)\s*',
            r'dropdown\s*',
            r'(?i)randomize\s*:\s*.*',  # Case-insensitive randomize and everything after colon
            r'(?i)dropdown\s*:\s*.*', 
            r'\w+\s*:\s*.*',  # Matches word, optional space, colon, and everything after it
            r'^\s*:\s*.*',  
            r'Show as\s*',  # Fixed pattern - removed unnecessary grouping and space
            r'\(Show as\)\s*',  # Added pattern for parentheses version,
            r'`[^`]*`',     
            r'(?i)Horizontal options\.\s*',       # Matches "Horizontal options."
            r'(?i)Vertical options\.\s*'  
        ]
        
        cleaned_text = question_data['extra_text']
        # Remove each pattern
        for pattern in patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text)
        
        # Clean up extra whitespace and set to None if empty
        cleaned_text = cleaned_text.strip()
        question_data['extra_text'] = cleaned_text if cleaned_text else None
    
    return question_data


def log_time(message):
    """Helper function to log timestamps with millisecond precision"""
    current_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"[{current_time}] {message}")




def remove_tags(text: str) -> str:
    """
    Remove all XML-style tags while preserving their content and spacing.
    
    Args:
        text (str): Input text containing tags
        
    Returns:
        str: Text with tags removed but content preserved
    
    Example:
        Input: "Hello <not_displayed>world</not_displayed>!"
        Output: "Hello world!"
    """
    # List of all possible tags to remove
    patterns = [
        (r'<not_displayed>', ''),
        (r'</not_displayed>', ''),
        (r'<question>', ''),
        (r'</question>', ''),
        (r'<label>', ''),
        (r'</label>', ''),
        (r'<options>', ''),
        (r'</options>', ''),
        # For logic tags with type attribute
        (r'<logic type="[^"]*">', ''),
        (r'</logic>', '')
    ]
    result = text
    user_changes = False
    
    for pattern, replacement in patterns:
        new_text = re.sub(pattern, replacement, result)
        if new_text != result:
            user_changes = True
        result = new_text
    
    return result, user_changes
    


def filter_nodes(question_data):
    # Check if the input has the required structure
    if not isinstance(question_data, dict) or 'nodes' not in question_data:
        return question_data
    
    # Filter out nodes with type 'not_displayed'
    filtered_nodes = [
        node for node in question_data['nodes'] 
        if node.get('type') != 'not_displayed'
    ]
    
    # Create a new dictionary with the filtered nodes
    filtered_data = question_data.copy()
    filtered_data['nodes'] = filtered_nodes
    
    return filtered_data




def process_survey_learning(user_id):
    # Construct the URL with the user_id
    url = f"https://visceralos.com/learning/survey/{user_id}"

    # Make the GET request
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        return None, False, f"Error: HTTP {response.status_code}"

    data = response.json()

    # Extract the survey_learning data
    survey_learning = data.get('survey_learning', {})
    taggings = survey_learning.get('taggings', [])

    # Create the result dictionary
    result = {}
    
    # Process taggings
    for tagging in taggings:
        tag = tagging.get('tag')
        text = tagging.get('text')
        
        if tag in result:
            if isinstance(result[tag], list):
                result[tag].append(text)
            else:
                result[tag] = [result[tag], text]
        else:
            result[tag] = text

    # Check if there's data
    has_data = len(taggings) > 0

    # print(result, has_data)

    return result, has_data


def clean_option_text(text: str) -> str:
    """Remove the "[XX]" prefix from option text if it exists."""
    return re.sub(r'^\[\d+\]\s*', '', text)


def check_keywords_and_create_prompt(input_text, keymap_names):
    # Convert input text and keywords to lowercase for matching
    input_text_lower = input_text.lower()
    
    # Check for matches
    matched_keywords = []
    original_formatted_keywords = []  # To store the original formatting
    
    for keyword in keymap_names:
        keyword_lower = keyword.lower()
        if keyword_lower in input_text_lower:
            # Find the position of the keyword in lowercase text
            start_pos = input_text_lower.find(keyword_lower)
            # Extract the original formatted version from input text
            original_format = input_text[start_pos:start_pos + len(keyword)]
            original_formatted_keywords.append(original_format)
            variable_name=keyword
    
    # Create prompt if exactly one match is found
    if len(original_formatted_keywords) == 1:
        return original_formatted_keywords[0], variable_name
    else:
        return None, None
    