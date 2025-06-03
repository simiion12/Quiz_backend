from typing import List, Optional, Tuple, Annotated
from pydantic import BaseModel, Field
from bson import ObjectId

# Custom type for ObjectId
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, (str, ObjectId)):
            raise ValueError("Invalid ObjectId")
        return str(v)

class Question(BaseModel):
    image_url: Optional[str] = None
    image_key: Optional[str] = None
    question: str
    answer: List[Tuple[bool, str]]
    explanation: Optional[str] = None

class Quiz(BaseModel):
    id: Annotated[str, Field(default_factory=lambda: str(ObjectId()), alias="_id")]
    course_id: int
    quiz_number: int
    questions: List[Question]
    time_for_completion: int
    is_active: bool

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }