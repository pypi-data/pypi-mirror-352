import hashlib
from datetime import date
from datetime import datetime
from typing import Any

import amsdal_glue as glue
from amsdal_glue_core.common.interfaces.connection import AsyncConnectionBase
from amsdal_glue_core.common.interfaces.connection import ConnectionBase
from amsdal_utils.config.data_models.repository_config import RepositoryConfig
from amsdal_utils.models.data_models.core import TypeData
from amsdal_utils.models.data_models.enums import CoreTypes
from amsdal_utils.schemas.schema import ObjectSchema
from amsdal_utils.utils.classes import import_class
from amsdal_utils.utils.singleton import Singleton

from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
from amsdal_data.connections.db_alias_map import CONNECTION_BACKEND_ALIASES
from amsdal_data.connections.historical.data_query_transform import META_PRIMARY_KEY_FIELDS

TABLE_NAME_PROPERTY = 'table_name'
PRIMARY_KEY_PROPERTY = 'primary_key'
FOREIGN_KEYS_PROPERTY = 'foreign_keys'
UNIQUE_PROPERTY = 'unique'
INDEXED_PROPERTY = 'indexed'


class SchemaManagerBase:
    pass


class SchemaManagerHandler(metaclass=Singleton):
    def __init__(self) -> None:
        self._schema_manager: SchemaManagerBase | None = None

    def set_schema_manager(self, schema_manager: SchemaManagerBase) -> None:
        self._schema_manager = schema_manager

    def get_schema_manager(self) -> SchemaManagerBase:
        if self._schema_manager is None:
            msg = 'Schema manager is not set.'
            raise ValueError(msg)
        return self._schema_manager


def resolve_backend_class(backend: str) -> type[ConnectionBase | AsyncConnectionBase]:
    if backend in CONNECTION_BACKEND_ALIASES:
        backend = CONNECTION_BACKEND_ALIASES[backend]

    return import_class(backend)


def get_schemas_for_connection_name(connection_name: str, repository_config: RepositoryConfig) -> list[str | None]:
    if connection_name == repository_config.default:
        return [None]

    return [
        _schema_name
        for _schema_name, _connection_name in repository_config.models.items()
        if _connection_name == connection_name
    ]


