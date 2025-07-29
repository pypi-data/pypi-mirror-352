def generate_next_question_label(json_payload):
    """
    Generates a new sequential question label (e.g., Q5) based on existing labels.
    Ensures the generated label is unique.
    
    Args:
        json_payload: The JSON payload containing blocks and questions
        
    Returns:
        str: A new unique sequential question label
    """
    # Create a set to track all existing labels
    existing_labels = set()
    highest_q_number = 0
    
    # Check if we have blocks with questions
    if hasattr(json_payload, "blocks"):
        blocks = json_payload.blocks
    elif isinstance(json_payload, dict) and "blocks" in json_payload:
        blocks = json_payload["blocks"]
    else:
        return "Q1"  # Default if no blocks found
    
    # Collect all existing labels and find highest Q-number
    for block in blocks:
        if "questions" in block:
            for question in block["questions"]:
                if "label" in question and question["label"]:
                    label = question["label"]
                    existing_labels.add(label)
                    
                    # Check for Q-format labels
                    if label.startswith("Q") and label[1:].isdigit():
                        q_number = int(label[1:])
                        highest_q_number = max(highest_q_number, q_number)
    
    # Generate a new sequential label
    next_q_number = highest_q_number + 1
    new_label = f"Q{next_q_number}"
    
    # Make sure the new label is unique - increment until we find an unused label
    while new_label in existing_labels:
        next_q_number += 1
        new_label = f"Q{next_q_number}"
    
    return new_label