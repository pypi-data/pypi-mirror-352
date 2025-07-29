import copy
def delete_sections(data, section_name_to_delete: str):
    """
    Delete a section (block) from the survey data structure
    
    Args:
        data: The complete_survey_data (JsonPayload model or dict)
        section_name_to_delete: Name of the section to delete
        
    Returns:
        dict: The updated data in dictionary format, ready for JSON serialization
    """
    # Create a deep copy to avoid modifying the original data
    if hasattr(data, "dict") and callable(data.dict):
        # It's a Pydantic model
        data_dict = data.dict()
    else:
        # It's already a dict or something else
        data_dict = copy.deepcopy(data)
    
    # Check if blocks exist
    if "blocks" in data_dict:
        # Get the question IDs that will be deleted
        deleted_question_ids = []
        for block in data_dict["blocks"]:
            if block.get("name") == section_name_to_delete:
                questions = block.get("questions", [])
                deleted_question_ids = [q.get("id") for q in questions if q.get("id")]
                break
        
        # Filter out the block with the matching name
        original_blocks_length = len(data_dict["blocks"])
        data_dict["blocks"] = [
            block for block in data_dict["blocks"]
            if block.get("name") != section_name_to_delete
        ]
        new_blocks_length = len(data_dict["blocks"])
        
        # Also update annotated_data if any block was removed
        if (original_blocks_length > new_blocks_length and 
            "annotated_data" in data_dict and 
            deleted_question_ids):
            data_dict["annotated_data"] = [
                item for item in data_dict["annotated_data"]
                if item.get("id") not in deleted_question_ids
            ]
    
    # Always return a dictionary, not a Pydantic model
    return data_dict
