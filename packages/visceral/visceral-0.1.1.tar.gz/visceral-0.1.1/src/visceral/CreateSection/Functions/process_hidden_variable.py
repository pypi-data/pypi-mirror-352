from CreateSection.Functions.generate_uuid import *
import time

def process_hidden_variables(question: dict) -> dict:
    """
    Process hidden variables in a question and create a new variable type question if needed.
    """
    if not question.get('hidden_variable') or not question.get("hidden-variable"):
        return None

    # Create a new question for the hidden variable
    hidden_var_question = {
        "id": generate_nano_id(),
        "text": question.get("question","Hidden Variable question"),
        "type": "variable",
        "issue": None,
        "label": f"{question['questionLabel']}HV",
        "config": {},
        "mdText": "Hidden Variable Question",
        "optout": {
            "text": None,
            "allowed": False
        },
        "created": int(uuid.uuid1().time * 1e-3),
        "dynamic": False,
        "options": [],
        "updated": int(time.time() * 1000),
        "condition": None,
        "confidence": 0.9,
        "definitions": []
    }

    # Process hidden variable definitions
    if isinstance(question['hidden-variable'], dict):
        for value, condition in question['hidden-variable'].items():
            hidden_var_question['definitions'].append({
                "value": value,
                "condition": condition
            })

    return hidden_var_question
