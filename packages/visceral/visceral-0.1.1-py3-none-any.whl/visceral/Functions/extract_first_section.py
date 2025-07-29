def extract_first_section(test_payload):
    print("test_payload", test_payload)
    """
    Extracts questions from the first block/section of the survey data.
    
    Args:
        test_payload: The survey data payload
        
    Returns:
        List of questions from the first block, or empty list if not found
    """
    try:
        # Access blocks - try both attribute and dictionary access
        if hasattr(test_payload, 'blocks'):
            blocks = test_payload.blocks
        elif isinstance(test_payload, dict) and 'blocks' in test_payload:
            blocks = test_payload['blocks']
        else:
            print("No blocks found in payload")
            return []
        
        # Check if blocks is empty
        if not blocks or len(blocks) == 0:
            print("Blocks list is empty")
            return []
        
        # Get the first block
        first_block = blocks[0]
        
        # Get questions from the first block
        if isinstance(first_block, dict) and 'questions' in first_block:
            return first_block['questions']
        elif hasattr(first_block, 'questions'):
            return first_block.questions
        else:
            print("No questions found in the first block")
            return []
            
    except Exception as e:
        print(f"Error extracting first section: {e}")
        return []