from typing import Any

import amsdal_glue as glue
from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
from amsdal_data.connections.historical.data_query_transform import METADATA_FIELD
from amsdal_data.connections.historical.data_query_transform import METADATA_TABLE_ALIAS
from amsdal_utils.query.enums import OrderDirection

from amsdal_models.classes.relationships.constants import FOREIGN_KEYS
from amsdal_models.classes.relationships.meta.references import build_fk_db_fields
from amsdal_models.querysets.query_builders.common import ModelType


def _field_shortcut(field_name: str) -> glue.Field:
    return glue.Field(name=field_name)


class BaseHistoricalQueryBuilder:
    @staticmethod
    def _fk_to_db_fields_for(model: type['ModelType']) -> dict[str, str]:
        fk_to_db_fields = {}
        fks = getattr(model, FOREIGN_KEYS, [])

        for fk in fks:
            field_info = model.model_fields[fk]
            _, db_fields, _ = build_fk_db_fields(fk, field_info)
            fk_to_db_fields.update(dict.fromkeys(db_fields, fk))

        return fk_to_db_fields

    def build_group_by(
        self,
        model: type['ModelType'],
        only: list[str] | None = None,
        select_related: dict[tuple[str, type['ModelType'], str], Any] | None = None,
        order_by: list[glue.OrderByQuery] | None = None,
    ) -> list[glue.GroupByQuery]:
        _group_by = [
            glue.GroupByQuery(
                field=glue.FieldReference(
                    field=self.build_field(pk_field),  # type: ignore[attr-defined]
                    table_name=self.build_table_name(model),  # type: ignore[attr-defined]
                ),
            )
            for pk_field in [PRIMARY_PARTITION_KEY, SECONDARY_PARTITION_KEY]
        ]

        for _only_field in only or []:
            normalized_item = self.normalize_primary_key(_only_field)  # type: ignore[attr-defined]

            if isinstance(normalized_item, list):
                # the field was specified as PK, skip we have already added them
                continue
            else:
                _group_by.extend(
                    [glue.GroupByQuery(field=_field) for _field in self._build_field_reference(normalized_item, model)]  # type: ignore[attr-defined]
                )

        if order_by:
            for _order_by in order_by:
                _group_by.append(glue.GroupByQuery(field=_order_by.field))

        if not select_related:
            return _group_by

        # process select_related
        for prop_name in model.model_fields:
            _group_by.extend(
                [glue.GroupByQuery(field=_field) for _field in self._build_field_reference(prop_name, model)]  # type: ignore[attr-defined]
            )

        _group_by.extend(
            [
                glue.GroupByQuery(
                    field=glue.FieldReference(
                        field=_field.field,
                        table_name=_field.table_name,
                    ),
                )
                for _field in self._build_nested_only(select_related)  # type: ignore[attr-defined]
            ]
        )

        return _group_by

    def build_order_by(self) -> list[glue.OrderByQuery] | None:
        if not self.qs_order_by:  # type: ignore[attr-defined]
            return None

        order_by = []
        fk_to_db_fields_map = self._fk_to_db_fields_for(self.qs_model)  # type: ignore[attr-defined]

        for item in self.qs_order_by:  # type: ignore[attr-defined]
            field_name = item.field_name

            if field_name in fk_to_db_fields_map:
                field_name = fk_to_db_fields_map[field_name]

            field = glue.FieldReference(
                field=self.build_field(field_name),  # type: ignore[attr-defined]
                table_name=self.qs_table_name,  # type: ignore[attr-defined]
            )

            if '__' in field_name:
                _field_name, _rest = field_name.split('__', 1)

                if _field_name == METADATA_FIELD:
                    field = glue.FieldReference(
                        field=self.build_field(_rest),  # type: ignore[attr-defined]
                        table_name=METADATA_TABLE_ALIAS,
                    )

            _order_by = glue.OrderByQuery(
                field=field,
                direction=(
                    {
                        OrderDirection.ASC: glue.OrderDirection.ASC,
                        OrderDirection.DESC: glue.OrderDirection.DESC,
                    }
                )[item.direction],
            )

            if _order_by not in order_by:
                order_by.append(_order_by)

        return order_by
