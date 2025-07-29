
from CreateSection.Functions.helper import create_skip
def process_skip_logic(questions_dict):
    # First pass: Collect all logic
    logic_map = {}
    for qstn_label, question in questions_dict.items():
        if 'logic' in question and question['logic']:
            for ref_qstn, values in question['logic'].items():
                if ref_qstn not in logic_map:
                    logic_map[ref_qstn] = {}
                logic_map[ref_qstn][qstn_label] = values

    # Second pass: Apply skip logic to options
    for qstn_label, logic_info in logic_map.items():
        if qstn_label in questions_dict and 'options' in questions_dict[qstn_label]:
            options = questions_dict[qstn_label]['options']
            for skip_to, values in logic_info.items():
                for i, (option, current_value) in enumerate(options.items()):
                    if i + 1 in values:  # Assuming options are 1-indexed in the logic
                        options[option] = f"SKIP TO {skip_to}"

    return questions_dict





def process_number_logic(question, processed_question, label):
    """
    Process number logic for questions, supporting both TERMINATING and SKIP TO conditions.
    
    Args:
        question: The original question dictionary
        processed_question: The processed question dictionary being built
        label: The question label
    """
    if not question.get('number_logic'):
        return

    for action, condition in question['number_logic'].items():
        if action.lower() == 'terminating':
            skip = create_skip(f"{condition}", "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            # Handle Q prefix in skip_to target
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            
            # Create skip condition
            skip = create_skip(f"{condition}", "skip", skip_to)
            processed_question["skips"].append(skip)


def process_currency_logic(question, processed_question, label):
    """
    Process currency logic for questions, supporting both TERMINATING and SKIP TO conditions.
    
    Args:
        question: The original question dictionary
        processed_question: The processed question dictionary being built
        label: The question label
    """
    if not question.get('currency_logic'):
        return

    for action, condition in question['currency_logic'].items():
        if action.lower() == 'terminating':
            # Use create_skip_for_number for DISQUALIFY
            skip = create_skip_for_number(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            # Handle Q prefix in skip_to target
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            
            # Create skip condition - don't clean the condition anymore
            skip = create_skip(condition, "skip", skip_to)
            processed_question["skips"].append(skip)

def create_skip_for_number(condition, action_type):
    """
    Create a skip object specifically for number-based conditions.
    
    Args:
        condition: The condition string
        action_type: The action type (typically "DISQUALIFY" for number logic)
    
    Returns:
        dict: A skip object with the condition and action type directly
    """
    return {
        "condition": condition,
        "action": action_type
    }






def process_year_logic(question, processed_question, label):
    for action, condition in question['year_logic'].items():
        if action == 'Terminating':
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            # Check if condition already contains the label
            if not condition.startswith(label):
                condition = f"{label} {condition}"
            skip = create_skip(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            skip = create_skip(f"{condition.strip()}", "skip", skip_to)
            processed_question["skips"].append(skip)







def process_percentage_logic(question, processed_question, label):
    for action, condition in question['percentage_logic'].items():
        if action == 'Terminating':
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            # Check if condition already contains the label
            if not condition.startswith(label):
                condition = f"{label} {condition}"
            skip = create_skip(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            skip = create_skip(f"{condition.strip()}", "skip", skip_to)
            processed_question["skips"].append(skip)

def process_text_logic(question, processed_question, label):
    for action, condition in question['single_text_logic'].items():
        if action == 'Terminating':
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            # Check if condition already contains the label
            if not condition.startswith(label):
                condition = f"{label} {condition}"
            skip = create_skip(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            skip = create_skip(f"{condition.strip()}", "skip", skip_to)
            processed_question["skips"].append(skip)






def process_nps_logic(question, processed_question, label):
    for action, condition in question['nps_logic'].items():
        if action == 'Terminating':
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            # Check if condition already contains the label
            if not condition.startswith(label):
                condition = f"{label} {condition}"
            skip = create_skip(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            skip = create_skip(f"{condition.strip()}", "skip", skip_to)
            processed_question["skips"].append(skip)

