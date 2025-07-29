

import signal
from functools import wraps
import json
import re
from CreateSection.Functions.generate_uuid import *
from typing import Dict, Any, List
from copy import deepcopy


def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def timeout(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set the signal handler and a timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            except TimeoutError:
                print(f"Operation timed out after {seconds} seconds")
                # Return the original JSON without modification
                return args[1]  # Return the input json_data
            finally:
                # Disable the alarm
                signal.alarm(0)
            return result
        return wrapper
    return decorator






def ensure_serializable(obj):
    return json.loads(json.dumps(obj))


def escape_string(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')

def add_raw_data_to_json(json_string, question):

    data = json.loads(json_string)
    
    data['raw_data'] = escape_string(question)
    
    return json.dumps(data, ensure_ascii=False)





def clean_survey_data(data):
    def clean_skip_logic(s, should_clean):
        if should_clean and isinstance(s, str):
            # Remove 'Q' from skip logic statements
            return re.sub(r'\bQ(?=\S)', '', s)
        return s

    cleaned_data = []
    
    for item in data:
        if isinstance(item, list):
            # Handle the case where the item is a list containing a JSON string
            json_str = item[0]
            try:
                item_dict = json.loads(json_str)
            except json.JSONDecodeError:
                # If JSON decoding fails, try to fix the JSON string
                json_str = re.sub(r'(\w+):', r'"\1":', json_str)
                json_str = json_str.replace("'", '"')
                item_dict = json.loads(json_str)
        elif isinstance(item, dict):
            # If the item is already a dictionary, use it as is
            item_dict = item
        else:
            # Skip any items that are neither list nor dict
            continue

        # Check if questionLabel doesn't start with 'Q'
        should_clean_skip_logic = not item_dict.get('questionLabel', '').startswith('Q')

        # Clean options only if questionLabel doesn't start with 'Q'
        if 'options' in item_dict and isinstance(item_dict['options'], dict):
            item_dict['options'] = {k: clean_skip_logic(v, should_clean_skip_logic) 
                                    for k, v in item_dict['options'].items()}

        cleaned_data.append(item_dict)

    return cleaned_data





def currency_symbol_to_code(symbol):
    currency_mapping = {
        '$': 'USD',  # US Dollar
        '€': 'EUR',  # Euro
        '£': 'GBP',  # British Pound Sterling
        '¥': 'JPY',  # Japanese Yen
        '₹': 'INR',  # Indian Rupee
        '₽': 'RUB',  # Russian Ruble
        '₣': 'CHF',  # Swiss Franc
        '₺': 'TRY',  # Turkish Lira
        '₩': 'KRW',  # South Korean Won
        '₴': 'UAH',  # Ukrainian Hryvnia
        'A$': 'AUD',  # Australian Dollar
        'C$': 'CAD',  # Canadian Dollar
        'HK$': 'HKD',  # Hong Kong Dollar
        '₱': 'PHP',  # Philippine Peso
        '฿': 'THB',  # Thai Baht
        'R$': 'BRL',  # Brazilian Real
        '₪': 'ILS',  # Israeli New Shekel
        '₦': 'NGN',  # Nigerian Naira
        '₡': 'CRC',  # Costa Rican Colón
        '₫': 'VND',  # Vietnamese Dong
        '៛': 'KHR',  # Cambodian Riel
        '₸': 'KZT',  # Kazakhstani Tenge
        '₿': 'BTC',  # Bitcoin
        'Ξ': 'ETH',  # Ethereum
        '₼': 'AZN',  # Azerbaijani Manat
        '₾': 'GEL',  # Georgian Lari
        '₻': 'MGA',  # Malagasy Ariary
        '₽': 'RUB',  # Russian Ruble (duplicate, keeping for compatibility)
        '₺': 'TRY',  # Turkish Lira (duplicate, keeping for compatibility)
    }
    return currency_mapping.get(symbol, 'USD')


def extract_currency_symbol(text):
    # This regex will match any non-alphanumeric character at the start of the string
    match = re.match(r'^[^\w\s]+', text.strip())
    return match.group(0) if match else '$'





def format_label(label: str) -> str:
    try:
        # print("Label is ", label)
        # Remove the last period if it exists
        if label.endswith('.'):
            label = label[:-1]
        
        # Remove any remaining non-alphanumeric characters except periods
        # formatted_label = re.sub(r'[^a-zA-Z0-9.]', '', label)
        formatted_label = re.sub(r'[^a-zA-Z0-9._\-#]', '', label)
        
        if not formatted_label:
            raise ValueError(f"Invalid label: {label}")
        
        return formatted_label
    except Exception as e:
        print(f"Warning: Error formatting label '{label}': {str(e)}")
        return generate_nano_id_for_label()  # Use a generated ID as a fallback

def map_type(input_type, has_options=False):
    if input_type == 'multi_text' or input_type=="multi-text":
        return 'text'
    if has_options and input_type not in ['multi_text', 'number', 'currency', 'percentage', 'year','multi-text']:
        return 'select'
    type_mapping = {
        'single-select': 'select',
        'Single-select': 'select',
        'single_select': 'select',
        'Single_select': 'select',
        'multi_select': 'select',
        'multi-select': 'select',
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
    if input_type=='ranking':
        return ""
    if input_type == 'grid':
        return None
    if has_options:
        return 'multi' if input_type in ['multi_select', 'checkbox','multi-select'] else 'single'
    subtype_mapping = {
        'single_select': 'single',
        'single-select':'single',
        "Single-select":'single',
        'Single_select': 'single',
        'multi_select': 'multi',
        'multi-select':"multi",
        'number entry': 'single',
        'dropdown': 'single',
        'checkbox': 'multi',
        'multi_text': 'multi',
        'multi-text' : 'multi',
        'year': '',
        'percentage': '',
        'currency': '',
        'number': '',
        'ranking':''
    }
    return subtype_mapping.get(input_type, 'single')

def map_config_ui(input_type, has_options=False):

    if has_options:
        return 'checkbox' if input_type in ['multi_select', 'checkbox','multi-select'] else 'radio'
    ui_mapping = {
        'single_select': 'radio',
        'Single_select': 'radio',
        'single-select':'radio',
        'Single-select':'radio',
        'multi_select': 'checkbox',
        'multi-select':'checkbox',
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
        # Keep the 'Q' prefix if it's present
        skip["action"]["label"] = skip_to
    return skip

# def create_skip_for_number(condition, action_type, skip_to=None):
#     skip = {
#         "id": generate_nano_id(),
#         "condition": condition,
#         "action": {
#             "type": action_type
#         }
#     }
#     if skip_to:
#         # Keep the 'Q' prefix if it's present
#         skip["action"]["label"] = skip_to
#     return skip



def clean_option_text(text: str) -> str:
    """Remove the "[XX]" prefix from option text if it exists."""
    return re.sub(r'^\[\d+\]\s*', '', text)




def clean_unique_identifier_text(text):
    # Split by the unique identifier marker and take the first part
    return text.split('$$^^')[0].strip()






def clean_other_option_text(text):
    """
    Cleans 'other' option text by removing trailing numbers.
    Example: 'other 1' -> 'other', 'specify 2' -> 'specify'
    """
    # If the text ends with a number preceded by a space, remove it
    import re
    return re.sub(r'\s+\d+$', '', text)


def preprocess_input(input_data, raw_text):
    preprocessed_data = []
    for item, raw in zip(input_data, raw_text):
        preprocessed_item = {
            'question': item['question'],
            'questionLabel': item['questionLabel'],
            'type': item['type'],
            'options': item.get('options', {}),
            'columns': item.get('columns', {}),
            'rows': item.get('rows', {}),
            'raw_data': raw  # Store the original item as raw_data
        }
        # Handle 'single_text' type
        if item['type'] == 'single_text' or item['type']=='single-text':
            preprocessed_item['type'] = 'text'
        preprocessed_data.append(preprocessed_item)
    return preprocessed_data





def preprocess_survey_data(input_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Preprocess the survey data to fit the expected input format for transform_survey_data.
    """
    preprocessed_data = []
    identified_blocks = {}

    # for block_name, questions in input_data.items():
    #     identified_blocks[block_name] = [q['questionLabel'] for q in questions]
    #     preprocessed_data.extend(questions)

    # return preprocessed_data, identified_blocks
    for block_name, questions in input_data.items():
        # Get labels, skipping any questions that cause errors
        block_labels = []
        for q in questions:
            try:
                if isinstance(q, dict) and 'questionLabel' in q:
                    block_labels.append(q['questionLabel'])
            except:
                continue
        
        identified_blocks[block_name] = block_labels
        preprocessed_data.extend(questions)

    return preprocessed_data, identified_blocks





def clean_text(text: str) -> str:
    """
    Clean individual text strings by removing trailing underscores and numbers.
    Args:
        text (str): The input text to clean
    Returns:
        str: The cleaned text
    """
    if not isinstance(text, str):
        return text
    return re.sub(r'_{2,}\d*$', '', text)

def clean_single_option(option: dict) -> dict:
    """
    Clean a single option dictionary by processing its text and mdText fields.
    Args:
        option (dict): The option dictionary to clean
    Returns:
        dict: The cleaned option dictionary
    """
    option_copy = option.copy()
    if 'text' in option_copy:
        option_copy['text'] = clean_text(option_copy['text'])
    if 'mdText' in option_copy:
        option_copy['mdText'] = clean_text(option_copy['mdText'])
    return option_copy

def clean_survey_data(survey_data: dict) -> dict:
    """
    Clean the entire survey data structure by processing all questions and their options.
    Args:
        survey_data (dict): The complete survey data dictionary
    Returns:
        dict: The cleaned survey data dictionary
    """
    # Create a deep copy to avoid modifying the original data
    cleaned_data = deepcopy(survey_data)
    
    # Check if data is the new structure (object with blocks and annotated_data)
    if isinstance(cleaned_data.get('data'), dict):
        # Process each section in blocks
        for section in cleaned_data['data'].get('blocks', []):
            for question in section.get('questions', []):
                if 'options' in question and isinstance(question['options'], list):
                    question['options'] = [clean_single_option(option) for option in question['options']]
    else:
        # Handle the old structure where data is an array
        for section in cleaned_data.get('data', []):
            for question in section.get('questions', []):
                if 'options' in question and isinstance(question['options'], list):
                    question['options'] = [clean_single_option(option) for option in question['options']]
    
    return cleaned_data

