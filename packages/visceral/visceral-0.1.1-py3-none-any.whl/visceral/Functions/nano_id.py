
import uuid

def generate_nano_id():
    return str(uuid.uuid4())

def generate_nano_id_for_label():
    return str(uuid.uuid4())[:3]
