def extract_conversation_from_metadata(metadata) -> str:
    """
    Extract conversation markdown from Metadata object
    
    Args:
        metadata (Metadata): Pydantic model containing previous_conversation_json
        
    Returns:
        str: The extracted conversation with messages separated by new lines
    """
    # Check if previous_conversation_json exists
    if not metadata.previous_conversation:
        return ""

    # Extract markdown from each message
    messages = []
    for message in metadata.previous_conversation:
        if "markdown" in message:
            messages.append(message["markdown"])
    
    # Join messages with double newlines
    return "\n\n".join(messages)