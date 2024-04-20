from fastapi import APIRouter, Depends, status, Body, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.base_schemas import (
    APIBaseListResponse,
    APIBasePaginatedResponse,
    APIBaseResponse,
    ErrorResponse,
    NotFoundErrorResponse,
)
from app.utils.helper_functions import handle_exceptions
from app.utils.constants import PAGE_SIZE


class BaseRouter:
    __abstract__ = True

    def __init__(
        self,
        model,
        get_response_schema,
        get_paginated_schema,
        get_all_schema,
        create_schema,
        update_schema,
        read_permissions,
        write_permissions,
    ):
        self.router = APIRouter()
        self.model = model
        self.get_response_schema = get_response_schema
        self.get_paginated_schema = get_paginated_schema
        self.get_all_schema = get_all_schema
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.read_permissions = read_permissions
        self.write_permissions = write_permissions

        self.base_response = {
            status.HTTP_404_NOT_FOUND: {
                "description": f"No {self.model.__name__} found."
            },
            420: {
                "model": ErrorResponse,
                "description": f"A database error occurred while processing the request. This could be due to a connection issue, a query error, or a data integrity issue.",
            },
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "model": ErrorResponse,
                "description": f"An unexpected error occurred while processing the request. This could be due to a server issue or an unexpected exception.",
            },
        }

        self.include_endpoints()

    # helper_functions

    def include_endpoints(self):
        self.generate_get_all_endpoint()
        self.generate_get_paginated_endpoint()
        self.generate_get_by_id_endpoint()
        self.generate_create_endpoint()
        self.generate_update_endpoint()
        self.generate_delete_endpoint()

    def get_router(self):
        return self.router

    # endpoints

    def generate_create_endpoint(self):
        @self.router.post(
            "/",
            status_code=status.HTTP_201_CREATED,
            responses=self.create_responses(),
        )
        @handle_exceptions
        async def create_record(
            request: self.create_schema = Body(...),
            db: Session = Depends(get_db),
            permissions: dict = Depends(self.write_permissions),
        ):
            """
            Create a new record.

            This endpoint creates a new record in the database with the data provided in the request.

            :param request: The request body containing the data for the new record.
            :param db: Database session dependency.
            :param permissions: Permission dependency.

            :return: A success message upon successful creation of the record along with the record details.

            :raises HTTPException(420): If a database error occurs.
            :raises HTTPException(500): If any other error occurred.
            """
            return self.create_new_record(request, db)

    def generate_get_all_endpoint(self):
        @self.router.get(
            "/all",
            status_code=status.HTTP_200_OK,
            responses=self.get_all_responses(),
        )
        @handle_exceptions
        async def get_records(
            db: Session = Depends(get_db),
            permissions: dict = Depends(self.read_permissions),
        ):
            """
            Retrieve all records.

            This endpoint retrieves all records from the database and returns the record details.

            :param db: Database session dependency.
            :param permissions: Permission dependency.

            :return: A success message upon successful retrieval of the records along with the record details.

            :raises HTTPException(404): If no records are found.
            :raises HTTPException(420): If a database error occurs.
            :raises HTTPException(500): If any other error occurred.
            """
            return self.get_all_records(db)

    def generate_get_paginated_endpoint(self):
        @self.router.get(
            "/paginated",
            status_code=status.HTTP_200_OK,
            responses=self.get_paginated_records_responses(),
        )
        @handle_exceptions
        async def get_records(
            page: int = Query(1),
            limit: int = Query(PAGE_SIZE),
            sort_by: str = Query("created_at"),
            order: str = Query("asc"),
            min_date: str = Query(None),
            max_date: str = Query(None),
            min_value: int = Query(None),
            max_value: int = Query(None),
            search_field: str = Query(None),
            search: str = Query(None),
            db: Session = Depends(get_db),
            permissions: dict = Depends(self.read_permissions),
        ):
            """
            Retrieve all records.

            This endpoint retrieves all records from the database and returns the record details.

            :param page: The page number for pagination.
            :param limit: The number of records per page.
            :param sort_by: The field to sort the records by.
            :param order: The order to sort the records in (asc or desc).
            :param min_date: The minimum date to filter the records by.
            :param max_date: The maximum date to filter the records by.
            :param min_value: The minimum value to filter the records by.
            :param max_value: The maximum value to filter the records by.
            :param search_field: The field to search the records by.
            :param search: The search query to filter the records by.
            :param db: Database session dependency.
            :param permissions: Permission dependency.

            :return: A success message upon successful retrieval of the records along with the record details.

            :raises HTTPException(404): If no records are found.
            :raises HTTPException(420): If a database error occurs.
            :raises HTTPException(500): If any other error occurred.
            """
            return self.get_paginated_records(
                db,
                page,
                limit,
                sort_by,
                order,
                min_date,
                max_date,
                min_value,
                max_value,
                search_field,
                search,
            )

    def generate_get_by_id_endpoint(self):
        @self.router.get(
            "/{record_id}",
            status_code=status.HTTP_200_OK,
            responses=self.get_record_responses(),
        )
        @handle_exceptions
        async def get_record_by_id(
            record_id: str,
            db: Session = Depends(get_db),
            permissions=Depends(self.read_permissions),
        ):
            """
            Retrieve a specific record.

            This endpoint retrieves a record identified by the record ID. It fetches the record from the database and returns the record details.

            :param record_id: The unique identifier of the record.
            :param db: Database session dependency.
            :param permissions: Permission dependency.

            :return: A success message upon successful retrieval of the record along with the record details.

            :raises HTTPException(404): If no record is found with the provided ID.
            :raises HTTPException(420): If a database error occurs.
            :raises HTTPException(500): If any other error occurred.

            """
            return self.get_record_by_id(record_id, db)

    def generate_update_endpoint(self):
        @self.router.put(
            "/{record_id}",
            status_code=status.HTTP_200_OK,
            responses=self.update_responses(),
        )
        @handle_exceptions
        async def update_record(
            record_id: str,
            request: self.update_schema = Body(...),
            db: Session = Depends(get_db),
            permissions: dict = Depends(self.write_permissions),
        ):
            """
            Update a specific record.

            This endpoint updates a record identified by the record ID. It updates the record in the database with the new data provided in the request.

            :param record_id: The unique identifier of the record.
            :param request: The request body containing the updated record data.
            :param db: Database session dependency.
            :param permissions: Permission dependency.

            :return: A success message upon successful update of the record along with the updated details.

            :raises HTTPException(404): If no record is found with the provided ID.
            :raises HTTPException(420): If a database error occurs.
            :raises HTTPException(500): If any other error occurred.

            """
            return self.update_existing_record(record_id, request, db)

    def generate_delete_endpoint(self):
        @self.router.delete(
            "/{record_id}",
            status_code=status.HTTP_200_OK,
            responses=self.delete_responses(),
        )
        @handle_exceptions
        async def delete_record(
            record_id: str,
            db: Session = Depends(get_db),
            permissions: dict = Depends(self.write_permissions),
        ):
            """
            Delete a specific record.

            This endpoint removes a record identified by the record ID. It deletes the record from the database.

            :param record_id: The unique identifier of the record.
            :param db: Database session dependency.
            :param permissions: Permission dependency.

            :return: A success message upon successful deletion of the record.

            :raises HTTPException(404): If no record is found with the provided ID.
            :raises HTTPException(420): If a database error occurs.
            :raises HTTPException(500): If any other error occurred.
            """
            return self.delete_existing_record(record_id, db)

    # Core Functionality

    def get_all_records(
        self,
        db,
        sort_by: str = "created_at",
        order: str = "asc",
        min_date: str = None,
        max_date: str = None,
        min_value: int = None,
        max_value: int = None,
        search_field: str = None,
        search: str = None,
    ):
        f"""Retrieve all {self.model.__name__} records from database

        Args:
            db (Session, optional): Database Session Defaults to Depends(get_db).

        Raises:
            :raises HTTPException(204): If no {self.model.__name__} records are found.
            :raises HTTPException(420): If a database error occurs.
            :raises HTTPException(500): If any other error occurred.
        """
        records = self.model.get_all(
            db,
            sort_by,
            order,
            min_date,
            max_date,
            min_value,
            max_value,
            search_field,
            search,
        )

        if records is None:
            return APIBaseListResponse(
                message=f"No {self.model.__name__} records found", data=[]
            )

        return APIBaseListResponse(
            message=f"All {self.model.__name__} records", data=records
        )

    def get_paginated_records(
        self,
        db,
        page: int = 1,
        limit: int = PAGE_SIZE,
        sort_by: str = "created_at",
        order: str = "asc",
        min_date: str = None,
        max_date: str = None,
        min_value: int = None,
        max_value: int = None,
        search_field: str = None,
        search: str = None,
    ):
        f"""Retrieve all {self.model.__name__} records from database

        Args:
            db (Session, optional): Database Session Defaults to Depends(get_db).

        Raises:
            :raises HTTPException(204): If no {self.model.__name__} records are found.
            :raises HTTPException(420): If a database error occurs.
            :raises HTTPException(500): If any other error occurred.
        """
        records = self.model.get_paginated(
            db,
            page,
            limit,
            sort_by,
            order,
            min_date,
            max_date,
            min_value,
            max_value,
            search_field,
            search,
        )
        pagination_metadata = self.model.get_pagination_metadata(
            db,
            page,
            limit,
            sort_by,
            order,
            min_date,
            max_date,
            min_value,
            max_value,
            search_field,
            search,
        )

        if records is None:
            return APIBasePaginatedResponse(
                message=f"No {self.model.__name__} records found",
                data=[],
                page=page,
                total_pages=pagination_metadata["total_pages"],
                total_records=pagination_metadata["total_count"],
                page_size=limit,
            )

        return APIBasePaginatedResponse(
            message=f"All {self.model.__name__} records",
            data=records,
            page=page,
            total_pages=pagination_metadata["total_pages"],
            total_records=pagination_metadata["total_count"],
            page_size=limit,
        )

    def get_record_by_id(self, record_id, db):
        f"""Retrieve {self.model.__name__} record with given id from database

        Args:
            db (Session, optional): Database Session Defaults to Depends(get_db).

        Raises:
            :raises HTTPException(204): If no {self.model.__name__} record with given id is found.
            :raises HTTPException(420): If a database error occurs.
            :raises HTTPException(500): If any other error occurred.
        """
        record = self.model.get_by_id(record_id, db)

        if record is None:
            raise NotFoundErrorResponse(
                message=f"No {self.model.__name__} Found With Given Id"
            )

        return APIBaseResponse(message=f"{self.model.__name__} Found", data=record)

    def create_new_record(self, request, db):
        new_record_data = {**request.model_dump()}
        record = self.model.create(db, **new_record_data)

        if not record:
            raise ErrorResponse(
                message=f"Error Occurred While Creating {self.model.__name__}"
            )

        return APIBaseResponse(
            message=f"{self.model.__name__} Created Successfully", data=record
        )

    def update_existing_record(self, record_id, request, db):

        existing_record = self.model.get_by_id(record_id, db)
        if existing_record is None:
            raise NotFoundErrorResponse(
                message=f"No {self.model.__name__} Found With Given Id"
            )

        new_record_data = {**request.model_dump()}
        record = self.model.update(record_id, db, **new_record_data)

        if not record:
            raise ErrorResponse(
                message=f"Error Occurred While Updating {self.model.__name__}"
            )

        return APIBaseResponse(
            message=f"{self.model.__name__} Updated Successfully", data=record
        )

    def delete_existing_record(self, record_id, db):
        existing_record = self.model.get_by_id(record_id, db)
        if existing_record is None:
            raise NotFoundErrorResponse(
                message=f"No {self.model.__name__} Found With Given Id"
            )

        self.model.delete(record_id, db)
        return APIBaseResponse(message=f"{self.model.__name__} Deleted Successfully")

    # Responses

    def get_all_responses(self):
        return {
            **self.base_response,
            status.HTTP_200_OK: {
                "model": self.get_all_schema,
                "description": f"The {self.model.__name__} records were successfully retrieved from the database. The response includes a JSON object containing the records' details.",
            },
        }

    def get_paginated_records_responses(self):
        return {
            **self.base_response,
            status.HTTP_200_OK: {
                "model": self.get_paginated_schema,
                "description": f"The {self.model.__name__} records were successfully retrieved from the database. The response includes a JSON object containing the records' details.",
            },
        }

    def get_record_responses(self):
        return {
            **self.base_response,
            status.HTTP_200_OK: {
                "model": self.get_response_schema,
                "description": f"The {self.model.__name__} record was successfully retrieved from the database. The response includes a JSON object containing the record's details.",
            },
        }

    def create_responses(self):
        return {
            **self.base_response,
            status.HTTP_201_CREATED: {
                "model": self.get_response_schema,
                "description": f"The {self.model.__name__} was successfully created. The response includes a success message and a JSON object containing the details of the created {self.model.__name__}.",
            },
        }

    def update_responses(self):
        return {
            **self.base_response,
            status.HTTP_200_OK: {
                "model": self.get_response_schema,
                "description": f"The {self.model.__name__} was successfully updated. The response includes a success message and a JSON object containing the updated details of the {self.model.__name__}.",
            },
        }

    def delete_responses(self):
        return {
            **self.base_response,
            status.HTTP_200_OK: {
                "model": APIBaseResponse,
                "description": f"The {self.model.__name__} was successfully deleted. The response includes a success message.",
            },
        }
