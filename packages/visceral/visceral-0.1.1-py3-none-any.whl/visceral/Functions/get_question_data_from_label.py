# def sanitize_text(text):
#     """Sanitize text by replacing curly quotes with standard quotes."""
#     if isinstance(text, str):
#         text = text.replace("'", "'").replace("'", "'").replace(""", '"').replace(""", '"')
#     return text

# def find_question_by_label(complete_survey_data, target_label, format_as_string=True):
#     """
#     Finds a question by its label in the survey data structure.
    
#     Args:
#         complete_survey_data: The complete_survey_data object containing blocks and questions
#         target_label: The label of the question to find (e.g., "Q2")
#         format_as_string: If True, returns a formatted string instead of the raw question object
        
#     Returns:
#         If format_as_string is True: A formatted string with question details
#         If format_as_string is False: The complete question data as a dictionary
#         Returns None if question is not found
#     """
#     try:
#         # Try to access blocks
#         blocks = None
        
#         if hasattr(complete_survey_data, 'blocks'):
#             blocks = complete_survey_data.blocks
#         elif isinstance(complete_survey_data, dict) and 'blocks' in complete_survey_data:
#             blocks = complete_survey_data['blocks']
        
#         # If blocks is still None, return None
#         if blocks is None:
#             print("No blocks found in the survey data")
#             return None
        
#         # Search through all blocks and questions
#         for block in blocks:
#             if not block:
#                 continue
                
#             # Get questions
#             questions = None
#             if isinstance(block, dict) and 'questions' in block:
#                 questions = block['questions']
#             elif hasattr(block, 'questions'):
#                 questions = block.questions
            
#             if not questions:
#                 continue
                
#             # Look for the question with the target label
#             for question in questions:
#                 label = None
                
#                 if isinstance(question, dict):
#                     label = question.get('label', '')
#                 else:
#                     label = getattr(question, 'label', '')
                
#                 # If we found a matching label
#                 if label == target_label:
#                     if not format_as_string:
#                         return question
                    
#                     # Format the question as a string
#                     question_text = ""
                    
#                     # Get the question text
#                     q_text = ""
#                     if isinstance(question, dict):
#                         q_text = sanitize_text(question.get('mdText', question.get('text', question.get('question', ''))))
#                     else:
#                         if hasattr(question, 'mdText'):
#                             q_text = sanitize_text(question.mdText)
#                         elif hasattr(question, 'text'):
#                             q_text = sanitize_text(question.text)
#                         elif hasattr(question, 'question'):
#                             q_text = sanitize_text(question.question)
                    
#                     # Add the label in front of the question text
#                     question_text = f"{label}. {q_text}"
                    
#                     # Get options
#                     options = []
#                     if isinstance(question, dict) and 'options' in question:
#                         options = question.get('options', [])
#                         if options:
#                             for opt in options:
#                                 opt_text = sanitize_text(opt.get('mdText', opt.get('text', '')))
#                                 if opt_text:
#                                     question_text += f"\n{opt_text}"
#                     elif hasattr(question, 'options'):
#                         options = getattr(question, 'options', [])
#                         if options:
#                             for opt in options:
#                                 opt_text = sanitize_text(getattr(opt, 'mdText', getattr(opt, 'text', '')))
#                                 if opt_text:
#                                     question_text += f"\n{opt_text}"
                    
#                     # Get rows if any
#                     rows = []
#                     if isinstance(question, dict) and 'rows' in question:
#                         rows = question.get('rows', [])
#                         if rows:
#                             for row in rows:
#                                 row_text = sanitize_text(row.get('mdText', row.get('text', '')))
#                                 if row_text:
#                                     question_text += f"\n{row_text}"
#                     elif hasattr(question, 'rows'):
#                         rows = getattr(question, 'rows', [])
#                         if rows:
#                             for row in rows:
#                                 row_text = sanitize_text(getattr(row, 'mdText', getattr(row, 'text', '')))
#                                 if row_text:
#                                     question_text += f"\n{row_text}"
                    
#                     # Get columns if any
#                     columns = []
#                     if isinstance(question, dict) and 'columns' in question:
#                         columns = question.get('columns', [])
#                         if columns:
#                             for col in columns:
#                                 col_text = sanitize_text(col.get('mdText', col.get('text', '')))
#                                 if col_text:
#                                     question_text += f"\n{col_text}"
#                     elif hasattr(question, 'columns'):
#                         columns = getattr(question, 'columns', [])
#                         if columns:
#                             for col in columns:
#                                 col_text = sanitize_text(getattr(col, 'mdText', getattr(col, 'text', '')))
#                                 if col_text:
#                                     question_text += f"\n{col_text}"
                    
