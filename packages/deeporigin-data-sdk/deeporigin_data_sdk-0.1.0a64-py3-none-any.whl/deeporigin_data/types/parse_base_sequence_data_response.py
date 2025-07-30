# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ParseBaseSequenceDataResponse", "Data", "DataAnnotation"]


class DataAnnotation(BaseModel):
    end: float

    name: str

    start: float

    color: Optional[str] = None

    direction: Union[Literal[1, -1], float, None] = None

    type: Optional[str] = None


class Data(BaseModel):
    seq: str

    annotations: Optional[List[DataAnnotation]] = None

    name: Optional[str] = None

    type: Optional[Literal["dna", "rna", "aa", "unknown"]] = None


class ParseBaseSequenceDataResponse(BaseModel):
    data: Data
