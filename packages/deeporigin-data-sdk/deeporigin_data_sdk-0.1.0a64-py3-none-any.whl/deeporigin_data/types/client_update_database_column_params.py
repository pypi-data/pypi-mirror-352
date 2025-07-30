# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "ClientUpdateDatabaseColumnParams",
    "Column",
    "ColumnColumnBooleanBase",
    "ColumnColumnDateBase",
    "ColumnColumnEditorBase",
    "ColumnColumnExpressionBase",
    "ColumnColumnFileBase",
    "ColumnColumnFileBaseConfigFile",
    "ColumnColumnFloatBase",
    "ColumnColumnFloatBaseConfigNumeric",
    "ColumnColumnFloatBaseConfigNumericNumberFormat",
    "ColumnColumnIntegerBase",
    "ColumnColumnIntegerBaseConfigNumeric",
    "ColumnColumnIntegerBaseConfigNumericNumberFormat",
    "ColumnColumnReferenceBase",
    "ColumnColumnSelectBase",
    "ColumnColumnSelectBaseConfigSelect",
    "ColumnColumnTextBase",
    "ColumnColumnURLBase",
    "ColumnColumnUserBase",
    "ColumnColumnLookupBase",
    "ColumnColumnLookupBaseLookupExternalColumn",
    "ColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase",
    "ColumnColumnLookupBaseLookupExternalColumnColumnDateBase",
    "ColumnColumnLookupBaseLookupExternalColumnColumnEditorBase",
    "ColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase",
    "ColumnColumnLookupBaseLookupExternalColumnColumnFileBase",
    "ColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile",
    "ColumnColumnLookupBaseLookupExternalColumnColumnFloatBase",
    "ColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric",
    "ColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat",
    "ColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase",
    "ColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric",
    "ColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat",
    "ColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase",
    "ColumnColumnLookupBaseLookupExternalColumnColumnSelectBase",
    "ColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect",
    "ColumnColumnLookupBaseLookupExternalColumnColumnTextBase",
    "ColumnColumnLookupBaseLookupExternalColumnColumnURLBase",
    "ColumnColumnLookupBaseLookupExternalColumnColumnUserBase",
]


class ClientUpdateDatabaseColumnParams(TypedDict, total=False):
    column: Required[Column]

    column_id: Required[Annotated[str, PropertyInfo(alias="columnId")]]

    database_id: Required[Annotated[str, PropertyInfo(alias="databaseId")]]


