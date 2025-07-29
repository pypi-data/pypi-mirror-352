def sanitize_text(text):
    """Sanitize text by replacing curly quotes with standard quotes."""
    if isinstance(text, str):
        text = text.replace("'", "'").replace("'", "'").replace(""", '"').replace(""", '"')
    return text

def get_raw_data(complete_survey_data):
    """
    Extracts survey questions grouped by sections, using raw_data when available.
    
    Args:
        complete_survey_data: The complete_survey_data object containing blocks and questions
        
    Returns:
        A list of dictionaries with section_name, block_name, and a list of formatted questions
    """
    sections_list = []
    
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
        
        # If blocks is still None, check if it's a standalone question
        if blocks is None:
            # Check if the data itself is a question with raw_data
            if isinstance(complete_survey_data, dict) and 'raw_data' in complete_survey_data:
                print("Found a single question with raw_data")
                
                # Create a dummy section with this single question
                section_name = "Main Section"
                
                # Use the raw_data directly
                raw_data = sanitize_text(complete_survey_data.get('raw_data', ''))
                
                if raw_data:
                    sections_list.append({
                        "section_name": section_name,
                        "questions": [raw_data]
                    })
                
                return sections_list
            # Check if it's a question without raw_data
            elif isinstance(complete_survey_data, dict) and ('text' in complete_survey_data or 
                                                             'mdText' in complete_survey_data or 
                                                             'question' in complete_survey_data):
                print("Found a single question without raw_data")
                
                # Create a dummy section with this single question
                section_name = "Main Section"
                
                
                # Extract the question data manually
                label = sanitize_text(complete_survey_data.get('label', ''))
                text = sanitize_text(complete_survey_data.get('mdText', 
                                    complete_survey_data.get('text', 
                                    complete_survey_data.get('question', ''))))
                
                # Format the question
                if label and text:
                    formatted_question = f"{label}. {text}"
                    sections_list.append({
                        "section_name": section_name,
                    
                        "questions": [formatted_question]
                    })
                
                return sections_list
            else:
                print("No blocks found and not a valid question")
                return sections_list
        
        # Process each block
        for block in blocks:
            if not block:
                continue
                
            # Get section name and block name
            section_name = None
            block_name = None
            if isinstance(block, dict):
                section_name = block.get('name', 'Unnamed Section')
                block_name = block.get('name', 'Unnamed Block')
            elif hasattr(block, 'name'):
                section_name = getattr(block, 'name', 'Unnamed Section')
                block_name = getattr(block, 'name', 'Unnamed Block')
            else:
                section_name = 'Unnamed Section'
                block_name = 'Unnamed Block'
            
            # Get questions
            questions = None
            if isinstance(block, dict) and 'questions' in block:
                questions = block['questions']
            elif hasattr(block, 'questions'):
                questions = block.questions
            
            if not questions:
                continue
                
            # List to hold questions for this section
            section_questions = []
            
            # Process each question
            for question in questions:
                # Try to use raw_data if available
                if isinstance(question, dict) and 'raw_data' in question:
                    raw_data = sanitize_text(question.get('raw_data', ''))
                    if raw_data:
                        section_questions.append(raw_data)
                        continue
                
                # If no raw_data, extract manually as before
                label = None
                text = None
                
                if isinstance(question, dict):
                    label = sanitize_text(question.get('label', ''))
                    text = sanitize_text(question.get('mdText', question.get('text', question.get('question', ''))))
                else:
                    label = sanitize_text(getattr(question, 'label', ''))
                    if hasattr(question, 'mdText'):
                        text = sanitize_text(question.mdText)
                    elif hasattr(question, 'text'):
                        text = sanitize_text(question.text)
                    elif hasattr(question, 'question'):
                        text = sanitize_text(question.question)
                    else:
                        text = ''
                
                # Format the question
                if label and text:
                    formatted_question = f"{label}. {text}"
                    section_questions.append(formatted_question)
            
            # Add section to the list if it has questions
            if section_questions:
                sections_list.append({
                    "section_name": section_name,
                    "block_name": block_name,
                    "questions": section_questions
                })
        
        print(f"Extracted questions from {len(sections_list)} sections")
        return sections_list
    
    except Exception as e:
        print(f"Error extracting questions: {e}")
        import traceback
        print(traceback.format_exc())
        return sections_list