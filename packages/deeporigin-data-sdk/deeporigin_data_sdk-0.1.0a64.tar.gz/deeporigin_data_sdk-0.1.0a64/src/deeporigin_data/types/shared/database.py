# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = [
    "Database",
    "Col",
    "ColColumnBooleanBase",
    "ColColumnDateBase",
    "ColColumnEditorBase",
    "ColColumnExpressionBase",
    "ColColumnFileBase",
    "ColColumnFileBaseConfigFile",
    "ColColumnFloatBase",
    "ColColumnFloatBaseConfigNumeric",
    "ColColumnFloatBaseConfigNumericNumberFormat",
    "ColColumnIntegerBase",
    "ColColumnIntegerBaseConfigNumeric",
    "ColColumnIntegerBaseConfigNumericNumberFormat",
    "ColColumnReferenceBase",
    "ColColumnSelectBase",
    "ColColumnSelectBaseConfigSelect",
    "ColColumnTextBase",
    "ColColumnURLBase",
    "ColColumnUserBase",
    "ColColumnLookupBase",
    "ColColumnLookupBaseLookupExternalColumn",
    "ColColumnLookupBaseLookupExternalColumnColumnBooleanBase",
    "ColColumnLookupBaseLookupExternalColumnColumnDateBase",
    "ColColumnLookupBaseLookupExternalColumnColumnEditorBase",
    "ColColumnLookupBaseLookupExternalColumnColumnExpressionBase",
    "ColColumnLookupBaseLookupExternalColumnColumnFileBase",
    "ColColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile",
    "ColColumnLookupBaseLookupExternalColumnColumnFloatBase",
    "ColColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric",
    "ColColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat",
    "ColColumnLookupBaseLookupExternalColumnColumnIntegerBase",
    "ColColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric",
    "ColColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat",
    "ColColumnLookupBaseLookupExternalColumnColumnReferenceBase",
    "ColColumnLookupBaseLookupExternalColumnColumnSelectBase",
    "ColColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect",
    "ColColumnLookupBaseLookupExternalColumnColumnTextBase",
    "ColColumnLookupBaseLookupExternalColumnColumnURLBase",
    "ColColumnLookupBaseLookupExternalColumnColumnUserBase",
]


class ColColumnBooleanBase(BaseModel):
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


class ColColumnDateBase(BaseModel):
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


class ColColumnEditorBase(BaseModel):
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


class ColColumnExpressionBase(BaseModel):
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


class ColColumnFileBaseConfigFile(BaseModel):
    allowed_extensions: Optional[List[str]] = FieldInfo(alias="allowedExtensions", default=None)


