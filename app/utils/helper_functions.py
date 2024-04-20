from app.schemas.base_schemas import NotFoundErrorResponse, ErrorResponse
import datetime
import pytz
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps


def handle_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTPExceptions as they are
            raise
        except SQLAlchemyError as e:
            # Handle database connection errors
            raise HTTPException(
                status_code=420,
                detail=f"Database connection error occurred: {e}",
                headers={"X-Error": "Database Error"},
            )
        except NotFoundErrorResponse as e:
            # Handle 404 errors
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource not found: {e.message}",
                headers={"X-Error": "Resource Not Found"},
            )
        except ErrorResponse as e:
            # Handle generic errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error occurred: {e.message}",
                headers={"X-Error": "Bad Request"},
            )
        except ValueError as e:
            # Handle value errors
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bad request error occurred: {str(e)}",
                headers={"X-Error": "Bad Request"},
            )
        except Exception as e:
            # Handle other unexpected errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error occurred: {str(e)}",
                headers={"X-Error": "Internal Server Error"},
            )

    return wrapper


def get_current_time():
    return (
        datetime.datetime.utcnow()
        .replace(tzinfo=pytz.utc)
        .astimezone(pytz.timezone("Asia/Kolkata"))
    )
