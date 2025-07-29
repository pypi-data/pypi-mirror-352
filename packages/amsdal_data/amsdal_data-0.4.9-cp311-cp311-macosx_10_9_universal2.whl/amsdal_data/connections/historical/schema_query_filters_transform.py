from copy import copy

import amsdal_glue as glue
from amsdal_glue_connections.sql.constants import SCHEMA_REGISTRY_TABLE
from amsdal_utils.models.enums import Versions

from amsdal_data.connections.constants import METADATA_TABLE
from amsdal_data.connections.constants import OBJECT_TABLE
from amsdal_data.connections.constants import REFERENCE_TABLE
from amsdal_data.connections.constants import SCHEMA_NAME_FIELD
from amsdal_data.connections.constants import SCHEMA_VERSION_FIELD
from amsdal_data.connections.constants import TRANSACTION_TABLE
from amsdal_data.connections.historical.command_builder import TABLE_NAME_VERSION_SEPARATOR
from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager
from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager


class BaseQueryFiltersTransform:
    def __init__(self, schema_query_filters: glue.Conditions | None) -> None:
        self.schema_query_filters = copy(schema_query_filters) if schema_query_filters else None

    @staticmethod
    def process_data(data: list[glue.Schema]) -> list[glue.Schema]:
        result = []

        for item in data:
            _item = copy(item)

            if TABLE_NAME_VERSION_SEPARATOR in item.name:
                _name, _version = _item.name.split(TABLE_NAME_VERSION_SEPARATOR)
                _item.name = _name
                _item.version = _version

            for constraint in _item.constraints or []:
                if isinstance(constraint, glue.PrimaryKeyConstraint):
                    _item.name, _ = _item.name.rsplit('_x_', 1) if '_x_' in _item.name else (_item.name, None)

            result.append(_item)

        return result

    @staticmethod
    def _transform_single_condition(condition: glue.Condition) -> glue.Conditions | glue.Condition:
        if not isinstance(condition.right, glue.Value):
            return condition

        if not isinstance(condition.left, glue.FieldReferenceExpression):
            return condition

        if condition.left.field_reference.field.name == SCHEMA_NAME_FIELD:
            value = condition.right

            if value.value in (
                TRANSACTION_TABLE,
                METADATA_TABLE,
                REFERENCE_TABLE,
                OBJECT_TABLE,
            ):
                value = copy(value)

            if condition.lookup == glue.FieldLookup.EQ:
                return glue.Conditions(
                    glue.Condition(
                        left=condition.left,
                        lookup=glue.FieldLookup.EQ,
                        negate=condition.negate,
                        right=value,
                    ),
                    glue.Condition(
                        left=condition.left,
                        lookup=glue.FieldLookup.STARTSWITH,
                        negate=condition.negate,
                        right=glue.Value(f'{value.value}{TABLE_NAME_VERSION_SEPARATOR}'),
                    ),
                    connector=glue.FilterConnector.OR,
                )

            return glue.Condition(
                left=condition.left,
                lookup=condition.lookup,
                negate=condition.negate,
                right=value,
            )

        if condition.left.field_reference.field.name == SCHEMA_VERSION_FIELD:
            if condition.lookup == glue.FieldLookup.EQ:
                return glue.Condition(
                    left=condition.left,
                    lookup=glue.FieldLookup.ENDSWITH,
                    negate=condition.negate,
                    right=glue.Value(f'{TABLE_NAME_VERSION_SEPARATOR}{condition.value.value}'),  # type: ignore[attr-defined]
                )
            return condition
        return condition


