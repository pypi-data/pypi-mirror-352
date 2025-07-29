def extract_survey_questions(complete_survey_data):
    """
    Extracts a list of all questions directly from complete_survey_data.
    
    Args:
        complete_survey_data: The complete_survey_data object containing blocks and questions
    
    Returns:
        A list of formatted strings for each question (label + text)
    """
    questions_list = []
    
    try:
        # Print the type of the input
        print(f"complete_survey_data type: {type(complete_survey_data)}")
        
        # Try to access blocks directly
        blocks = None
        
        if hasattr(complete_survey_data, 'blocks'):
            blocks = complete_survey_data.blocks
            print(f"Found blocks as attribute with {len(blocks) if blocks else 0} blocks")
        elif isinstance(complete_survey_data, dict) and 'blocks' in complete_survey_data:
            blocks = complete_survey_data['blocks']
            print(f"Found blocks as dict key with {len(blocks)} blocks")
        
        # If blocks is still None, return empty list
        if blocks is None:
            print("No blocks found")
            return questions_list
        
        # Process each block
        for block in blocks:
            if not block:
                continue
                
            # Get questions
            questions = None
            
            if isinstance(block, dict) and 'questions' in block:
                questions = block['questions']
            elif hasattr(block, 'questions'):
                questions = block.questions
            
            if not questions:
                continue
                
            # Process each question
            for question in questions:
                # Get label and text
                label = None
                text = None
                
                if isinstance(question, dict):
                    label = question.get('label', '')
                    text = question.get('mdText', question.get('text', question.get('question', '')))
                else:
                    label = getattr(question, 'label', '')
                    if hasattr(question, 'mdText'):
                        text = question.mdText
                    elif hasattr(question, 'text'):
                        text = question.text
                    elif hasattr(question, 'question'):
                        text = question.question
                    else:
                        text = ''
                
                # Add to list if we have both label and text
                if label and text:
                    formatted_question = f"{label}. {text}"
                    questions_list.append(formatted_question)
        
        print(f"Extracted {len(questions_list)} questions")
        return questions_list
    except Exception as e:
        print(f"Error extracting questions: {e}")
        import traceback
        print(traceback.format_exc())
        return questions_list


# Usage:
# questions_list = extract_survey_questions(data_from_api.meta.complete_survey_data)