#                     return question_text
        
#         # If we didn't find the question, return None
#         print(f"No question found with label: {target_label}")
#         return None
    
#     except Exception as e:
#         print(f"Error finding question: {e}")
#         import traceback
#         print(traceback.format_exc())
#         return None

# def generate_complete_questions(complete_survey_data):
#     """
#     Extracts survey questions grouped by sections, including options and rows/columns if present.

#     Args:
#         complete_survey_data: The complete_survey_data object containing blocks and questions

#     Returns:
#         A list of dictionaries with section_name and a list of formatted questions
#     """
#     sections_list = []
    
#     try:
#         # Print the type of the input
#         print(f"complete_survey_data type: {type(complete_survey_data)}")
        
#         # Try to access blocks directly
#         blocks = None
        
#         if hasattr(complete_survey_data, 'blocks'):
#             blocks = complete_survey_data.blocks
#             print(f"Found blocks as attribute with {len(blocks) if blocks else 0} blocks")
#         elif isinstance(complete_survey_data, dict) and 'blocks' in complete_survey_data:
#             blocks = complete_survey_data['blocks']
#             print(f"Found blocks as dict key with {len(blocks)} blocks")
        
#         # If blocks is still None, return empty list
#         if blocks is None:
#             print("No blocks found")
#             return sections_list
        
#         # Process each block
#         for block in blocks:
#             if not block:
#                 continue
                
#             # Get section name
#             section_name = None
#             if isinstance(block, dict):
#                 section_name = block.get('name', 'Unnamed Section')
#             elif hasattr(block, 'name'):
#                 section_name = getattr(block, 'name', 'Unnamed Section')
#             else:
#                 section_name = 'Unnamed Section'
            
#             # Get questions
#             questions = None
#             if isinstance(block, dict) and 'questions' in block:
#                 questions = block['questions']
#             elif hasattr(block, 'questions'):
#                 questions = block.questions
            
#             if not questions:
#                 continue
                
#             # List to hold questions for this section
#             section_questions = []
            
#             # Process each question
#             for question in questions:
#                 # Get label and text
#                 label = None
#                 text = None
                
#                 if isinstance(question, dict):
#                     label = sanitize_text(question.get('label', ''))
#                     text = sanitize_text(question.get('mdText', question.get('text', question.get('question', ''))))
#                 else:
#                     label = sanitize_text(getattr(question, 'label', ''))
#                     if hasattr(question, 'mdText'):
#                         text = sanitize_text(question.mdText)
#                     elif hasattr(question, 'text'):
#                         text = sanitize_text(question.text)
#                     elif hasattr(question, 'question'):
#                         text = sanitize_text(question.question)
#                     else:
#                         text = ''
                
#                 # Get options if they exist
#                 options_text = []
#                 if isinstance(question, dict) and 'options' in question:
#                     options = question.get('options', [])
#                     options_text = [sanitize_text(opt.get('mdText', opt.get('text', ''))) for opt in options if sanitize_text(opt.get('mdText', opt.get('text', '')))]
#                 elif hasattr(question, 'options'):
#                     options = getattr(question, 'options', [])
#                     options_text = [sanitize_text(opt.mdText if hasattr(opt, 'mdText') else opt.text) for opt in options if (hasattr(opt, 'mdText') and opt.mdText) or (hasattr(opt, 'text') and opt.text)]
                
#                 # Get rows or columns if they exist (for matrix-style questions)
#                 rows_text = []
#                 columns_text = []
#                 if isinstance(question, dict):
#                     rows = question.get('rows', [])
#                     columns = question.get('columns', [])
#                     rows_text = [sanitize_text(row.get('mdText', row.get('text', ''))) for row in rows if sanitize_text(row.get('mdText', row.get('text', '')))]
#                     columns_text = [sanitize_text(col.get('mdText', col.get('text', ''))) for col in columns if sanitize_text(col.get('mdText', col.get('text', '')))]
#                 elif hasattr(question, 'rows') or hasattr(question, 'columns'):
#                     rows = getattr(question, 'rows', [])
#                     columns = getattr(question, 'columns', [])
#                     rows_text = [sanitize_text(row.mdText if hasattr(row, 'mdText') else row.text) for row in rows if (hasattr(row, 'mdText') and row.mdText) or (hasattr(row, 'text') and row.text)]
#                     columns_text = [sanitize_text(col.mdText if hasattr(col, 'mdText') else col.text) for col in columns if (hasattr(col, 'mdText') and col.mdText) or (hasattr(col, 'text') and col.text)]
                
