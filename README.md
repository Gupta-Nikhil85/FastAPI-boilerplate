# FastAPI boilerplate 

### A basic CRUD api using FastAPI, leveraging Object Oriented Programming Concepts.

# Installation Guide

This guide will help you set up and run your Python web application.

## Prerequisites

- Python 3.6 or higher installed on your system
- pip package manager
- Docker (optional, for Docker installation)

## Directory Structure
```plaintext
.
├── alembic
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
├── alembic.ini
├── app
│   ├── config.py
│   ├── database.py
│   ├── __init__.py
│   ├── models
│   │   ├── base_model.py
│   │   ├── example_model.py
│   │   └── __init__.py
│   ├── routes
│   │   ├── base_router.py
│   │   ├── example_router.py
│   │   └── __init__.py
│   ├── schemas
│   │   ├── base_schemas.py
│   │   ├── example_schemas.py
│   │   └──__init__.py 
│   └── utils
│       ├── constants.py
│       ├── helper_functions.py
│       └── permission_utils.py
├── main.py
├── .env-example
├── README.md
└── requirements.txt
```

## Installation Steps

1. **Clone the Repository**

    ```bash
    git clone git@github.com:Gupta-Nikhil85/FastAPI-broilerplate.git
    cd FastAPI-broilerplate
    ```

2. **Create a Virtual Environment** (optional but recommended)

    ```bash
    # Using virtualenv
    virtualenv venv
    source venv/bin/activate
    
    # Using venv (Python 3.6+)
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Database Setup** (assuming you're using SQLAlchemy with Alembic for migrations)

    - Initialize Alembic

        ```bash
        alembic init alembic
        ```

    - Edit `alembic.ini` to point to your database. Change the `sqlalchemy.url` in `alembic.ini` to your database URI.

    - Generate Initial Migration (optional, if you have models already)

        ```bash
        alembic revision --autogenerate -m "Initial migration"
        ```

    - Apply Migrations

        ```bash
        alembic upgrade head
        ```

5. **Configuration**

    - Copy `.env-example` to a new `.env` file, providing configurations for your app.

6. **Run the Application**

    ```bash
    uvicorn main:app --reload
    ```

7. **Access the Application**

    The application should be running now. Access it through a web browser or API client, depending on your project.

## Usage

### Example Model (`app/models/example_model.py`)
```python
from app.models.base_model import BaseModel
from sqlalchemy import String, Column, Integer


class ExampleModel(BaseModel):
    __tablename__ = "example"
    name = Column(String(255), nullable=False)
    value = Column(Integer, nullable=False)
    description = Column(String(255), nullable=False)

```

### Example Schemas (`app/schemas/example_schemas.py`)

```python
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

```

### Example Router (`app/routes/example_router.py`)

```python
from app.routes.base_router import BaseRouter
from app.models.example_model import ExampleModel
from app.schemas.example_schemas import (
    ExampleBase,
    ExampleBaseListResponseSchema,
    ExampleBasePaginatedResponseSchema,
    ExampleBaseResponseSchema,
)
from app.utils.permission_utils import check_read_permissions, check_write_permissions


class ExampleRouter(BaseRouter):
    def __init__(
        self
    ):
        super().__init__(
            ExampleModel,
            ExampleBaseResponseSchema,
            ExampleBasePaginatedResponseSchema,
            ExampleBaseListResponseSchema,
            ExampleBase,
            ExampleBase,
            check_read_permissions,
            check_write_permissions,
        )


router = ExampleRouter().get_router()

```


## Contributor Guidelines

Contributions are welcome! Please follow these guidelines:

- Fork the repository.
- Create a new branch for your feature/bug fix.
- Make your changes.
- Write tests if applicable.
- Run tests and ensure they pass.
- Commit your changes with descriptive messages.
- Push your changes to your fork.
- Create a pull request to the main repository.

## Author

- Nikhil Gupta <nikhilgupta8800@gmail.com>


## Notes

- Ensure that your database server is running and accessible.
- Make sure to set appropriate environment variables for sensitive data like database credentials in production.
- Modify the configuration files (`config.py`, `alembic.ini`) according to your environment needs.