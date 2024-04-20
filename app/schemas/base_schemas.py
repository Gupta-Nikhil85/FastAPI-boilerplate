"""This file contains the schemas used for the open API documentation. It contains schemas based on different scenarios."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str


class NotFoundErrorResponse(BaseModel):
    message: str = "Resource not found"


class APIBaseResponse(BaseModel):
    message: str
    data: dict = None


class APIBaseListResponse(BaseModel):
    message: str
    data: list


class APIBasePaginatedResponse(BaseModel):
    message: str
    data: list
    page: int
    total_pages: int
    total_records: int
    page_size: int