#                 # Format the question
#                 if label and text:
#                     formatted_question = f"{label}. {text}"
#                     if options_text:
#                         formatted_question += f" Options: {', '.join(options_text)}"
#                     if rows_text:
#                         formatted_question += f" Rows: {', '.join(rows_text)}"
#                     if columns_text:
#                         formatted_question += f" Columns: {', '.join(columns_text)}"
#                     section_questions.append(formatted_question)
            
#             # Add section to the list if it has questions
#             if section_questions:
#                 sections_list.append({
#                     "section_name": section_name,
#                     "questions": section_questions
#                 })
        
#         print(f"Extracted questions from {len(sections_list)} sections")
#         return sections_list
    
#     except Exception as e:
#         print(f"Error extracting questions: {e}")
#         import traceback
#         print(traceback.format_exc())
#         return sections_list

# def generate_complete_questions(complete_survey_data):
#     """
#     Extracts survey questions grouped by sections, including options and rows/columns if present.

#     Args:
#         complete_survey_data: The complete_survey_data object containing blocks and questions

#     Returns:
#         A list of dictionaries with section_name and a list of formatted questions
#     """
#     sections_list = []
    
#     try:
#         # Print the type of the input
#         print(f"complete_survey_data type: {type(complete_survey_data)}")
        
#         # Try to access blocks directly
#         blocks = None
        
#         if hasattr(complete_survey_data, 'blocks'):
#             blocks = complete_survey_data.blocks
#             print(f"Found blocks as attribute with {len(blocks) if blocks else 0} blocks")
#         elif isinstance(complete_survey_data, dict) and 'blocks' in complete_survey_data:
#             blocks = complete_survey_data['blocks']
#             print(f"Found blocks as dict key with {len(blocks)} blocks")
        
#         # If blocks is still None, return empty list
#         if blocks is None:
#             print("No blocks found")
#             return sections_list
        
#         # Process each block
#         for block in blocks:
#             if not block:
#                 continue
                
#             # Get section name
#             section_name = None
#             if isinstance(block, dict):
#                 section_name = block.get('name', 'Unnamed Section')
#             elif hasattr(block, 'name'):
#                 section_name = getattr(block, 'name', 'Unnamed Section')
#             else:
#                 section_name = 'Unnamed Section'
            
#             # Get questions
#             questions = None
#             if isinstance(block, dict) and 'questions' in block:
#                 questions = block['questions']
#             elif hasattr(block, 'questions'):
#                 questions = block.questions
            
#             if not questions:
#                 continue
                
#             # List to hold questions for this section
#             section_questions = []
            
#             # Process each question
#             for question in questions:
#                 # Get label and text
#                 label = None
#                 text = None
                
#                 if isinstance(question, dict):
#                     label = sanitize_text(question.get('label', ''))
#                     text = sanitize_text(question.get('mdText', question.get('text', question.get('question', ''))))
#                 else:
#                     label = sanitize_text(getattr(question, 'label', ''))
#                     if hasattr(question, 'mdText'):
#                         text = sanitize_text(question.mdText)
#                     elif hasattr(question, 'text'):
#                         text = sanitize_text(question.text)
#                     elif hasattr(question, 'question'):
#                         text = sanitize_text(question.question)
#                     else:
#                         text = ''
                
#                 # Get options if they exist
#                 options_text = []
#                 if isinstance(question, dict) and 'options' in question:
#                     options = question.get('options', [])
#                     options_text = [sanitize_text(opt.get('mdText', opt.get('text', ''))) for opt in options if sanitize_text(opt.get('mdText', opt.get('text', '')))]
#                 elif hasattr(question, 'options'):
#                     options = getattr(question, 'options', [])
#                     options_text = [sanitize_text(opt.mdText if hasattr(opt, 'mdText') else opt.text) for opt in options if (hasattr(opt, 'mdText') and opt.mdText) or (hasattr(opt, 'text') and opt.text)]
                
