from app.models.base_model import BaseModel
from sqlalchemy import String, Column, Integer


class ExampleModel(BaseModel):
    __tablename__ = "example"
    name = Column(String(255), nullable=False)
    value = Column(Integer, nullable=False)
    description = Column(String(255), nullable=False)
