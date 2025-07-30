# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.database import Database

__all__ = [
    "UpdateDatabaseColumnResponse",
    "Data",
    "DataColumn",
    "DataColumnColumnBooleanBase",
    "DataColumnColumnDateBase",
    "DataColumnColumnEditorBase",
    "DataColumnColumnExpressionBase",
    "DataColumnColumnFileBase",
    "DataColumnColumnFileBaseConfigFile",
    "DataColumnColumnFloatBase",
    "DataColumnColumnFloatBaseConfigNumeric",
    "DataColumnColumnFloatBaseConfigNumericNumberFormat",
    "DataColumnColumnIntegerBase",
    "DataColumnColumnIntegerBaseConfigNumeric",
    "DataColumnColumnIntegerBaseConfigNumericNumberFormat",
    "DataColumnColumnReferenceBase",
    "DataColumnColumnSelectBase",
    "DataColumnColumnSelectBaseConfigSelect",
    "DataColumnColumnTextBase",
    "DataColumnColumnURLBase",
    "DataColumnColumnUserBase",
    "DataColumnColumnLookupBase",
    "DataColumnColumnLookupBaseLookupExternalColumn",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnDateBase",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnEditorBase",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnFileBase",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnFloatBase",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnSelectBase",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnTextBase",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnURLBase",
    "DataColumnColumnLookupBaseLookupExternalColumnColumnUserBase",
]


class DataColumnColumnBooleanBase(BaseModel):
    type: Literal["boolean"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnDateBase(BaseModel):
    type: Literal["date"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnEditorBase(BaseModel):
    type: Literal["editor"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnExpressionBase(BaseModel):
    expression_code: str = FieldInfo(alias="expressionCode")

    expression_return_type: Literal["text", "float", "integer"] = FieldInfo(alias="expressionReturnType")

    type: Literal["expression"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnFileBaseConfigFile(BaseModel):
    allowed_extensions: Optional[List[str]] = FieldInfo(alias="allowedExtensions", default=None)


class DataColumnColumnFileBase(BaseModel):
    type: Literal["file"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_file: Optional[DataColumnColumnFileBaseConfigFile] = FieldInfo(alias="configFile", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnFloatBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataColumnColumnFloatBaseConfigNumeric(BaseModel):
    number_format: Optional[DataColumnColumnFloatBaseConfigNumericNumberFormat] = FieldInfo(
        alias="numberFormat", default=None
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataColumnColumnFloatBase(BaseModel):
    type: Literal["float"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[DataColumnColumnFloatBaseConfigNumeric] = FieldInfo(alias="configNumeric", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnIntegerBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataColumnColumnIntegerBaseConfigNumeric(BaseModel):
    number_format: Optional[DataColumnColumnIntegerBaseConfigNumericNumberFormat] = FieldInfo(
        alias="numberFormat", default=None
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataColumnColumnIntegerBase(BaseModel):
    type: Literal["integer"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[DataColumnColumnIntegerBaseConfigNumeric] = FieldInfo(alias="configNumeric", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnReferenceBase(BaseModel):
    reference_database_row_id: str = FieldInfo(alias="referenceDatabaseRowId")

    type: Literal["reference"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnSelectBaseConfigSelect(BaseModel):
    options: List[str]

    can_create: Optional[bool] = FieldInfo(alias="canCreate", default=None)


class DataColumnColumnSelectBase(BaseModel):
    config_select: DataColumnColumnSelectBaseConfigSelect = FieldInfo(alias="configSelect")

    type: Literal["select"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnTextBase(BaseModel):
    type: Literal["text"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnURLBase(BaseModel):
    type: Literal["url"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnUserBase(BaseModel):
    type: Literal["user"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase(BaseModel):
    type: Literal["boolean"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnDateBase(BaseModel):
    type: Literal["date"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnEditorBase(BaseModel):
    type: Literal["editor"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase(BaseModel):
    expression_code: str = FieldInfo(alias="expressionCode")

    expression_return_type: Literal["text", "float", "integer"] = FieldInfo(alias="expressionReturnType")

    type: Literal["expression"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile(BaseModel):
    allowed_extensions: Optional[List[str]] = FieldInfo(alias="allowedExtensions", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnFileBase(BaseModel):
    type: Literal["file"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_file: Optional[DataColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile] = FieldInfo(
        alias="configFile", default=None
    )

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric(BaseModel):
    number_format: Optional[DataColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat] = (
        FieldInfo(alias="numberFormat", default=None)
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataColumnColumnLookupBaseLookupExternalColumnColumnFloatBase(BaseModel):
    type: Literal["float"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[DataColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric] = FieldInfo(
        alias="configNumeric", default=None
    )

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric(BaseModel):
    number_format: Optional[
        DataColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat
    ] = FieldInfo(alias="numberFormat", default=None)
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase(BaseModel):
    type: Literal["integer"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[DataColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric] = FieldInfo(
        alias="configNumeric", default=None
    )

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase(BaseModel):
    reference_database_row_id: str = FieldInfo(alias="referenceDatabaseRowId")

    type: Literal["reference"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect(BaseModel):
    options: List[str]

    can_create: Optional[bool] = FieldInfo(alias="canCreate", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnSelectBase(BaseModel):
    config_select: DataColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect = FieldInfo(
        alias="configSelect"
    )

    type: Literal["select"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnTextBase(BaseModel):
    type: Literal["text"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnURLBase(BaseModel):
    type: Literal["url"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataColumnColumnLookupBaseLookupExternalColumnColumnUserBase(BaseModel):
    type: Literal["user"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


DataColumnColumnLookupBaseLookupExternalColumn: TypeAlias = Union[
    DataColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase,
    DataColumnColumnLookupBaseLookupExternalColumnColumnDateBase,
    DataColumnColumnLookupBaseLookupExternalColumnColumnEditorBase,
    DataColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase,
    DataColumnColumnLookupBaseLookupExternalColumnColumnFileBase,
    DataColumnColumnLookupBaseLookupExternalColumnColumnFloatBase,
    DataColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase,
    DataColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase,
    DataColumnColumnLookupBaseLookupExternalColumnColumnSelectBase,
    DataColumnColumnLookupBaseLookupExternalColumnColumnTextBase,
    DataColumnColumnLookupBaseLookupExternalColumnColumnURLBase,
    DataColumnColumnLookupBaseLookupExternalColumnColumnUserBase,
]


class DataColumnColumnLookupBase(BaseModel):
    lookup_external_column: DataColumnColumnLookupBaseLookupExternalColumn = FieldInfo(alias="lookupExternalColumn")

    lookup_external_column_id: str = FieldInfo(alias="lookupExternalColumnId")

    lookup_source_column_id: str = FieldInfo(alias="lookupSourceColumnId")

    type: Literal["lookup"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


DataColumn: TypeAlias = Union[
    DataColumnColumnBooleanBase,
    DataColumnColumnDateBase,
    DataColumnColumnEditorBase,
    DataColumnColumnExpressionBase,
    DataColumnColumnFileBase,
    DataColumnColumnFloatBase,
    DataColumnColumnIntegerBase,
    DataColumnColumnReferenceBase,
    DataColumnColumnSelectBase,
    DataColumnColumnTextBase,
    DataColumnColumnURLBase,
    DataColumnColumnUserBase,
    DataColumnColumnLookupBase,
]


class Data(BaseModel):
    column: DataColumn

    database: Database


class UpdateDatabaseColumnResponse(BaseModel):
    data: Data
