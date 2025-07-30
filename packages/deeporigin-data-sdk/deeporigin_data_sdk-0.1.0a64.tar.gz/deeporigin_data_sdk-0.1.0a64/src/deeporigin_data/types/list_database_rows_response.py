# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .shared.database_row import DatabaseRow

__all__ = ["ListDatabaseRowsResponse", "Meta"]


class Meta(BaseModel):
    count: float
    """The total number of rows in the database."""


class ListDatabaseRowsResponse(BaseModel):
    data: List[DatabaseRow]

    meta: Meta