class SchemaQueryFiltersTransform(BaseQueryFiltersTransform):
    def __init__(self, schema_query_filters: glue.Conditions | None) -> None:
        super().__init__(schema_query_filters)
        self.schema_version_manager = HistoricalSchemaVersionManager()

    def transform(self) -> glue.Conditions | None:
        if not self.schema_query_filters:
            return self.schema_query_filters
        return self._transform(self.schema_query_filters)

    def _transform(self, item: glue.Conditions) -> glue.Conditions:
        _conditions: list[glue.Condition | glue.Conditions] = []
        _items = []

        for _condition in item.children:
            _condition = copy(_condition)

            if isinstance(_condition, glue.Conditions):
                _conditions.append(self._transform(_condition))
                continue

            if item.connector == glue.FilterConnector.OR:
                _conditions.append(self._transform_single_condition(_condition))
                continue

            if not isinstance(_condition.left, glue.FieldReferenceExpression):
                _conditions.append(self._transform_single_condition(_condition))
                continue

            if _condition.left.field_reference.field.name not in (SCHEMA_NAME_FIELD, SCHEMA_VERSION_FIELD):
                _conditions.append(_condition)
                continue

            _items.append(_condition)

        _conditions.extend(self._transform_multiple_conditions(_items))

        return glue.Conditions(
            *_conditions,
            connector=item.connector,
            negated=item.negated,
        )

    def _transform_multiple_conditions(self, items: list[glue.Condition]) -> list[glue.Condition]:
        if not items:
            return []

        if len(items) == 1:
            return [self._transform_single_condition(items[0])]  # type: ignore[list-item]

        if len(items) > 2:  # noqa: PLR2004
            msg = 'Only two conditions are supported'
            raise ValueError(msg)

        if not all(isinstance(condition.right, glue.Value) for condition in items):
            return items

        if not all(isinstance(condition.left, glue.FieldReferenceExpression) for condition in items):
            return items

        _name: glue.Condition = next(filter(lambda x: x.left.field_reference.field.name == SCHEMA_NAME_FIELD, items))  # type: ignore[arg-type, attr-defined]
        _version: glue.Condition = next(
            filter(lambda x: x.left.field_reference.field.name == SCHEMA_VERSION_FIELD, items)  # type: ignore[attr-defined, arg-type]
        )
        _version_value = _version.right.value  # type: ignore[attr-defined]

        if not _version_value:
            return [
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=SCHEMA_NAME_FIELD),
                            table_name=SCHEMA_REGISTRY_TABLE,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    negate=_name.negate,
                    right=glue.Value(_name.right.value),  # type: ignore[attr-defined]
                ),
            ]

        if _version_value in (
            glue.Version.LATEST,
            Versions.LATEST,
            'LATEST',
        ):
            class_version = self.schema_version_manager.get_latest_schema_version(
                _name.right.value  # type: ignore[attr-defined]
            )

            if not class_version:
                return [
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=SCHEMA_NAME_FIELD),
                                table_name=SCHEMA_REGISTRY_TABLE,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        negate=_name.negate,
                        right=glue.Value(_name.right.value),  # type: ignore[attr-defined]
                    ),
                ]

            if class_version in (
                glue.Version.LATEST,
                Versions.LATEST,
                'LATEST',
            ):
                return [
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=SCHEMA_NAME_FIELD),
                                table_name=SCHEMA_REGISTRY_TABLE,
                            ),
                        ),
                        lookup=glue.FieldLookup.STARTSWITH,
                        negate=_name.negate,
                        right=glue.Value(f'{_name.right.value}{TABLE_NAME_VERSION_SEPARATOR}'),  # type: ignore[attr-defined]
                    ),
                ]

            _version_value = class_version
        return [
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=SCHEMA_NAME_FIELD),
                        table_name=SCHEMA_REGISTRY_TABLE,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                negate=_name.negate,
                right=glue.Value(f'{_name.right.value}{TABLE_NAME_VERSION_SEPARATOR}{_version_value}'),  # type: ignore[attr-defined]
            ),
        ]