class ColumnColumnBooleanBase(TypedDict, total=False):
    type: Required[Literal["boolean"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnDateBase(TypedDict, total=False):
    type: Required[Literal["date"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnEditorBase(TypedDict, total=False):
    type: Required[Literal["editor"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnExpressionBase(TypedDict, total=False):
    expression_code: Required[Annotated[str, PropertyInfo(alias="expressionCode")]]

    expression_return_type: Required[
        Annotated[Literal["text", "float", "integer"], PropertyInfo(alias="expressionReturnType")]
    ]

    type: Required[Literal["expression"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnFileBaseConfigFile(TypedDict, total=False):
    allowed_extensions: Annotated[List[str], PropertyInfo(alias="allowedExtensions")]


class ColumnColumnFileBase(TypedDict, total=False):
    type: Required[Literal["file"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    config_file: Annotated[ColumnColumnFileBaseConfigFile, PropertyInfo(alias="configFile")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnFloatBaseConfigNumericNumberFormat(TypedDict, total=False):
    maximum_fraction_digits: Annotated[float, PropertyInfo(alias="maximumFractionDigits")]

    maximum_significant_digits: Annotated[float, PropertyInfo(alias="maximumSignificantDigits")]

    minimum_fraction_digits: Annotated[float, PropertyInfo(alias="minimumFractionDigits")]

    minimum_significant_digits: Annotated[float, PropertyInfo(alias="minimumSignificantDigits")]


class ColumnColumnFloatBaseConfigNumeric(TypedDict, total=False):
    number_format: Annotated[ColumnColumnFloatBaseConfigNumericNumberFormat, PropertyInfo(alias="numberFormat")]
    """Options for formatting numbers, used only for display purposes."""

    unit: str


class ColumnColumnFloatBase(TypedDict, total=False):
    type: Required[Literal["float"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    config_numeric: Annotated[ColumnColumnFloatBaseConfigNumeric, PropertyInfo(alias="configNumeric")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnIntegerBaseConfigNumericNumberFormat(TypedDict, total=False):
    maximum_fraction_digits: Annotated[float, PropertyInfo(alias="maximumFractionDigits")]

    maximum_significant_digits: Annotated[float, PropertyInfo(alias="maximumSignificantDigits")]

    minimum_fraction_digits: Annotated[float, PropertyInfo(alias="minimumFractionDigits")]

    minimum_significant_digits: Annotated[float, PropertyInfo(alias="minimumSignificantDigits")]


class ColumnColumnIntegerBaseConfigNumeric(TypedDict, total=False):
    number_format: Annotated[ColumnColumnIntegerBaseConfigNumericNumberFormat, PropertyInfo(alias="numberFormat")]
    """Options for formatting numbers, used only for display purposes."""

    unit: str


class ColumnColumnIntegerBase(TypedDict, total=False):
    type: Required[Literal["integer"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    config_numeric: Annotated[ColumnColumnIntegerBaseConfigNumeric, PropertyInfo(alias="configNumeric")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnReferenceBase(TypedDict, total=False):
    reference_database_row_id: Required[Annotated[str, PropertyInfo(alias="referenceDatabaseRowId")]]

    type: Required[Literal["reference"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnSelectBaseConfigSelect(TypedDict, total=False):
    options: Required[List[str]]

    can_create: Annotated[bool, PropertyInfo(alias="canCreate")]


class ColumnColumnSelectBase(TypedDict, total=False):
    config_select: Required[Annotated[ColumnColumnSelectBaseConfigSelect, PropertyInfo(alias="configSelect")]]

    type: Required[Literal["select"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnTextBase(TypedDict, total=False):
    type: Required[Literal["text"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnURLBase(TypedDict, total=False):
    type: Required[Literal["url"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnUserBase(TypedDict, total=False):
    type: Required[Literal["user"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase(TypedDict, total=False):
    type: Required[Literal["boolean"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnDateBase(TypedDict, total=False):
    type: Required[Literal["date"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnEditorBase(TypedDict, total=False):
    type: Required[Literal["editor"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase(TypedDict, total=False):
    expression_code: Required[Annotated[str, PropertyInfo(alias="expressionCode")]]

    expression_return_type: Required[
        Annotated[Literal["text", "float", "integer"], PropertyInfo(alias="expressionReturnType")]
    ]

    type: Required[Literal["expression"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile(TypedDict, total=False):
    allowed_extensions: Annotated[List[str], PropertyInfo(alias="allowedExtensions")]


class ColumnColumnLookupBaseLookupExternalColumnColumnFileBase(TypedDict, total=False):
    type: Required[Literal["file"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    config_file: Annotated[
        ColumnColumnLookupBaseLookupExternalColumnColumnFileBaseConfigFile, PropertyInfo(alias="configFile")
    ]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat(TypedDict, total=False):
    maximum_fraction_digits: Annotated[float, PropertyInfo(alias="maximumFractionDigits")]

    maximum_significant_digits: Annotated[float, PropertyInfo(alias="maximumSignificantDigits")]

    minimum_fraction_digits: Annotated[float, PropertyInfo(alias="minimumFractionDigits")]

    minimum_significant_digits: Annotated[float, PropertyInfo(alias="minimumSignificantDigits")]


class ColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric(TypedDict, total=False):
    number_format: Annotated[
        ColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumericNumberFormat,
        PropertyInfo(alias="numberFormat"),
    ]
    """Options for formatting numbers, used only for display purposes."""

    unit: str


class ColumnColumnLookupBaseLookupExternalColumnColumnFloatBase(TypedDict, total=False):
    type: Required[Literal["float"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    config_numeric: Annotated[
        ColumnColumnLookupBaseLookupExternalColumnColumnFloatBaseConfigNumeric, PropertyInfo(alias="configNumeric")
    ]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat(TypedDict, total=False):
    maximum_fraction_digits: Annotated[float, PropertyInfo(alias="maximumFractionDigits")]

    maximum_significant_digits: Annotated[float, PropertyInfo(alias="maximumSignificantDigits")]

    minimum_fraction_digits: Annotated[float, PropertyInfo(alias="minimumFractionDigits")]

    minimum_significant_digits: Annotated[float, PropertyInfo(alias="minimumSignificantDigits")]


class ColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric(TypedDict, total=False):
    number_format: Annotated[
        ColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumericNumberFormat,
        PropertyInfo(alias="numberFormat"),
    ]
    """Options for formatting numbers, used only for display purposes."""

    unit: str


class ColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase(TypedDict, total=False):
    type: Required[Literal["integer"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    config_numeric: Annotated[
        ColumnColumnLookupBaseLookupExternalColumnColumnIntegerBaseConfigNumeric, PropertyInfo(alias="configNumeric")
    ]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase(TypedDict, total=False):
    reference_database_row_id: Required[Annotated[str, PropertyInfo(alias="referenceDatabaseRowId")]]

    type: Required[Literal["reference"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect(TypedDict, total=False):
    options: Required[List[str]]

    can_create: Annotated[bool, PropertyInfo(alias="canCreate")]


class ColumnColumnLookupBaseLookupExternalColumnColumnSelectBase(TypedDict, total=False):
    config_select: Required[
        Annotated[
            ColumnColumnLookupBaseLookupExternalColumnColumnSelectBaseConfigSelect, PropertyInfo(alias="configSelect")
        ]
    ]

    type: Required[Literal["select"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnTextBase(TypedDict, total=False):
    type: Required[Literal["text"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnURLBase(TypedDict, total=False):
    type: Required[Literal["url"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


class ColumnColumnLookupBaseLookupExternalColumnColumnUserBase(TypedDict, total=False):
    type: Required[Literal["user"]]

    id: str
    """Deep Origin system ID."""

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


ColumnColumnLookupBaseLookupExternalColumn: TypeAlias = Union[
    ColumnColumnLookupBaseLookupExternalColumnColumnBooleanBase,
    ColumnColumnLookupBaseLookupExternalColumnColumnDateBase,
    ColumnColumnLookupBaseLookupExternalColumnColumnEditorBase,
    ColumnColumnLookupBaseLookupExternalColumnColumnExpressionBase,
    ColumnColumnLookupBaseLookupExternalColumnColumnFileBase,
    ColumnColumnLookupBaseLookupExternalColumnColumnFloatBase,
    ColumnColumnLookupBaseLookupExternalColumnColumnIntegerBase,
    ColumnColumnLookupBaseLookupExternalColumnColumnReferenceBase,
    ColumnColumnLookupBaseLookupExternalColumnColumnSelectBase,
    ColumnColumnLookupBaseLookupExternalColumnColumnTextBase,
    ColumnColumnLookupBaseLookupExternalColumnColumnURLBase,
    ColumnColumnLookupBaseLookupExternalColumnColumnUserBase,
]


class ColumnColumnLookupBase(TypedDict, total=False):
    lookup_external_column: Required[
        Annotated[ColumnColumnLookupBaseLookupExternalColumn, PropertyInfo(alias="lookupExternalColumn")]
    ]

    lookup_external_column_id: Required[Annotated[str, PropertyInfo(alias="lookupExternalColumnId")]]

    lookup_source_column_id: Required[Annotated[str, PropertyInfo(alias="lookupSourceColumnId")]]

    type: Required[Literal["lookup"]]

    cardinality: Literal["one", "many"]

    cell_json_schema: Annotated[object, PropertyInfo(alias="cellJsonSchema")]

    enabled_viewers: Annotated[
        List[Literal["code", "html", "image", "molecule", "notebook", "sequence", "smiles", "spreadsheet"]],
        PropertyInfo(alias="enabledViewers"),
    ]

    inline_viewer: Annotated[Literal["molecule2d"], PropertyInfo(alias="inlineViewer")]

    is_required: Annotated[bool, PropertyInfo(alias="isRequired")]

    json_field: Annotated[str, PropertyInfo(alias="jsonField")]

    name: str

    system_type: Annotated[Literal["name", "bodyDocument"], PropertyInfo(alias="systemType")]


Column: TypeAlias = Union[
    ColumnColumnBooleanBase,
    ColumnColumnDateBase,
    ColumnColumnEditorBase,
    ColumnColumnExpressionBase,
    ColumnColumnFileBase,
    ColumnColumnFloatBase,
    ColumnColumnIntegerBase,
    ColumnColumnReferenceBase,
    ColumnColumnSelectBase,
    ColumnColumnTextBase,
    ColumnColumnURLBase,
    ColumnColumnUserBase,
    ColumnColumnLookupBase,
]
