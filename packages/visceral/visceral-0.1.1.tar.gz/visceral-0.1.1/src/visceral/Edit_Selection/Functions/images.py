import modal
import pydantic
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Union, Any





testing_image = modal.Image.debian_slim(python_version="3.10").pip_install(
    "requests~=2.31.0",
    "nanoid","anthropic","instructor","pydantic","fastapi"  
)



# New Pydantic models
class QuestionItem(pydantic.BaseModel):
    id: str
    full_question_text: str
    question_type: str

class SurveyCorrection(pydantic.BaseModel):
    # Common fields
    user_id: int
    workspace_id: int
    team_id: int
    survey_id: int
    # Instructions that apply to all questions
    instructions: str
    selected_question_text: str
    previous_conversation: Optional[str]=None
    # Array of individual questions
    questions: List[QuestionItem]

class QuestionResponse(pydantic.BaseModel):
    correction: Optional[str]=None
    suggestion: Optional[str]=None
    chat: Optional[str]=None
    question_id: int
    question_type: str
    raw_question: str