class AsyncSchemaQueryFiltersTransform(BaseQueryFiltersTransform):
    def __init__(self, schema_query_filters: glue.Conditions | None) -> None:
        super().__init__(schema_query_filters)
        self.schema_version_manager = AsyncHistoricalSchemaVersionManager()

    async def transform(self) -> glue.Conditions | None:
        if not self.schema_query_filters:
            return self.schema_query_filters
        return await self._transform(self.schema_query_filters)

    async def _transform(self, item: glue.Conditions) -> glue.Conditions:
        _conditions: list[glue.Condition | glue.Conditions] = []
        _items = []

        for _condition in item.children:
            _condition = copy(_condition)

            if isinstance(_condition, glue.Conditions):
                _conditions.append(await self._transform(_condition))
                continue

            if item.connector == glue.FilterConnector.OR:
                _conditions.append(self._transform_single_condition(_condition))
                continue

            if not isinstance(_condition.left, glue.FieldReferenceExpression):
                _conditions.append(self._transform_single_condition(_condition))
                continue

            if _condition.left.field_reference.field.name not in (SCHEMA_NAME_FIELD, SCHEMA_VERSION_FIELD):
                _conditions.append(_condition)
                continue

            _items.append(_condition)

        _conditions.extend(await self._transform_multiple_conditions(_items))

        return glue.Conditions(
            *_conditions,
            connector=item.connector,
            negated=item.negated,
        )

    async def _transform_multiple_conditions(self, items: list[glue.Condition]) -> list[glue.Condition]:
        if not items:
            return []

        if len(items) == 1:
            return [self._transform_single_condition(items[0])]  # type: ignore[list-item]

        if len(items) > 2:  # noqa: PLR2004
            msg = 'Only two conditions are supported'
            raise ValueError(msg)

        if not all(isinstance(condition.right, glue.Value) for condition in items):
            return items

        if not all(isinstance(condition.left, glue.FieldReferenceExpression) for condition in items):
            return items

        _name: glue.Condition = next(filter(lambda x: x.left.field_reference.field.name == SCHEMA_NAME_FIELD, items))  # type: ignore[arg-type, attr-defined]
        _version: glue.Condition = next(
            filter(lambda x: x.left.field_reference.field.name == SCHEMA_VERSION_FIELD, items)  # type: ignore[attr-defined, arg-type]
        )
        _version_value = _version.right.value  # type: ignore[attr-defined]

        if not _version_value:
            return [
                glue.Condition(
                    left=glue.FieldReferenceExpression(
                        field_reference=glue.FieldReference(
                            field=glue.Field(name=SCHEMA_NAME_FIELD),
                            table_name=SCHEMA_REGISTRY_TABLE,
                        ),
                    ),
                    lookup=glue.FieldLookup.EQ,
                    negate=_name.negate,
                    right=glue.Value(_name.right.value),  # type: ignore[attr-defined]
                ),
            ]

        if _version_value in (
            glue.Version.LATEST,
            Versions.LATEST,
            'LATEST',
        ):
            class_version = await self.schema_version_manager.get_latest_schema_version(
                _name.right.value  # type: ignore[attr-defined]
            )

            if not class_version:
                return [
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=SCHEMA_NAME_FIELD),
                                table_name=SCHEMA_REGISTRY_TABLE,
                            ),
                        ),
                        lookup=glue.FieldLookup.EQ,
                        negate=_name.negate,
                        right=glue.Value(_name.right.value),  # type: ignore[attr-defined]
                    ),
                ]

            if class_version in (
                glue.Version.LATEST,
                Versions.LATEST,
                'LATEST',
            ):
                return [
                    glue.Condition(
                        left=glue.FieldReferenceExpression(
                            field_reference=glue.FieldReference(
                                field=glue.Field(name=SCHEMA_NAME_FIELD),
                                table_name=SCHEMA_REGISTRY_TABLE,
                            ),
                        ),
                        lookup=glue.FieldLookup.STARTSWITH,
                        negate=_name.negate,
                        right=glue.Value(f'{_name.right.value}{TABLE_NAME_VERSION_SEPARATOR}'),  # type: ignore[attr-defined]
                    ),
                ]

            _version_value = class_version
        return [
            glue.Condition(
                left=glue.FieldReferenceExpression(
                    field_reference=glue.FieldReference(
                        field=glue.Field(name=SCHEMA_NAME_FIELD),
                        table_name=SCHEMA_REGISTRY_TABLE,
                    ),
                ),
                lookup=glue.FieldLookup.EQ,
                negate=_name.negate,
                right=glue.Value(f'{_name.right.value}{TABLE_NAME_VERSION_SEPARATOR}{_version_value}'),  # type: ignore[attr-defined]
            ),
        ]
