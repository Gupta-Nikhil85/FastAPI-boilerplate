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
