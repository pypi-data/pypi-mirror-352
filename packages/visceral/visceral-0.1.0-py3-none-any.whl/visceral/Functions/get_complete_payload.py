def sanitize_text(text):
    """Sanitize text by replacing curly quotes with standard quotes."""
    if isinstance(text, str):
        text = text.replace("'", "'").replace("'", "'").replace(""", '"').replace(""", '"')
    return text

def generate_complete_questions_payload(complete_survey_data):
    """
    Extracts survey questions grouped by sections, including options and rows/columns if present,
    and displays the block name for each section.

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
        
        # If blocks is still None, return empty list
        if blocks is None:
            print("No blocks found")
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
                # Get label and text
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
                
                # Get options if they exist
                options_text = []
                if isinstance(question, dict) and 'options' in question:
                    options = question.get('options', [])
                    for opt in options:
                        if isinstance(opt, str):
                            opt_text = sanitize_text(opt)
                        else:
                            opt_text = sanitize_text(opt.get('mdText', opt.get('text', '')) if isinstance(opt, dict) else (opt.mdText if hasattr(opt, 'mdText') else opt.text))
                        if opt_text:
                            options_text.append(opt_text)
                elif hasattr(question, 'options'):
                    options = getattr(question, 'options', [])
                    for opt in options:
                        if isinstance(opt, str):
                            opt_text = sanitize_text(opt)
                        else:
                            opt_text = sanitize_text(opt.mdText if hasattr(opt, 'mdText') else opt.text)
                        if opt_text:
                            options_text.append(opt_text)
                
                # Get rows or columns if they exist (for matrix-style questions)
                rows_text = []
                columns_text = []
                if isinstance(question, dict):
                    rows = question.get('rows', [])
                    columns = question.get('columns', [])
                    rows_text = [sanitize_text(row.get('mdText', row.get('text', ''))) for row in rows if sanitize_text(row.get('mdText', row.get('text', '')))]
                    columns_text = [sanitize_text(col.get('mdText', col.get('text', ''))) for col in columns if sanitize_text(col.get('mdText', col.get('text', '')))]
                elif hasattr(question, 'rows') or hasattr(question, 'columns'):
                    rows = getattr(question, 'rows', [])
                    columns = getattr(question, 'columns', [])
                    rows_text = [sanitize_text(row.mdText if hasattr(row, 'mdText') else row.text) for row in rows if (hasattr(row, 'mdText') and row.mdText) or (hasattr(row, 'text') and row.text)]
                    columns_text = [sanitize_text(col.mdText if hasattr(col, 'mdText') else col.text) for col in columns if (hasattr(col, 'mdText') and col.mdText) or (hasattr(col, 'text') and col.text)]
                
                # Format the question
                if label and text:
                    formatted_question = f"{label}. {text}"
                    if options_text:
                        formatted_question += f" Options: {', '.join(options_text)}"
                    if rows_text:
                        formatted_question += f" Rows: {', '.join(rows_text)}"
                    if columns_text:
                        formatted_question += f" Columns: {', '.join(columns_text)}"
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

# Test the function
# if __name__ == "__main__":
    # test_payload = {
    #     "blocks": [
    #         {
    #             "id": "block_1",
    #             "name": "Introduction Block",
    #             "questions": [
    #                 {
    #                     "id": "q1",
    #                     "label": "INTRO",
    #                     "mdText": "Welcome to our survey. Please answer honestly. What device are you using?",
    #                     "type": "transition",
    #                     "options": []
    #                 },
    #                 {
    #                     "id": "q2",
    #                     "label": "Q1",
    #                     "mdText": "How satisfied are you with our service?",
    #                     "type": "select",
    #                     "options": [
    #                         {"mdText": "Very Satisfied"},
    #                         {"mdText": "Satisfied"},
    #                         {"mdText": "Neutral"},
    #                         {"mdText": "Dissatisfied"}
    #                     ]
    #                 },
    #                 {
    #                     "id": "q3",
    #                     "label": "Q2",
    #                     "mdText": "Rate the following aspects:",
    #                     "type": "matrix",
    #                     "rows": [
    #                         {"mdText": "Quality"},
    #                         {"mdText": "Speed"}
    #                     ],
    #                     "columns": [
    #                         {"mdText": "Excellent"},
    #                         {"mdText": "Good"},
    #                         {"mdText": "Poor"}
    #                     ]
    #                 }
    #             ]
    #         },
    #         {
    #             "id": "block_2",
    #             "name": "Demographics Block",
    #             "questions": [
    #                 {
    #                     "id": "q4",
    #                     "label": "Q3",
    #                     "mdText": "What is your age group?",
    #                     "type": "select",
    #                     "options": [
    #                         {"mdText": "18-24"},
    #                         {"mdText": "25-34"},
    #                         {"mdText": "35-44"}
    #                     ]
    #                 }
    #             ]
    #         }
    #     ]
    # }
    
    # # Run the function
    # result = generate_complete_questions(test_payload)
    
    # # Print formatted output for clarity
    # for section in result:
    #     print(f"\nSection: {section['block_name']}")
    #     for question in section['questions']:
    #         print(f"- {question}")