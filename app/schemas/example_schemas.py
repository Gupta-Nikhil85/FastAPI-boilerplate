from pydantic import BaseModel
from typing import List
from app.schemas.base_schemas import (
    APIBaseResponse,
    APIBaseListResponse,
    APIBasePaginatedResponse,
)


class ExampleBase(BaseModel):
    name: str
    value: int
    description: str


class GetExampleBaseSchema(ExampleBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True


class ExampleBaseResponseSchema(APIBaseResponse):
    data: GetExampleBaseSchema

    class Config:
        orm_mode = True


class ExampleBaseListResponseSchema(APIBaseListResponse):
    data: List[GetExampleBaseSchema]

    class Config:
        orm_mode = True


class ExampleBasePaginatedResponseSchema(APIBasePaginatedResponse):
    data: List[GetExampleBaseSchema]

    class Config:
        orm_mode = True
