def get_block_names(payload):
    # Check if payload is a JsonPayload object and convert it to a dictionary
    if hasattr(payload, 'to_dict'):
        payload_dict = payload.to_dict()  # Use to_dict() if available
    elif hasattr(payload, '__dict__'):
        payload_dict = payload.__dict__  # Convert object attributes to dict
    else:
        payload_dict = dict(payload)  # Try to cast directly to dict
    
    # Access the blocks from the dictionary
    blocks = payload_dict["blocks"]
    block_names = [block["name"] for block in blocks]
    return block_names