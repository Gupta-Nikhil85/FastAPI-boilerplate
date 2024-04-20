from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.documentation_schemas import ErrorResponse
from app.utils.helper_functions import handle_exceptions


class BaseRouter:
    __abstract__ = True

    def __init__(
        self,
        model,
        create_schema,
        get_schema,
        update_schema,
        success_creation_response,
        check_read_permissions,
        check_create_permission,
        check_edit_permissions,
    ):
        self.router = APIRouter()
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.get_schema = get_schema
        self.success_creation_response = success_creation_response
        self.check_create_permission = check_create_permission
        self.check_read_permissions = check_read_permissions
        self.check_edit_permissions = check_edit_permissions

        self.include_endpoints()

    # helper_functions

    def include_endpoints(self):
        self.generate_get_all_endpoint()
        self.generate_get_by_id_endpoint()
        self.generate_create_endpoint()
        self.generate_update_endpoint()
        self.generate_delete_endpoint()

    def get_router(self):
        return self.router

    # endpoints

    def generate_create_endpoint(self):
        @self.router.post(
            "/create/",
            status_code=status.HTTP_201_CREATED,
            responses=self.create_responses(),
        )
        @handle_exceptions
        async def create_record(
            request: self.create_schema = Body(...),
            db: Session = Depends(get_db),
            permissions=Depends(self.check_create_permission),
        ):
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
            permissions=Depends(self.check_read_permissions),
        ):
            return self.get_all_records(db)

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
            permissions=Depends(self.check_read_permissions),
        ):
            return self.get_record_by_id(record_id, db)

    def generate_update_endpoint(self):
        @self.router.put(
            "/update/{record_id}",
            status_code=status.HTTP_200_OK,
            responses=self.update_responses(),
        )
        @handle_exceptions
        async def update_record(
            record_id: str,
            request: self.update_schema = Body(...),
            db: Session = Depends(get_db),
            permissions=Depends(self.check_edit_permissions),
        ):
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
            permissions=Depends(self.check_edit_permissions),
        ):
            """
            Delete a specific record.

            This endpoint removes a record identified by the record ID. It deletes the record from the database.

            :param record_id: The unique identifier of the record.
            :param db: Database session dependency.

            :return: A success message upon successful deletion of the record.

            :raises HTTPException(404): If no record is found with the provided ID.
            :raises HTTPException(420): If a database error occurs.
            :raises HTTPException(500): If any other error occurred.
            """
            return self.delete_existing_record(record_id, db)

    # Core Functionality

    def get_all_records(self, db):
        f"""Retrieve all {self.model.__name__} records from database

        Args:
            db (Session, optional): Database Session Defaults to Depends(get_db).

        Raises:
            :raises HTTPException(204): If no {self.model.__name__} records are found.
            :raises HTTPException(420): If a database error occurs.
            :raises HTTPException(500): If any other error occurred.
        """
        records = self.model.get_all(db)

        if records is None:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail=f"No {self.model.__name__} Found",
            )

        return records

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
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail=f"No {self.model.__name__} Found With Given Id",
            )

        return record

    def create_new_record(self, request, db):
        new_record_data = {**request.model_dump()}
        record = self.model.create(db, **new_record_data)

        if record:
            return {
                "message": f"{self.model.__name__} created successfully",
                "details": record,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error occurred while creating {self.model.__name__}.",
            )

    def update_existing_record(self, record_id, request, db):
        new_record_data = {**request.model_dump()}
        record = self.model.update(record_id, db, **new_record_data)

        if record:
            return {
                "message": f"{self.model.__name__} updated successfully",
                "details": record,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error occurred while updating {self.model.__name__}.",
            )

    def delete_existing_record(self, record_id, db):
        existing_record = self.model.get_by_id(record_id, db)
        if existing_record is None:
            raise HTTPException(
                status_code=404, detail=f"No {self.model.__name__} found"
            )

        self.model.delete(record_id, db)
        return {"message": f"{self.model.__name__} deleted successfully"}

    # Responses

    def get_all_responses(self):
        return {
            200: {
                "model": list[self.get_schema],
                "description": f"The {self.model.__name__} records were successfully retrieved from the database. The response includes a JSON object containing the records' details.",
            },
            204: {"description": f"No {self.model.__name__} found."},
            420: {
                "model": ErrorResponse,
                "description": f"A database error occurred while processing the request. This could be due to a connection issue, a query error, or a data integrity issue.",
            },
            500: {
                "model": ErrorResponse,
                "description": f"An unexpected error occurred while processing the request. This could be due to a server issue or an unexpected exception.",
            },
        }

    def get_record_responses(self):
        return {
            200: {
                "model": self.get_schema,
                "description": f"The {self.model.__name__} record was successfully retrieved from the database. The response includes a JSON object containing the record's details.",
            },
            204: {"description": f"No {self.model.__name__} found."},
            420: {
                "model": ErrorResponse,
                "description": f"A database error occurred while processing the request. This could be due to a connection issue, a query error, or a data integrity issue.",
            },
            500: {
                "model": ErrorResponse,
                "description": f"An unexpected error occurred while processing the request. This could be due to a server issue or an unexpected exception.",
            },
        }

    def create_responses(self):
        return {
            201: {
                "model": self.success_creation_response,
                "description": f"The {self.model.__name__} was successfully created. The response includes a success message and a JSON object containing the details of the created {self.model.__name__}.",
            },
            420: {
                "model": ErrorResponse,
                "description": f"A database error occurred while processing the request. This could be due to a connection issue, a query error, or a data integrity issue.",
            },
            500: {
                "model": ErrorResponse,
                "description": f"An unexpected error occurred while processing the request. This could be due to a server issue or an unexpected exception.",
            },
        }

    def update_responses(self):
        return {
            200: {
                "model": self.success_creation_response,
                "description": f"The {self.model.__name__} was successfully updated. The response includes a success message and a JSON object containing the details of the updated {self.model.__name__}.",
            },
            420: {
                "model": ErrorResponse,
                "description": f"A database error occurred while processing the request. This could be due to a connection issue, a query error, or a data integrity issue.",
            },
            500: {
                "model": ErrorResponse,
                "description": f"An unexpected error occurred while processing the request. This could be due to a server issue or an unexpected exception.",
            },
        }

    def delete_responses(self):
        return {
            200: {
                "model": str,
                "description": f"The {self.model.__name__} was successfully deleted. The response includes a success message.",
            },
            404: {
                "model": ErrorResponse,
                "description": f"The requested {self.model.__name__} could not be found in the database. This could be because the {self.model.__name__} does not exist or the provided ID is incorrect.",
            },
            420: {
                "model": ErrorResponse,
                "description": f"A database error occurred while processing the request. This could be due to a connection issue, a query error, or a data integrity issue.",
            },
            500: {
                "model": ErrorResponse,
                "description": f"An unexpected error occurred while processing the request. This could be due to a server issue or an unexpected exception.",
            },
        }
