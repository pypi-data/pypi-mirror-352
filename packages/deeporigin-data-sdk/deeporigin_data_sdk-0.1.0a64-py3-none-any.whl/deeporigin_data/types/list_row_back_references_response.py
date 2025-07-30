# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .shared.database import Database
from .shared.workspace import Workspace
from .shared.database_row import DatabaseRow

__all__ = [
    "ListRowBackReferencesResponse",
    "Data",
    "DataRowSharedDatabase",
    "DataRowSharedDatabaseReferencedColumn",
    "DataRowSharedDatabaseReferencedColumnColumnBooleanBase",
    "DataRowSharedDatabaseReferencedColumnColumnDateBase",
    "DataRowSharedDatabaseReferencedColumnColumnEditorBase",
    "DataRowSharedDatabaseReferencedColumnColumnExpressionBase",
    "DataRowSharedDatabaseReferencedColumnColumnFileBase",
    "DataRowSharedDatabaseReferencedColumnColumnFileBaseConfigFile",
    "DataRowSharedDatabaseReferencedColumnColumnFloatBase",
    "DataRowSharedDatabaseReferencedColumnColumnFloatBaseConfigNumeric",
    "DataRowSharedDatabaseReferencedColumnColumnFloatBaseConfigNumericNumberFormat",
    "DataRowSharedDatabaseReferencedColumnColumnIntegerBase",
    "DataRowSharedDatabaseReferencedColumnColumnIntegerBaseConfigNumeric",
    "DataRowSharedDatabaseReferencedColumnColumnIntegerBaseConfigNumericNumberFormat",
    "DataRowSharedDatabaseReferencedColumnColumnReferenceBase",
    "DataRowSharedDatabaseReferencedColumnColumnSelectBase",
    "DataRowSharedDatabaseReferencedColumnColumnSelectBaseConfigSelect",
    "DataRowSharedDatabaseReferencedColumnColumnTextBase",
    "DataRowSharedDatabaseReferencedColumnColumnURLBase",
    "DataRowSharedDatabaseReferencedColumnColumnUserBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumn",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnDateBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnEditorBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnTextBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnURLBase",
    "DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnUserBase",
    "DataRowSharedDatabaseRow",
    "DataRowSharedDatabaseRowReferencedColumn",
    "DataRowSharedDatabaseRowReferencedColumnColumnBooleanBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnDateBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnEditorBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnExpressionBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnFileBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnFileBaseConfigFile",
    "DataRowSharedDatabaseRowReferencedColumnColumnFloatBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnFloatBaseConfigNumeric",
    "DataRowSharedDatabaseRowReferencedColumnColumnFloatBaseConfigNumericNumberFormat",
    "DataRowSharedDatabaseRowReferencedColumnColumnIntegerBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnIntegerBaseConfigNumeric",
    "DataRowSharedDatabaseRowReferencedColumnColumnIntegerBaseConfigNumericNumberFormat",
    "DataRowSharedDatabaseRowReferencedColumnColumnReferenceBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnSelectBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnSelectBaseConfigSelect",
    "DataRowSharedDatabaseRowReferencedColumnColumnTextBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnURLBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnUserBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumn",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnDateBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnEditorBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnTextBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnURLBase",
    "DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnUserBase",
    "DataRowSharedWorkspace",
    "DataRowSharedWorkspaceReferencedColumn",
    "DataRowSharedWorkspaceReferencedColumnColumnBooleanBase",
    "DataRowSharedWorkspaceReferencedColumnColumnDateBase",
    "DataRowSharedWorkspaceReferencedColumnColumnEditorBase",
    "DataRowSharedWorkspaceReferencedColumnColumnExpressionBase",
    "DataRowSharedWorkspaceReferencedColumnColumnFileBase",
    "DataRowSharedWorkspaceReferencedColumnColumnFileBaseConfigFile",
    "DataRowSharedWorkspaceReferencedColumnColumnFloatBase",
    "DataRowSharedWorkspaceReferencedColumnColumnFloatBaseConfigNumeric",
    "DataRowSharedWorkspaceReferencedColumnColumnFloatBaseConfigNumericNumberFormat",
    "DataRowSharedWorkspaceReferencedColumnColumnIntegerBase",
    "DataRowSharedWorkspaceReferencedColumnColumnIntegerBaseConfigNumeric",
    "DataRowSharedWorkspaceReferencedColumnColumnIntegerBaseConfigNumericNumberFormat",
    "DataRowSharedWorkspaceReferencedColumnColumnReferenceBase",
    "DataRowSharedWorkspaceReferencedColumnColumnSelectBase",
    "DataRowSharedWorkspaceReferencedColumnColumnSelectBaseConfigSelect",
    "DataRowSharedWorkspaceReferencedColumnColumnTextBase",
    "DataRowSharedWorkspaceReferencedColumnColumnURLBase",
    "DataRowSharedWorkspaceReferencedColumnColumnUserBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumn",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnDateBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnEditorBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnTextBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnURLBase",
    "DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnUserBase",
]