#                 # Get rows or columns if they exist (for matrix-style questions)
#                 rows_text = []
#                 columns_text = []
#                 if isinstance(question, dict):
#                     rows = question.get('rows', [])
#                     columns = question.get('columns', [])
#                     rows_text = [sanitize_text(row.get('mdText', row.get('text', ''))) for row in rows if sanitize_text(row.get('mdText', row.get('text', '')))]
#                     columns_text = [sanitize_text(col.get('mdText', col.get('text', ''))) for col in columns if sanitize_text(col.get('mdText', col.get('text', '')))]
#                 elif hasattr(question, 'rows') or hasattr(question, 'columns'):
#                     rows = getattr(question, 'rows', [])
#                     columns = getattr(question, 'columns', [])
#                     rows_text = [sanitize_text(row.mdText if hasattr(row, 'mdText') else row.text) for row in rows if (hasattr(row, 'mdText') and row.mdText) or (hasattr(row, 'text') and row.text)]
#                     columns_text = [sanitize_text(col.mdText if hasattr(col, 'mdText') else col.text) for col in columns if (hasattr(col, 'mdText') and col.mdText) or (hasattr(col, 'text') and col.text)]
                
#                 # Format the question
#                 if label and text:
#                     formatted_question = f"{label}. {text}"
#                     if options_text:
#                         formatted_question += f" Options: {', '.join(options_text)}"
#                     if rows_text:
#                         formatted_question += f" Rows: {', '.join(rows_text)}"
#                     if columns_text:
#                         formatted_question += f" Columns: {', '.join(columns_text)}"
#                     section_questions.append(formatted_question)
            
#             # Add section to the list if it has questions
#             if section_questions:
#                 sections_list.append({
#                     "section_name": section_name,
#                     "questions": section_questions
#                 })
        
#         print(f"Extracted questions from {len(sections_list)} sections")
#         return sections_list
    
#     except Exception as e:
#         print(f"Error extracting questions: {e}")
#         import traceback
#         print(traceback.format_exc())
#         return sections_list
        


def sanitize_text(text):
    """Sanitize text by replacing curly quotes with standard quotes."""
    if isinstance(text, str):
        text = text.replace("'", "'").replace("'", "'").replace(""", '"').replace(""", '"')
    return text