class ColColumnFileBase(BaseModel):
    type: Literal["file"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_file: Optional[ColColumnFileBaseConfigFile] = FieldInfo(alias="configFile", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class ColColumnFloatBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class ColColumnFloatBaseConfigNumeric(BaseModel):
    number_format: Optional[ColColumnFloatBaseConfigNumericNumberFormat] = FieldInfo(alias="numberFormat", default=None)
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class ColColumnFloatBase(BaseModel):
    type: Literal["float"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[ColColumnFloatBaseConfigNumeric] = FieldInfo(alias="configNumeric", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class ColColumnIntegerBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class ColColumnIntegerBaseConfigNumeric(BaseModel):
    number_format: Optional[ColColumnIntegerBaseConfigNumericNumberFormat] = FieldInfo(
        alias="numberFormat", default=None
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class ColColumnIntegerBase(BaseModel):
    type: Literal["integer"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[ColColumnIntegerBaseConfigNumeric] = FieldInfo(alias="configNumeric", default=None)

    enabled_viewers: Optional[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]]
    ] = FieldInfo(alias="enabledViewers", default=None)

    inline_viewer: Optional[Literal["molecule2d"]] = FieldInfo(alias="inlineViewer", default=None)

    is_required: Optional[bool] = FieldInfo(alias="isRequired", default=None)

    json_field: Optional[str] = FieldInfo(alias="jsonField", default=None)

    name: Optional[str] = None

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    system_type: Optional[Literal["name", "bodyDocument"]] = FieldInfo(alias="systemType", default=None)


class ColColumnReferenceBase(BaseModel):
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


class ColColumnSelectBaseConfigSelect(BaseModel):
    options: List[str]

    can_create: Optional[bool] = FieldInfo(alias="canCreate", default=None)


class ColColumnSelectBase(BaseModel):
    config_select: ColColumnSelectBaseConfigSelect = FieldInfo(alias="configSelect")

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


class ColColumnTextBase(BaseModel):
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


class ColColumnURLBase(BaseModel):
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


class ColColumnUserBase(BaseModel):
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


class ColColumnLookupBaseLookupExternalColumnColumnBooleanBase(BaseModel):
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


class ColColumnLookupBaseLookupExternalColumnColumnDateBase(BaseModel):
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


class ColColumnLookupBaseLookupExternalColumnColumnEditorBase(BaseModel):
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


class ColColumnLookupBaseLookupExternalColumnColumnExpressionBase(BaseModel):
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


class ColColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile(BaseModel):
    allowed_extensions: Optional[List[str]] = FieldInfo(alias="allowedExtensions", default=None)


class ColColumnLookupBaseLookupExternalColumnColumnFileBase(BaseModel):
    type: Literal["file"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_file: Optional[ColColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile] = FieldInfo(
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


class ColColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class ColColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric(BaseModel):
    number_format: Optional[ColColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat] = (
        FieldInfo(alias="numberFormat", default=None)
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class ColColumnLookupBaseLookupExternalColumnColumnFloatBase(BaseModel):
    type: Literal["float"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[ColColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric] = FieldInfo(
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


class ColColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat(BaseModel):
    maximum_fraction_digits: Optional[float] = FieldInfo(alias="maximumFractionDigits", default=None)

    maximum_significant_digits: Optional[float] = FieldInfo(alias="maximumSignificantDigits", default=None)

    minimum_fraction_digits: Optional[float] = FieldInfo(alias="minimumFractionDigits", default=None)

    minimum_significant_digits: Optional[float] = FieldInfo(alias="minimumSignificantDigits", default=None)


class ColColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric(BaseModel):
    number_format: Optional[ColColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat] = (
        FieldInfo(alias="numberFormat", default=None)
    )
    """Options for formatting numbers, used only for display purposes."""

    unit: Optional[str] = None


class ColColumnLookupBaseLookupExternalColumnColumnIntegerBase(BaseModel):
    type: Literal["integer"]

    id: Optional[str] = None
    """Deep Origin system ID."""

    cardinality: Optional[Literal["one", "many"]] = None

    cell_json_schema: Optional[object] = FieldInfo(alias="cellJsonSchema", default=None)

    config_numeric: Optional[ColColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric] = FieldInfo(
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


class ColColumnLookupBaseLookupExternalColumnColumnReferenceBase(BaseModel):
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


class ColColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect(BaseModel):
    options: List[str]

    can_create: Optional[bool] = FieldInfo(alias="canCreate", default=None)


class ColColumnLookupBaseLookupExternalColumnColumnSelectBase(BaseModel):
    config_select: ColColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect = FieldInfo(alias="configSelect")

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


class ColColumnLookupBaseLookupExternalColumnColumnTextBase(BaseModel):
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


class ColColumnLookupBaseLookupExternalColumnColumnURLBase(BaseModel):
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


class ColColumnLookupBaseLookupExternalColumnColumnUserBase(BaseModel):
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


ColColumnLookupBaseLookupExternalColumn: TypeAlias = Union[
    ColColumnLookupBaseLookupExternalColumnColumnBooleanBase,
    ColColumnLookupBaseLookupExternalColumnColumnDateBase,
    ColColumnLookupBaseLookupExternalColumnColumnEditorBase,
    ColColumnLookupBaseLookupExternalColumnColumnExpressionBase,
    ColColumnLookupBaseLookupExternalColumnColumnFileBase,
    ColColumnLookupBaseLookupExternalColumnColumnFloatBase,
    ColColumnLookupBaseLookupExternalColumnColumnIntegerBase,
    ColColumnLookupBaseLookupExternalColumnColumnReferenceBase,
    ColColumnLookupBaseLookupExternalColumnColumnSelectBase,
    ColColumnLookupBaseLookupExternalColumnColumnTextBase,
    ColColumnLookupBaseLookupExternalColumnColumnURLBase,
    ColColumnLookupBaseLookupExternalColumnColumnUserBase,
]


class ColColumnLookupBase(BaseModel):
    lookup_external_column: ColColumnLookupBaseLookupExternalColumn = FieldInfo(alias="lookupExternalColumn")

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


Col: TypeAlias = Union[
    ColColumnBooleanBase,
    ColColumnDateBase,
    ColColumnEditorBase,
    ColColumnExpressionBase,
    ColColumnFileBase,
    ColColumnFloatBase,
    ColColumnIntegerBase,
    ColColumnReferenceBase,
    ColColumnSelectBase,
    ColColumnTextBase,
    ColColumnURLBase,
    ColColumnUserBase,
    ColColumnLookupBase,
]


class Database(BaseModel):
    id: str
    """Deep Origin system ID."""

    hid: str

    hid_prefix: str = FieldInfo(alias="hidPrefix")

    name: str

    type: Literal["database"]

    cols: Optional[List[Col]] = None

    created_by_user_drn: Optional[str] = FieldInfo(alias="createdByUserDrn", default=None)

    creation_block_id: Optional[str] = FieldInfo(alias="creationBlockId", default=None)

    creation_parent_id: Optional[str] = FieldInfo(alias="creationParentId", default=None)

    date_created: Optional[str] = FieldInfo(alias="dateCreated", default=None)

    date_updated: Optional[str] = FieldInfo(alias="dateUpdated", default=None)

    edited_by_user_drn: Optional[str] = FieldInfo(alias="editedByUserDrn", default=None)

    editor: Optional[object] = None

    is_inline_database: Optional[bool] = FieldInfo(alias="isInlineDatabase", default=None)

    is_locked: Optional[bool] = FieldInfo(alias="isLocked", default=None)

    parent_hid: Optional[str] = FieldInfo(alias="parentHid", default=None)

    parent_id: Optional[str] = FieldInfo(alias="parentId", default=None)

    row_json_schema: Optional[object] = FieldInfo(alias="rowJsonSchema", default=None)