class DataRowSharedDatabaseReferencedColumnColumnBooleanBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnDateBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnEditorBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnExpressionBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnFileBaseConfigFile(BaseModel):
    allowed_extensions: Optional[List[str]] = FieldInfo(alias="allowedExtensions", default=None)


class DataRowSharedDatabaseReferencedColumnColumnFileBase(BaseModel):
    type: Literal["file"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_file: Optional[DataRowSharedDatabaseReferencedColumnColumnFileBaseConfigFile] = FieldInfo(
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


class DataRowSharedDatabaseReferencedColumnColumnFloatBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedDatabaseReferencedColumnColumnFloatBaseConfigNumeric(BaseModel):
    number_format: Optional[DataRowSharedDatabaseReferencedColumnColumnFloatBaseConfigNumericNumberFormat] = FieldInfo(
        alias="numberFormat", default=None
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedDatabaseReferencedColumnColumnFloatBase(BaseModel):
    type: Literal["float"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[DataRowSharedDatabaseReferencedColumnColumnFloatBaseConfigNumeric] = FieldInfo(
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


class DataRowSharedDatabaseReferencedColumnColumnIntegerBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedDatabaseReferencedColumnColumnIntegerBaseConfigNumeric(BaseModel):
    number_format: Optional[DataRowSharedDatabaseReferencedColumnColumnIntegerBaseConfigNumericNumberFormat] = (
        FieldInfo(alias="numberFormat", default=None)
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedDatabaseReferencedColumnColumnIntegerBase(BaseModel):
    type: Literal["integer"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[DataRowSharedDatabaseReferencedColumnColumnIntegerBaseConfigNumeric] = FieldInfo(
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


class DataRowSharedDatabaseReferencedColumnColumnReferenceBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnSelectBaseConfigSelect(BaseModel):
    options: List[str]

    can_create: Optional[bool] = FieldInfo(alias="canCreate", default=None)


class DataRowSharedDatabaseReferencedColumnColumnSelectBase(BaseModel):
    config_select: DataRowSharedDatabaseReferencedColumnColumnSelectBaseConfigSelect = FieldInfo(alias="configSelect")

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


class DataRowSharedDatabaseReferencedColumnColumnTextBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnURLBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnUserBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnDateBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnEditorBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile(BaseModel):
    allowed_extensions: Optional[List[str]] = FieldInfo(alias="allowedExtensions", default=None)


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBase(BaseModel):
    type: Literal["file"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_file: Optional[
        DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile
    ] = FieldInfo(alias="configFile", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat(
    BaseModel
):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric(BaseModel):
    number_format: Optional[
        DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat
    ] = FieldInfo(alias="numberFormat", default=None)
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBase(BaseModel):
    type: Literal["float"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[
        DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric
    ] = FieldInfo(alias="configNumeric", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat(
    BaseModel
):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric(
    BaseModel
):
    number_format: Optional[
        DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat
    ] = FieldInfo(alias="numberFormat", default=None)
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase(BaseModel):
    type: Literal["integer"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[
        DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric
    ] = FieldInfo(alias="configNumeric", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect(BaseModel):
    options: List[str]

    can_create: Optional[bool] = FieldInfo(alias="canCreate", default=None)


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBase(BaseModel):
    config_select: DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect = FieldInfo(
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


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnTextBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnURLBase(BaseModel):
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


class DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnUserBase(BaseModel):
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


DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumn: TypeAlias = Union[
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnDateBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnEditorBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnTextBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnURLBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumnColumnUserBase,
]


class DataRowSharedDatabaseReferencedColumnColumnLookupBase(BaseModel):
    lookup_external_column: DataRowSharedDatabaseReferencedColumnColumnLookupBaseLookupExternalColumn = FieldInfo(
        alias="lookupExternalColumn"
    )

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


DataRowSharedDatabaseReferencedColumn: TypeAlias = Union[
    DataRowSharedDatabaseReferencedColumnColumnBooleanBase,
    DataRowSharedDatabaseReferencedColumnColumnDateBase,
    DataRowSharedDatabaseReferencedColumnColumnEditorBase,
    DataRowSharedDatabaseReferencedColumnColumnExpressionBase,
    DataRowSharedDatabaseReferencedColumnColumnFileBase,
    DataRowSharedDatabaseReferencedColumnColumnFloatBase,
    DataRowSharedDatabaseReferencedColumnColumnIntegerBase,
    DataRowSharedDatabaseReferencedColumnColumnReferenceBase,
    DataRowSharedDatabaseReferencedColumnColumnSelectBase,
    DataRowSharedDatabaseReferencedColumnColumnTextBase,
    DataRowSharedDatabaseReferencedColumnColumnURLBase,
    DataRowSharedDatabaseReferencedColumnColumnUserBase,
    DataRowSharedDatabaseReferencedColumnColumnLookupBase,
]


class DataRowSharedDatabase(Database):
    referenced_column: DataRowSharedDatabaseReferencedColumn = FieldInfo(alias="referencedColumn")


class DataRowSharedDatabaseRowReferencedColumnColumnBooleanBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnDateBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnEditorBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnExpressionBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnFileBaseConfigFile(BaseModel):
    allowed_extensions: Optional[List[str]] = FieldInfo(alias="allowedExtensions", default=None)


class DataRowSharedDatabaseRowReferencedColumnColumnFileBase(BaseModel):
    type: Literal["file"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_file: Optional[DataRowSharedDatabaseRowReferencedColumnColumnFileBaseConfigFile] = FieldInfo(
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


class DataRowSharedDatabaseRowReferencedColumnColumnFloatBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedDatabaseRowReferencedColumnColumnFloatBaseConfigNumeric(BaseModel):
    number_format: Optional[DataRowSharedDatabaseRowReferencedColumnColumnFloatBaseConfigNumericNumberFormat] = (
        FieldInfo(alias="numberFormat", default=None)
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedDatabaseRowReferencedColumnColumnFloatBase(BaseModel):
    type: Literal["float"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[DataRowSharedDatabaseRowReferencedColumnColumnFloatBaseConfigNumeric] = FieldInfo(
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


class DataRowSharedDatabaseRowReferencedColumnColumnIntegerBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedDatabaseRowReferencedColumnColumnIntegerBaseConfigNumeric(BaseModel):
    number_format: Optional[DataRowSharedDatabaseRowReferencedColumnColumnIntegerBaseConfigNumericNumberFormat] = (
        FieldInfo(alias="numberFormat", default=None)
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedDatabaseRowReferencedColumnColumnIntegerBase(BaseModel):
    type: Literal["integer"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[DataRowSharedDatabaseRowReferencedColumnColumnIntegerBaseConfigNumeric] = FieldInfo(
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


class DataRowSharedDatabaseRowReferencedColumnColumnReferenceBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnSelectBaseConfigSelect(BaseModel):
    options: List[str]

    can_create: Optional[bool] = FieldInfo(alias="canCreate", default=None)


class DataRowSharedDatabaseRowReferencedColumnColumnSelectBase(BaseModel):
    config_select: DataRowSharedDatabaseRowReferencedColumnColumnSelectBaseConfigSelect = FieldInfo(
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


class DataRowSharedDatabaseRowReferencedColumnColumnTextBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnURLBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnUserBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnDateBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnEditorBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile(BaseModel):
    allowed_extensions: Optional[List[str]] = FieldInfo(alias="allowedExtensions", default=None)


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBase(BaseModel):
    type: Literal["file"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_file: Optional[
        DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile
    ] = FieldInfo(alias="configFile", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat(
    BaseModel
):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric(
    BaseModel
):
    number_format: Optional[
        DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat
    ] = FieldInfo(alias="numberFormat", default=None)
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBase(BaseModel):
    type: Literal["float"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[
        DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric
    ] = FieldInfo(alias="configNumeric", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat(
    BaseModel
):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric(
    BaseModel
):
    number_format: Optional[
        DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat
    ] = FieldInfo(alias="numberFormat", default=None)
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase(BaseModel):
    type: Literal["integer"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[
        DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric
    ] = FieldInfo(alias="configNumeric", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect(
    BaseModel
):
    options: List[str]

    can_create: Optional[bool] = FieldInfo(alias="canCreate", default=None)


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBase(BaseModel):
    config_select: DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect = FieldInfo(
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


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnTextBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnURLBase(BaseModel):
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


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnUserBase(BaseModel):
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


DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumn: TypeAlias = Union[
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnDateBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnEditorBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnTextBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnURLBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumnColumnUserBase,
]


class DataRowSharedDatabaseRowReferencedColumnColumnLookupBase(BaseModel):
    lookup_external_column: DataRowSharedDatabaseRowReferencedColumnColumnLookupBaseLookupExternalColumn = FieldInfo(
        alias="lookupExternalColumn"
    )

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


DataRowSharedDatabaseRowReferencedColumn: TypeAlias = Union[
    DataRowSharedDatabaseRowReferencedColumnColumnBooleanBase,
    DataRowSharedDatabaseRowReferencedColumnColumnDateBase,
    DataRowSharedDatabaseRowReferencedColumnColumnEditorBase,
    DataRowSharedDatabaseRowReferencedColumnColumnExpressionBase,
    DataRowSharedDatabaseRowReferencedColumnColumnFileBase,
    DataRowSharedDatabaseRowReferencedColumnColumnFloatBase,
    DataRowSharedDatabaseRowReferencedColumnColumnIntegerBase,
    DataRowSharedDatabaseRowReferencedColumnColumnReferenceBase,
    DataRowSharedDatabaseRowReferencedColumnColumnSelectBase,
    DataRowSharedDatabaseRowReferencedColumnColumnTextBase,
    DataRowSharedDatabaseRowReferencedColumnColumnURLBase,
    DataRowSharedDatabaseRowReferencedColumnColumnUserBase,
    DataRowSharedDatabaseRowReferencedColumnColumnLookupBase,
]


class DataRowSharedDatabaseRow(DatabaseRow):
    referenced_column: DataRowSharedDatabaseRowReferencedColumn = FieldInfo(alias="referencedColumn")


class DataRowSharedWorkspaceReferencedColumnColumnBooleanBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnDateBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnEditorBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnExpressionBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnFileBaseConfigFile(BaseModel):
    allowed_extensions: Optional[List[str]] = FieldInfo(alias="allowedExtensions", default=None)


class DataRowSharedWorkspaceReferencedColumnColumnFileBase(BaseModel):
    type: Literal["file"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_file: Optional[DataRowSharedWorkspaceReferencedColumnColumnFileBaseConfigFile] = FieldInfo(
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


class DataRowSharedWorkspaceReferencedColumnColumnFloatBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedWorkspaceReferencedColumnColumnFloatBaseConfigNumeric(BaseModel):
    number_format: Optional[DataRowSharedWorkspaceReferencedColumnColumnFloatBaseConfigNumericNumberFormat] = FieldInfo(
        alias="numberFormat", default=None
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedWorkspaceReferencedColumnColumnFloatBase(BaseModel):
    type: Literal["float"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[DataRowSharedWorkspaceReferencedColumnColumnFloatBaseConfigNumeric] = FieldInfo(
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


class DataRowSharedWorkspaceReferencedColumnColumnIntegerBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedWorkspaceReferencedColumnColumnIntegerBaseConfigNumeric(BaseModel):
    number_format: Optional[DataRowSharedWorkspaceReferencedColumnColumnIntegerBaseConfigNumericNumberFormat] = (
        FieldInfo(alias="numberFormat", default=None)
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedWorkspaceReferencedColumnColumnIntegerBase(BaseModel):
    type: Literal["integer"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[DataRowSharedWorkspaceReferencedColumnColumnIntegerBaseConfigNumeric] = FieldInfo(
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


class DataRowSharedWorkspaceReferencedColumnColumnReferenceBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnSelectBaseConfigSelect(BaseModel):
    options: List[str]

    can_create: Optional[bool] = FieldInfo(alias="canCreate", default=None)


class DataRowSharedWorkspaceReferencedColumnColumnSelectBase(BaseModel):
    config_select: DataRowSharedWorkspaceReferencedColumnColumnSelectBaseConfigSelect = FieldInfo(alias="configSelect")

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


class DataRowSharedWorkspaceReferencedColumnColumnTextBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnURLBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnUserBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnDateBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnEditorBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile(BaseModel):
    allowed_extensions: Optional[List[str]] = FieldInfo(alias="allowedExtensions", default=None)


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBase(BaseModel):
    type: Literal["file"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_file: Optional[
        DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile
    ] = FieldInfo(alias="configFile", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat(
    BaseModel
):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric(BaseModel):
    number_format: Optional[
        DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat
    ] = FieldInfo(alias="numberFormat", default=None)
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBase(BaseModel):
    type: Literal["float"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[
        DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric
    ] = FieldInfo(alias="configNumeric", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat(
    BaseModel
):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric(
    BaseModel
):
    number_format: Optional[
        DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat
    ] = FieldInfo(alias="numberFormat", default=None)
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase(BaseModel):
    type: Literal["integer"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[
        DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric
    ] = FieldInfo(alias="configNumeric", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect(BaseModel):
    options: List[str]

    can_create: Optional[bool] = FieldInfo(alias="canCreate", default=None)


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBase(BaseModel):
    config_select: DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect = FieldInfo(
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


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnTextBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnURLBase(BaseModel):
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


class DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnUserBase(BaseModel):
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


DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumn: TypeAlias = Union[
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnDateBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnEditorBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFileBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnFloatBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnSelectBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnTextBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnURLBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumnColumnUserBase,
]


class DataRowSharedWorkspaceReferencedColumnColumnLookupBase(BaseModel):
    lookup_external_column: DataRowSharedWorkspaceReferencedColumnColumnLookupBaseLookupExternalColumn = FieldInfo(
        alias="lookupExternalColumn"
    )

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


DataRowSharedWorkspaceReferencedColumn: TypeAlias = Union[
    DataRowSharedWorkspaceReferencedColumnColumnBooleanBase,
    DataRowSharedWorkspaceReferencedColumnColumnDateBase,
    DataRowSharedWorkspaceReferencedColumnColumnEditorBase,
    DataRowSharedWorkspaceReferencedColumnColumnExpressionBase,
    DataRowSharedWorkspaceReferencedColumnColumnFileBase,
    DataRowSharedWorkspaceReferencedColumnColumnFloatBase,
    DataRowSharedWorkspaceReferencedColumnColumnIntegerBase,
    DataRowSharedWorkspaceReferencedColumnColumnReferenceBase,
    DataRowSharedWorkspaceReferencedColumnColumnSelectBase,
    DataRowSharedWorkspaceReferencedColumnColumnTextBase,
    DataRowSharedWorkspaceReferencedColumnColumnURLBase,
    DataRowSharedWorkspaceReferencedColumnColumnUserBase,
    DataRowSharedWorkspaceReferencedColumnColumnLookupBase,
]


class DataRowSharedWorkspace(Workspace):
    referenced_column: DataRowSharedWorkspaceReferencedColumn = FieldInfo(alias="referencedColumn")


class Data(BaseModel):
    rows: List[Union[DataRowSharedDatabase, DataRowSharedDatabaseRow, DataRowSharedWorkspace]]


class ListRowBackReferencesResponse(BaseModel):
    data: Data
