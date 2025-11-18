"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Survey-related schemas

class SurveyQuestion(BaseModel):
    id: str
    topic: str
    text: str
    type: Literal["scale", "single", "text"] = "scale"
    options: Optional[List[str]] = None

class Survey(BaseModel):
    survey_id: str
    title: str
    description: str
    questions: List[SurveyQuestion]

class SurveyAnswer(BaseModel):
    question_id: str
    answer: str

class SurveyResponse(BaseModel):
    """
    Survey responses collection schema
    Collection name: "surveyresponse"
    """
    survey_id: str
    answers: List[SurveyAnswer]
    user_agent: Optional[str] = None
    ip: Optional[str] = None
