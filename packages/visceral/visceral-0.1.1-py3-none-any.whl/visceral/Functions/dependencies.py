import re

def extract_dependencies_from_text(text):
    """
    Extract dependencies from text enclosed in double curly braces.
    
    Args:
        text (str): The text to search for dependencies
        
    Returns:
        list: List of unique dependencies found in the text
    """
    if not isinstance(text, str):
        return []
    
    # Find all occurrences of text within double curly braces
    matches = re.findall(r'{([^{}]+)}', text)
    
    # Remove duplicates and return the list
    return list(set(matches))


def extract_skip_dependencies(question_data, label):
    """
    Extract dependencies from skip logic in question data.
    
    Args:
        question_data (dict): The question data object
        label (str): The current question label
        
    Returns:
        list: List of skip destinations (question labels)
    """
    skip_dependencies = []
    
    # Process single select option logic
    if 'options' in question_data and isinstance(question_data['options'], list):
        for option_dict in question_data['options']:
            for option_text, option_logic in option_dict.items():
                if option_logic and option_logic != 'None':
                    if option_logic.startswith('SKIP TO '):
                        skip_to = option_logic.replace('SKIP TO ', '').strip()
                        if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                            skip_to = skip_to[1:]
                        skip_dependencies.append(skip_to)

    return skip_dependencies

def extract_dependencies(question_data):
    """
    Extract all dependencies from a question data object.
    
    Args:
        question_data (dict): The question data object
        
    Returns:
        list: List of unique dependencies
    """
    dependencies = []
    label = question_data.get('questionLabel', '') or question_data.get('qstnLabel', '')
    
    # Check question text for dependencies
    if 'question' in question_data and isinstance(question_data['question'], str):
        dependencies.extend(extract_dependencies_from_text(question_data['question']))

    dependencies.extend(extract_skip_dependencies(question_data, label))

    ask_logic = question_data.get('ask_logic', '')
    condition = ask_logic.get('1', '') if isinstance(ask_logic, dict) else ask_logic

    if condition and isinstance(condition, str):
        # Extract question label before comparison operators
        condition_match = re.search(r'^([A-Za-z0-9]+)\s*(?:==|!=|>|<|>=|<=|IN|NOT IN)', condition)
        if condition_match:
            question_label = condition_match.group(1).strip()
            dependencies.append(question_label)

    # Add this to extract_dependencies function to handle piping dependencies
    if 'piping' in question_data and question_data['piping']:
        for prev_question_label, pipe_type in question_data['piping'].items():
            # Add the previous question label as a dependency
            dependencies.append(prev_question_label)


    # Add these checks to extract_skip_dependencies function
    # Process number logic
    if 'number_logic' in question_data:
        for action, condition in question_data['number_logic'].items():
            if action.startswith('SKIP TO '):
                skip_to = action.replace('SKIP TO ', '').strip()
                if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                    skip_to = skip_to[1:]
                dependencies.append(skip_to)

    # Process currency logic 
    if 'currency_logic' in question_data:
        for action, condition in question_data['currency_logic'].items():
            if action.startswith('SKIP TO '):
                skip_to = action.replace('SKIP TO ', '').strip()
                if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                    skip_to = skip_to[1:]
                dependencies.append(skip_to)

    if 'single_text_logic' in question_data:
        for action, condition in question_data['single_text_logic'].items():
            if action.startswith('SKIP TO '):
                skip_to = action.replace('SKIP TO ', '').strip()
                if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                    skip_to = skip_to[1:]
                dependencies.append(skip_to)

    # Process year logic
    if 'year_logic' in question_data:
        for action, condition in question_data['year_logic'].items():
            if action.startswith('SKIP TO '):
                skip_to = action.replace('SKIP TO ', '').strip()
                if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                    skip_to = skip_to[1:]
                dependencies.append(skip_to)

    # Process percentage logic
    if 'percentage_logic' in question_data:
        for action, condition in question_data['percentage_logic'].items():
            if action.startswith('SKIP TO '):
                skip_to = action.replace('SKIP TO ', '').strip()
                if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                    skip_to = skip_to[1:]
                dependencies.append(skip_to)
                
        
                
    return list(set(dependencies))  # Remove duplicates_