def object_schema_to_glue_schema(
    object_schema: ObjectSchema,
    *,
    is_lakehouse_only: bool = False,
    use_foreign_keys: bool = False,
    schema_names: list[str] | None = None,
) -> glue.Schema:
    from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY

    table_name = getattr(object_schema, TABLE_NAME_PROPERTY, None) or object_schema.title
    pk_fields: list[str] = getattr(object_schema, PRIMARY_KEY_PROPERTY, None) or [PRIMARY_PARTITION_KEY]
    pk_db_fields: dict[str, list[str]] = {pk: _list_normalize(object_schema, pk) for pk in pk_fields}
    properties = []
    schema_metadata: dict[str, Any] = {
        META_PRIMARY_KEY_FIELDS: pk_db_fields,
    }

    if pk_fields == [PRIMARY_PARTITION_KEY]:
        properties.append(
            glue.PropertySchema(
                name=PRIMARY_PARTITION_KEY,
                type=str,
                required=True,
            ),
        )

    _pk_constraint = glue.PrimaryKeyConstraint(
        name=f'pk_{table_name.lower()}',
        fields=[pk for db_fields in pk_db_fields.values() for pk in db_fields],
    )
    _schema = glue.Schema(
        name=table_name,
        version=glue.Version.LATEST,
        properties=properties,
        constraints=[
            _pk_constraint,
        ],
        indexes=[],
    )

    if is_lakehouse_only:
        _schema.properties.append(
            glue.PropertySchema(
                name=SECONDARY_PARTITION_KEY,
                type=str,
                required=True,
            ),
        )
        _pk_constraint.fields.append(SECONDARY_PARTITION_KEY)

    _fks = getattr(object_schema, FOREIGN_KEYS_PROPERTY, {})

    for _, property_data in (object_schema.properties or {}).items():
        _is_property_required = property_data.field_name in object_schema.required

        if is_reference_type(property_data.type) and use_foreign_keys and property_data.field_name in _fks:
            _db_fields, _fk_table_name, _ref_pks = _fks[property_data.field_name]

            for _db_field, _db_internal_type in _db_fields.items():
                _db_type = CoreTypes.to_python_type(_db_internal_type)
                _property = glue.PropertySchema(
                    name=_db_field,
                    type=_db_type,
                    required=_is_property_required,
                )
                _schema.properties.append(_property)

            __field_value = hashlib.md5((property_data.field_name or '').encode()).hexdigest()  # noqa: S324
            _fk_name = f'fk_{object_schema.title}_{__field_value}'.lower()
            if not _schema.constraints:
                _schema.constraints = []

            _schema.constraints.append(
                glue.ForeignKeyConstraint(
                    name=_fk_name,
                    fields=list(_db_fields.keys()),
                    reference_schema=glue.SchemaReference(
                        name=_fk_table_name,
                        version=glue.Version.LATEST,
                    ),
                    reference_fields=_ref_pks,
                ),
            )
            schema_metadata.setdefault(FOREIGN_KEYS_PROPERTY, {})[_fk_name] = property_data.field_name
        elif (
            property_data.type == CoreTypes.ARRAY.value
            and isinstance(property_data.items, TypeData)
            and is_reference_type(property_data.items.type)
            and use_foreign_keys
            and (not schema_names or property_data.items.type in schema_names)
        ):
            continue
        else:
            _type = property_data.type
            # this is probably a enum, we do not want it to be JSON
            if property_data.options and is_reference_type(property_data.type):
                if all(isinstance(option.value, str) for option in property_data.options):
                    _type = CoreTypes.STRING.value
                elif all(isinstance(option.value, int) for option in property_data.options):
                    _type = CoreTypes.INTEGER.value

            _property = glue.PropertySchema(
                name=property_data.field_name or '',
                type=object_schema_type_to_glue_type(_type),
                required=_is_property_required,
                default=property_data.default,
                description=property_data.title,
            )
            _schema.properties.append(_property)

    for unique_fields in getattr(object_schema, UNIQUE_PROPERTY, []) or []:
        if not _schema.constraints:
            _schema.constraints = []

        db_unique_fields = []

        if use_foreign_keys:
            for _field in unique_fields:
                if _field in _fks:
                    _db_fields, _fk_table_name, _ref_pks = _fks[_field]
                    db_unique_fields.extend(_db_fields.keys())
                else:
                    db_unique_fields.append(_field)
        else:
            db_unique_fields = unique_fields

        _schema.constraints.append(
            glue.UniqueConstraint(
                fields=db_unique_fields,
                name=f'unq_{object_schema.title.lower()}_{"_".join(db_unique_fields)}',
            ),
        )

    for indexed_field in getattr(object_schema, INDEXED_PROPERTY, []) or []:
        if not _schema.indexes:
            _schema.indexes = []

        db_indexed_fields = []

        if use_foreign_keys and indexed_field in _fks:
            _db_fields, _fk_table_name, _ref_pks = _fks[_field]
            db_indexed_fields.extend(_db_fields.keys())
        else:
            db_indexed_fields = [indexed_field]

        _schema.indexes.append(
            glue.IndexSchema(
                fields=db_indexed_fields,
                name=f'idx_{object_schema.title.lower()}_{"_".join(db_indexed_fields)}',
            ),
        )

    if schema_metadata:
        _schema.metadata = schema_metadata

    return _schema


def object_schema_type_to_glue_type(property_type: str) -> glue.Schema | glue.SchemaReference | type[Any]:
    if property_type == CoreTypes.ANYTHING.value:
        return dict

    if property_type == CoreTypes.NUMBER.value:
        return float

    if property_type == CoreTypes.INTEGER.value:
        return int

    if property_type == CoreTypes.BOOLEAN.value:
        return bool

    if property_type == CoreTypes.STRING.value:
        return str

    if property_type == CoreTypes.DATE.value:
        return date

    if property_type == CoreTypes.DATETIME.value:
        return datetime

    if property_type == CoreTypes.BINARY.value:
        return bytes

    if property_type == CoreTypes.ARRAY.value:
        return list

    if property_type == CoreTypes.DICTIONARY.value:
        return dict

    if is_reference_type(property_type):
        return dict
    return str


def is_reference_type(property_type: str) -> bool:
    return property_type[0] == property_type[0].upper()


def _list_normalize(object_schema: ObjectSchema, pk: str) -> list[str]:
    if pk == PRIMARY_PARTITION_KEY:
        return [pk]

    _properties = object_schema.properties or {}
    if pk not in _properties:
        try:
            prop = next(prop for prop in _properties.values() if prop.field_name == pk)
        except StopIteration:
            return [pk]

        value = prop.db_field
    else:
        value = _properties[pk].db_field

    if not value:
        return [pk]

    if isinstance(value, str):
        return [value]
    return value