def find_question_by_label(complete_survey_data, target_label, format_as_string=True):
    """
    Finds a question by its label in the survey data structure.
    
    Args:
        complete_survey_data: The complete_survey_data object containing blocks and questions
        target_label: The label of the question to find (e.g., "Q2")
        format_as_string: If True, returns a dict with formatted text and ID, otherwise raw question
        
    Returns:
        If format_as_string is True: A dict with 'question_text' and 'question_id'
        If format_as_string is False: The complete question data as a dictionary
        Returns None if question is not found
    """
    try:
        # Try to access blocks
        blocks = None
        
        if hasattr(complete_survey_data, 'blocks'):
            blocks = complete_survey_data.blocks
        elif isinstance(complete_survey_data, dict) and 'blocks' in complete_survey_data:
            blocks = complete_survey_data['blocks']
        
        # If blocks is still None, return None
        if blocks is None:
            print("No blocks found in the survey data")
            return None
        
        # Search through all blocks and questions
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
                
            # Look for the question with the target label
            for question in questions:
                label = None
                
                if isinstance(question, dict):
                    label = question.get('label', '')
                else:
                    label = getattr(question, 'label', '')
                
                # If we found a matching label
                if label == target_label:
                    if not format_as_string:
                        return question
                    
                    # Extract question ID
                    question_id = ""
                    if isinstance(question, dict) and 'id' in question:
                        question_id = question['id']
                    elif hasattr(question, 'id'):
                        question_id = question.id
                    
                    # Format the question as a string
                    question_text = ""
                    
                    # Get the question text
                    q_text = ""
                    if isinstance(question, dict):
                        q_text = sanitize_text(question.get('mdText', question.get('text', question.get('question', ''))))
                    else:
                        if hasattr(question, 'mdText'):
                            q_text = sanitize_text(question.mdText)
                        elif hasattr(question, 'text'):
                            q_text = sanitize_text(question.text)
                        elif hasattr(question, 'question'):
                            q_text = sanitize_text(question.question)
                        else:
                            q_text = ''
                    
                    # Add the label in front of the question text
                    question_text = f"{label}. {q_text}"
                    
                    # Get options
                    options = []
                    if isinstance(question, dict) and 'options' in question:
                        options = question.get('options', [])
                        if options:
                            for opt in options:
                                opt_text = ""
                                if isinstance(opt, dict):
                                    opt_text = sanitize_text(opt.get('mdText', opt.get('text', '')))
                                else:
                                    opt_text = sanitize_text(getattr(opt, 'mdText', getattr(opt, 'text', '')))
                                if opt_text:
                                    question_text += f"\n{opt_text}"
                    elif hasattr(question, 'options'):
                        options = getattr(question, 'options', [])
                        if options:
                            for opt in options:
                                opt_text = ""
                                if hasattr(opt, 'mdText') and opt.mdText:
                                    opt_text = sanitize_text(opt.mdText)
                                elif hasattr(opt, 'text') and opt.text:
                                    opt_text = sanitize_text(opt.text)
                                if opt_text:
                                    question_text += f"\n{opt_text}"
                    
                    # Get rows if any
                    rows = []
                    if isinstance(question, dict) and 'rows' in question:
                        rows = question.get('rows', [])
                        if rows:
                            for row in rows:
                                row_text = ""
                                if isinstance(row, dict):
                                    row_text = sanitize_text(row.get('mdText', row.get('text', '')))
                                else:
                                    row_text = sanitize_text(getattr(row, 'mdText', getattr(row, 'text', '')))
                                if row_text:
                                    question_text += f"\n{row_text}"
                    elif hasattr(question, 'rows'):
                        rows = getattr(question, 'rows', [])
                        if rows:
                            for row in rows:
                                row_text = ""
                                if hasattr(row, 'mdText') and row.mdText:
                                    row_text = sanitize_text(row.mdText)
                                elif hasattr(row, 'text') and row.text:
                                    row_text = sanitize_text(row.text)
                                if row_text:
                                    question_text += f"\n{row_text}"
                    
                    # Get columns if any
                    columns = []
                    if isinstance(question, dict) and 'columns' in question:
                        columns = question.get('columns', [])
                        if columns:
                            for col in columns:
                                col_text = ""
                                if isinstance(col, dict):
                                    col_text = sanitize_text(col.get('mdText', col.get('text', '')))
                                else:
                                    col_text = sanitize_text(getattr(col, 'mdText', getattr(col, 'text', '')))
                                if col_text:
                                    question_text += f"\n{col_text}"
                    elif hasattr(question, 'columns'):
                        columns = getattr(question, 'columns', [])
                        if columns:
                            for col in columns:
                                col_text = ""
                                if hasattr(col, 'mdText') and col.mdText:
                                    col_text = sanitize_text(col.mdText)
                                elif hasattr(col, 'text') and col.text:
                                    col_text = sanitize_text(col.text)
                                if col_text:
                                    question_text += f"\n{col_text}"
                    
                    # Create and return the result dictionary
                    result = {
                        "question_text": question_text,
                        "question_id": question_id
                    }
                    return result
        
        # If we didn't find the question, return None
        print(f"No question found with label: {target_label}")
        return None
    
    except Exception as e:
        print(f"Error finding question: {e}")
        import traceback
        print(traceback.format_exc())
        return None

def generate_complete_questions(complete_survey_data):
    """
    Extracts survey questions grouped by sections, including options and rows/columns if present.

    Args:
        complete_survey_data: The complete_survey_data object containing blocks and questions

    Returns:
        A list of dictionaries with section_name and a list of formatted questions
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
                
            # Get section name
            section_name = None
            if isinstance(block, dict):
                section_name = block.get('name', 'Unnamed Section')
            elif hasattr(block, 'name'):
                section_name = getattr(block, 'name', 'Unnamed Section')
            else:
                section_name = 'Unnamed Section'
            
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
                    options_text = [sanitize_text(opt.get('mdText', opt.get('text', ''))) for opt in options if sanitize_text(opt.get('mdText', opt.get('text', '')))]
                elif hasattr(question, 'options'):
                    options = getattr(question, 'options', [])
                    options_text = [sanitize_text(opt.mdText if hasattr(opt, 'mdText') else opt.text) for opt in options if (hasattr(opt, 'mdText') and opt.mdText) or (hasattr(opt, 'text') and opt.text)]
                
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
                    "questions": section_questions
                })
        
        print(f"Extracted questions from {len(sections_list)} sections")
        return sections_list
    
    except Exception as e:
        print(f"Error extracting questions: {e}")
        import traceback
        print(traceback.format_exc())
        return sections_list