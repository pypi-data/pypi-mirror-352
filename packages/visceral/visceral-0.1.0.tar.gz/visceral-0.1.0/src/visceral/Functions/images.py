import modal
import pydantic
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Union, Any, Literal


categorizer = modal.Image.debian_slim(python_version="3.10").pip_install(
    "anthropic",
    "fastapi",
    "pydantic",
    "instructor", 
    "openai",
    "pandas", "numpy", "openpyxl","websockets"
)



testing_image = modal.Image.debian_slim(python_version="3.10").pip_install(
    "requests~=2.31.0",
    "nanoid","anthropic","instructor","pydantic","fastapi"  , "pandas", "numpy", "openpyxl","websockets"
)


testing_image = testing_image.copy_local_file("survey_data.xlsx", "/app/survey_data.xlsx")

class Block_Section(pydantic.BaseModel):
    type: str
    text: str
    number_of_questions: int

# Update the request model to accept a list of blocks
class GenerateRequestForSection(pydantic.BaseModel):
    survey_agent_id: str
    blocks: List[Block_Section]
    
class ValidationData(pydantic.BaseModel):
    instructions: Optional[str] = None

# Updated Pydantic model to handle multiple questions
class QuestionInput(pydantic.BaseModel):
    correction: Optional[str] = None
    suggestion: Optional[str] = None
    raw_question: Optional[str] = None
    question_id: str
    type: Literal["correction", "suggestion", "both"]


class JsonPayload(pydantic.BaseModel):
    blocks: List[Dict[str, Any]]
    config: Dict[str, Any] = {}
    annotated_data: List[Dict[str, Any]]

class ConversationMessage(pydantic.BaseModel):
    from_: Literal["assistant", "user"] = pydantic.Field(alias="from")
    message: str

class SampleSpecs(pydantic.BaseModel):
    budget: Optional[str] = None
    audience: Optional[str] = None
    consumer_or_B2B: Optional[str] = None
    survey_length: Optional[float] = None
    target_audience: Optional[str] = None

class Metadata(pydantic.BaseModel):
    user_id: int
    workspace_id: int
    team_id: int
    survey_id: Union[int, str]
    complete_survey_data : Optional[JsonPayload] = None
    headers: Optional[str] = None
    previous_conversation: Optional[List[Dict[str,Any]]] = None
    objective: Optional[str] = None
    published: Optional[bool]=False
    authorization: Optional[str] = None
    sample_specs: Optional[SampleSpecs] = None
    survey_id_int: Optional[int] = None
    quotas: List[Dict[str, Any]] = Field(default_factory=list)
    


class RawQuestionText(pydantic.BaseModel):
    raw_question_text: Optional[str] = None
    question_label: Optional[str] = None
    response: Optional[str] = None
    type_of_section: Optional[str] = None
    number_of_questions: Optional[str] = None
    surveysection_details: Optional[str] = None
    question_id: Optional[str] = None
    question_type: Optional[str] = None
    section_name: Optional[str] = None
    instructions: Optional[str] = None
    panel_id: Optional[int] = None
    bid_id: Optional[int] = None
    quotas:Optional[List[Dict[str,Any]]] = None
    




class DeleteQuestion(pydantic.BaseModel):
    question_label: str


class Input_FE(pydantic.BaseModel):
    objective: str



frontend = modal.Image.debian_slim(python_version="3.10").pip_install(
    "anthropic",
    "fastapi",
    "pydantic",
    "instructor", "pymupdf","python-docx", "boto3 ", 
)