import json
from typing import Any

import amsdal_glue as glue
from amsdal_data.connections.constants import METADATA_KEY
from amsdal_data.connections.constants import PRIMARY_PARTITION_KEY
from amsdal_data.connections.constants import SECONDARY_PARTITION_KEY
from amsdal_data.connections.historical.data_query_transform import METADATA_FIELD
from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager
from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager
from amsdal_data.services.table_schema_manager import AsyncTableSchemasManager
from amsdal_data.services.table_schema_manager import TableSchemasManager
from amsdal_data.transactions.manager import AmsdalAsyncTransactionManager
from amsdal_data.transactions.manager import AmsdalTransactionManager
from amsdal_data.utils import object_schema_to_glue_schema
from amsdal_utils.models.data_models.enums import BaseClasses
from amsdal_utils.models.data_models.enums import MetaClasses
from amsdal_utils.models.enums import ModuleType
from amsdal_utils.models.enums import Versions
from amsdal_utils.schemas.schema import ObjectSchema
from amsdal_utils.schemas.schema import PropertyData
from pydantic import TypeAdapter
from pydantic import ValidationError

from amsdal_models.classes.glue_utils import model_to_data
from amsdal_models.classes.helpers.reference_loader import ReferenceLoader
from amsdal_models.classes.model import Model
from amsdal_models.errors import MigrationsError
from amsdal_models.migration.base_migration_schemas import BaseMigrationSchemas
from amsdal_models.migration.data_classes import Action
from amsdal_models.migration.executors.base import AsyncBaseMigrationExecutor
from amsdal_models.migration.executors.base import BaseMigrationExecutor
from amsdal_models.querysets.executor import LAKEHOUSE_DB_ALIAS


class DefaultMigrationExecutor(BaseMigrationExecutor):
    """
    Default implementation of the BaseMigrationExecutor for handling database schema migrations.

    This class provides concrete implementations for creating, updating, and deleting classes
    in the database schema. It also manages schema migration buffers and processes object schemas.
    """

    def __init__(self, schemas: BaseMigrationSchemas, *, use_foreign_keys: bool = True) -> None:
        self.schemas = schemas
        self._table_schemas_manager = TableSchemasManager()
        self._use_foreign_keys = use_foreign_keys

        super().__init__()

    def create_class(
        self,
        schemas: BaseMigrationSchemas,  # noqa: ARG002
        class_name: str,
        object_schema: ObjectSchema,
        module_type: ModuleType,
    ) -> None:
        """
        Creates a class in the database schema.

        This method registers a new class version if the schema type is `TYPE` and the class name
            is not `BaseClasses.OBJECT`.
        Otherwise, it buffers the class migration operation for further processing.

        Args:
            schemas (BaseMigrationSchemas): The migration schemas used for the operations.
            class_name (str): The name of the class to be created.
            object_schema (ObjectSchema): The schema of the object to be created.
            module_type (ModuleType): The type of the schema.

        Returns:
            None
        """
        if module_type == ModuleType.TYPE:
            self.schemas.register_model_version(
                class_name=class_name,
                class_version='',
            )

            if class_name != BaseClasses.OBJECT:
                return

        self.buffer_class_migration(
            class_name,
            object_schema,
            module_type,
        )

    def update_class(
        self,
        schemas: BaseMigrationSchemas,  # noqa: ARG002
        class_name: str,
        object_schema: ObjectSchema,
        module_type: ModuleType,
    ) -> None:
        """
        Buffers the class update operation.

        This method appends the given class name, object schema, and schema type to both
        the non-flushable buffer and the main buffer for further processing.

        Args:
            schemas (BaseMigrationSchemas): The migration schemas used for the operations.
            class_name (str): The name of the class to be updated.
            object_schema (ObjectSchema): The current object schema.
            module_type (ModuleType): The type of the schema.

        Returns:
            None
        """
        self.buffer_class_migration(
            class_name,
            object_schema,
            module_type,
        )

    def delete_class(
        self,
        schemas: BaseMigrationSchemas,
        class_name: str,
        module_type: ModuleType,  # noqa: ARG002
    ) -> None:
        """
        Deletes a class from the database schema.

        This method removes the specified class from the database schema and unregisters it from the migration schemas.

        Args:
            schemas (BaseMigrationSchemas): The migration schemas used for the operations.
            class_name (str): The name of the class to be deleted.
            module_type (ModuleType): The type of the schema.

        Returns:
            None
        """
        base_class_name = self._resolve_base_class_name(class_name, meta_class=MetaClasses.CLASS_OBJECT)

        self._table_schemas_manager.delete_class_object_schema(
            schema_reference=glue.SchemaReference(
                name=base_class_name,
                version=Versions.LATEST,
            ),
            class_object_id=class_name,
        )
        schemas.unregister_model(class_name)

    def flush_buffer(self) -> None:
        """
        Flushes the migration buffer and processes the buffered classes.

        This method registers the buffered classes in the migration schemas, compiles the buffered classes,
        and processes each class in the buffer to create tables, save class objects, and migrate historical data.
        Finally, it clears the main migration buffer.

        Returns:
            None
        """
        for class_name, object_schema, module_type in self._buffer:
            self.schemas.register_model(
                class_name=class_name,
                object_schema=object_schema,
                module_type=module_type,
                class_version='' if class_name == BaseClasses.OBJECT else Versions.LATEST,
            )

        self.schemas.compile_buffered_classes()

        for class_name, object_schema, module_type in self._buffer:
            _properties = object_schema.properties or {}
            for prop_name, prop in _properties.items():
                prop.field_name = prop_name
                prop.field_id = prop_name

            if class_name == BaseClasses.OBJECT:
                self._create_table(
                    object_schema,
                    class_version='',
                    using=LAKEHOUSE_DB_ALIAS,
                )
                continue

            is_meta_class_object = object_schema.meta_class == MetaClasses.CLASS_OBJECT
            base_class_name = self._resolve_base_class_name(class_name, meta_class=object_schema.meta_class)
            schema_reference = glue.SchemaReference(
                name=base_class_name,
                version='' if base_class_name == BaseClasses.OBJECT.value else Versions.LATEST,
            )
            base_class = self.schemas.get_model(base_class_name)

            action: Action = self._check_class(
                schema_reference=schema_reference,
                object_schema=object_schema,
                base_class=base_class,
            )

            if is_meta_class_object and action in (Action.CREATE, Action.UPDATE):
                _, _is_updated = self._create_table(
                    object_schema,
                    Versions.LATEST,
                    using=(
                        LAKEHOUSE_DB_ALIAS
                        if object_schema.title
                        in (
                            BaseClasses.CLASS_OBJECT,
                            BaseClasses.CLASS_OBJECT_META,
                        )
                        else None
                    ),
                )

                if action == Action.UPDATE and not _is_updated:
                    msg = f'Table for {object_schema.title} was not updated. Changes were not detected.'
                    raise RuntimeError(msg)

            if action != Action.NO_ACTION:
                saved_data = self._save_class(
                    schema_reference=schema_reference,
                    base_class=base_class,
                    object_schema=object_schema,
                    action=action,
                )

                # TODO: is it for meta type classes?
                if base_class.__name__ == BaseClasses.OBJECT:
                    HistoricalSchemaVersionManager().register_object_class(saved_data)

            if base_class_name == BaseClasses.CLASS_OBJECT:
                base_meta_class = self.schemas.get_model(BaseClasses.CLASS_OBJECT_META.value)

                # Just save new class object meta schema
                self._save_object_class_meta(
                    base_class=base_meta_class,
                    object_schema=object_schema,
                    module_type=module_type.value,
                )

            if is_meta_class_object and action == Action.UPDATE:
                self._migrate_historical_data(
                    self.schemas,
                    class_name,
                    prior_version=saved_data[METADATA_FIELD]['prior_version'],
                    new_version=saved_data[METADATA_FIELD]['object_version'],
                )

        super().flush_buffer()

    def _check_class(
        self,
        schema_reference: glue.SchemaReference,
        object_schema: ObjectSchema,
        base_class: type[Model],
    ) -> Action:
        data: dict[str, Any] | None = self._table_schemas_manager.search_latest_class_object(
            schema_reference=schema_reference,
            class_object_name=object_schema.title,
        )

        if not data:
            return Action.CREATE

        latest_class_object = base_class(**data)
        schema_dump = base_class(**object_schema.model_dump()).model_dump()
        new_class_schema = json.dumps(schema_dump, default=str, sort_keys=True)
        existing_class_schema = json.dumps(latest_class_object.model_dump(), default=str, sort_keys=True)

        if new_class_schema == existing_class_schema:
            return Action.NO_ACTION
        return Action.UPDATE

    def _save_class(
        self,
        schema_reference: glue.SchemaReference,
        base_class: type[Model],
        object_schema: ObjectSchema,
        action: Action,
    ) -> dict[str, Any]:
        class_object = base_class(
            **object_schema.model_dump(),
            _object_id=object_schema.title,
        )
        class_object_data = model_to_data(class_object)

        if action == Action.CREATE:
            return self._table_schemas_manager.insert_class_object_schema(
                schema_reference=schema_reference,
                class_object_data=class_object_data,
            )
        else:
            return self._table_schemas_manager.update_class_object_schema(
                schema_reference=schema_reference,
                class_object_data=class_object_data,
            )

    def _save_object_class_meta(
        self,
        base_class: type[Model],
        object_schema: ObjectSchema,
        module_type: str,
    ) -> None:
        schema_reference = glue.SchemaReference(
            name=BaseClasses.CLASS_OBJECT_META.value,
            version=glue.Version.LATEST,
        )
        action = self._check_class(schema_reference, object_schema, base_class)
        object_schema.class_schema_type = module_type  # type: ignore[attr-defined]
        self._save_class(schema_reference, base_class, object_schema, action)

    def _create_table(
        self,
        object_schema: ObjectSchema,
        class_version: str | Versions,
        using: str | None = None,
    ) -> tuple[bool, bool]:
        from amsdal_data.application import DataApplication

        is_lakehouse_only = using == LAKEHOUSE_DB_ALIAS or DataApplication().is_lakehouse_only
        schema = object_schema_to_glue_schema(
            object_schema,
            is_lakehouse_only=is_lakehouse_only,
            use_foreign_keys=self._use_foreign_keys,
            schema_names=self.schemas.registered_model_names(),
        )
        schema.version = class_version

        return self._table_schemas_manager.register_table(
            schema,
            using=using,
        )

    def _migrate_historical_data(
        self,
        schemas: BaseMigrationSchemas,
        class_name: str,
        prior_version: str,
        new_version: str,
    ) -> None:
        from amsdal_data.application import DataApplication

        if class_name in (BaseClasses.OBJECT, BaseClasses.CLASS_OBJECT):
            msg = 'Migrations for Object and ClassObject classes are not supported for now.'
            raise NotImplementedError(msg)

        schema_version_manager = HistoricalSchemaVersionManager()
        operation_manager = DataApplication().operation_manager
        migrated_class = schemas.get_model(class_name)
        mutations = []

        old_schema_reference = glue.SchemaReference(
            name=class_name,
            version=prior_version,
        )
        new_schema_reference = glue.SchemaReference(
            name=class_name,
            version=new_version,
        )

        for old_data in self._table_schemas_manager.fetch_historical_data(old_schema_reference):
            _data = self._clean_data(migrated_class, old_data)
            model_data: glue.Data = model_to_data(migrated_class(**_data))
            model_data.data[METADATA_KEY] = old_data[METADATA_KEY]

            # adjust class versions in metadata
            _class_schema_ref = model_data.data[METADATA_KEY]['class_schema_reference']['ref']
            _class_schema_ref['class_version'] = schema_version_manager.get_latest_schema_version(
                _class_schema_ref['class_name'],
            )
            _class_schema_ref['object_version'] = schema_version_manager.get_latest_schema_version(
                _class_schema_ref['object_id'],
            )

            _meta_class_schema = model_data.data[METADATA_KEY]['class_meta_schema_reference']

            if _meta_class_schema:
                _meta_class_schema_ref = _meta_class_schema['ref']
                _meta_class_schema_ref['class_version'] = schema_version_manager.get_latest_schema_version(
                    _meta_class_schema_ref['class_name'],
                )
                _meta_class_schema_ref['object_version'] = schema_version_manager.get_latest_schema_version(
                    _meta_class_schema_ref['object_id'],
                )

            model_data.data[PRIMARY_PARTITION_KEY] = old_data[PRIMARY_PARTITION_KEY]
            model_data.data[SECONDARY_PARTITION_KEY] = glue.Version.LATEST

            mutations.append(
                glue.UpdateData(
                    schema=new_schema_reference,
                    data=model_data,
                ),
            )

        if not mutations:
            return

        _transaction_manager = AmsdalTransactionManager()

        result = operation_manager.perform_data_command_lakehouse(
            command=glue.DataCommand(
                mutations=mutations,  # type: ignore[arg-type]
                root_transaction_id=_transaction_manager.get_root_transaction_id(),
                transaction_id=_transaction_manager.transaction_id,
            ),
        )

        if not result.success:
            msg = f'Failed to migrate historical data for class: {class_name}. Details: {result.message}'
            raise MigrationsError(msg) from result.exception

    def _clean_data(self, model_class: type[Model], data: dict[str, Any]) -> dict[str, Any]:
        cleaned_data: dict[str, Any] = {}

        for field_name, field in model_class.model_fields.items():
            _type_adapter = TypeAdapter(field.annotation)  # type: ignore[var-annotated]

            try:
                _type_adapter.validate_python(data.get(field_name))
            except ValidationError:
                if isinstance(data.get(field_name), (int, float)) and field.annotation in (  # noqa: UP038
                    str,
                    str | None,
                ):
                    cleaned_data[field_name] = str(data.get(field_name))

                continue
            else:
                cleaned_data[field_name] = data.get(field_name)

        return cleaned_data

    def _process_object_schema(
        self,
        object_schema: ObjectSchema,
        class_name: str,
        buffer: list[tuple[str, ObjectSchema, ModuleType]],
    ) -> ObjectSchema:
        fields = self.generate_full_object_schema(
            class_name,
            object_schema,
            buffer,
        )
        new_object_schema = object_schema.model_copy(deep=True)
        properties = new_object_schema.properties or {}
        new_object_schema.properties = {}

        for field in fields:
            field_id = field.field_id
            if not field.is_deleted and field.field_name in properties:
                new_object_schema.properties[field_id] = properties[field.field_name]
                new_object_schema.properties[field_id].field_id = field.field_id
                new_object_schema.properties[field_id].field_name = field.field_name
                new_object_schema.properties[field_id].is_deleted = False
            else:
                new_object_schema.properties[field_id] = PropertyData(
                    title=field.field_name,
                    is_deleted=field.is_deleted,
                    field_name=field.field_name,
                    field_id=field.field_id,
                    type=field.field_type,
                    default=None,
                    items=None,
                    options=None,
                    read_only=False,
                )
        return new_object_schema

    def register_schemas(self) -> None:
        """
        Registers the schemas in the table schemas manager.

        This method retrieves the object schemas from the database, processes them, and registers
        them in the table schemas manager. It handles both `ClassObject` and `ClassObjectMeta` schemas,
        and ensures that all necessary references are loaded and processed.

        Returns:
            None
        """
        buffer = []

        object_class = self.schemas.get_model(BaseClasses.OBJECT.value)
        for object_object in (
            object_class.objects.using(LAKEHOUSE_DB_ALIAS)
            .filter(title__in=['ClassObject', 'ClassObjectMeta'])
            .order_by('_metadata__updated_at')
            .execute()
        ):
            object_schema = ObjectSchema(**object_object.model_dump())
            buffer.append((object_schema.title, object_schema, ModuleType.CORE))
            schema = object_schema_to_glue_schema(
                self._process_object_schema(object_schema, object_schema.title, buffer),
                schema_names=self.schemas.registered_model_names(),
            )
            schema.version = object_object.get_metadata().object_version
            schema.name = object_schema.title

        base_meta_class = self.schemas.get_model(BaseClasses.CLASS_OBJECT_META.value)

        loaded_references = set()
        for meta_object in (
            base_meta_class.objects.using(LAKEHOUSE_DB_ALIAS).order_by('_metadata__updated_at').execute()
        ):
            class_object_reference = meta_object.get_metadata().class_meta_schema_reference

            if class_object_reference in loaded_references or class_object_reference is None:
                continue

            loaded_references.add(class_object_reference)
            class_object = ReferenceLoader(class_object_reference).load_reference(using=LAKEHOUSE_DB_ALIAS)

            dump = meta_object.model_dump()
            dump.update(class_object.model_dump())
            object_schema = ObjectSchema(**dump)
            buffer.append((object_schema.title, object_schema, ModuleType.CORE))
            schema = object_schema_to_glue_schema(
                self._process_object_schema(object_schema, object_schema.title, buffer),
                schema_names=self.schemas.registered_model_names(),
            )
            schema.version = class_object.get_metadata().object_version
            schema.name = object_schema.title


class DefaultAsyncMigrationExecutor(AsyncBaseMigrationExecutor):
    """
    Default implementation of the BaseMigrationExecutor for handling database schema migrations.

    This class provides concrete implementations for creating, updating, and deleting classes
    in the database schema. It also manages schema migration buffers and processes object schemas.
    """

    def __init__(self, schemas: BaseMigrationSchemas, *, use_foreign_keys: bool = True) -> None:
        self.schemas = schemas
        self._table_schemas_manager = AsyncTableSchemasManager()
        self._use_foreign_keys = use_foreign_keys

        super().__init__()

    def create_class(
        self,
        schemas: BaseMigrationSchemas,  # noqa: ARG002
        class_name: str,
        object_schema: ObjectSchema,
        module_type: ModuleType,
    ) -> None:
        """
        Creates a class in the database schema.

        This method registers a new class version if the schema type is `TYPE` and the class name
            is not `BaseClasses.OBJECT`.
        Otherwise, it buffers the class migration operation for further processing.

        Args:
            schemas (BaseMigrationSchemas): The migration schemas used for the operations.
            class_name (str): The name of the class to be created.
            object_schema (ObjectSchema): The schema of the object to be created.
            module_type (ModuleType): The type of the schema.

        Returns:
            None
        """
        if module_type == ModuleType.TYPE:
            AsyncHistoricalSchemaVersionManager().register_last_version(
                schema_name=class_name,
                schema_version='',
            )

            if class_name != BaseClasses.OBJECT:
                return

        self.buffer_class_migration(
            class_name,
            object_schema,
            module_type,
        )

    def update_class(
        self,
        schemas: BaseMigrationSchemas,  # noqa: ARG002
        class_name: str,
        object_schema: ObjectSchema,
        module_type: ModuleType,
    ) -> None:
        """
        Buffers the class update operation.

        This method appends the given class name, object schema, and schema type to both
        the non-flushable buffer and the main buffer for further processing.

        Args:
            schemas (BaseMigrationSchemas): The migration schemas used for the operations.
            class_name (str): The name of the class to be updated.
            object_schema (ObjectSchema): The current object schema.
            module_type (ModuleType): The type of the schema.

        Returns:
            None
        """
        self.buffer_class_migration(
            class_name,
            object_schema,
            module_type,
        )

    async def delete_class(  # type: ignore[override]
        self,
        schemas: BaseMigrationSchemas,
        class_name: str,
        module_type: ModuleType,  # noqa: ARG002
    ) -> None:
        """
        Deletes a class from the database schema.

        This method removes the specified class from the database schema and unregisters it from the migration schemas.

        Args:
            schemas (BaseMigrationSchemas): The migration schemas used for the operations.
            class_name (str): The name of the class to be deleted.
            module_type (ModuleType): The type of the schema.

        Returns:
            None
        """
        base_class_name = self._resolve_base_class_name(class_name, meta_class=MetaClasses.CLASS_OBJECT)

        await self._table_schemas_manager.delete_class_object_schema(
            schema_reference=glue.SchemaReference(
                name=base_class_name,
                version=Versions.LATEST,
            ),
            class_object_id=class_name,
        )
        schemas.unregister_model(class_name)

    async def flush_buffer(self) -> None:  # type: ignore[override]
        """
        Flushes the migration buffer and processes the buffered classes.

        This method registers the buffered classes in the migration schemas, compiles the buffered classes,
        and processes each class in the buffer to create tables, save class objects, and migrate historical data.
        Finally, it clears the main migration buffer.

        Returns:
            None
        """
        for class_name, object_schema, module_type in self._buffer:
            self.schemas.register_model(
                class_name=class_name,
                object_schema=object_schema,
                module_type=module_type,
                class_version='' if class_name == BaseClasses.OBJECT else Versions.LATEST,
            )

        self.schemas.compile_buffered_classes()

        for class_name, object_schema, module_type in self._buffer:
            _properties = object_schema.properties or {}
            for prop_name, prop in _properties.items():
                prop.field_name = prop_name
                prop.field_id = prop_name

            if class_name == BaseClasses.OBJECT:
                await self._create_table(
                    object_schema,
                    class_version='',
                    using=LAKEHOUSE_DB_ALIAS,
                )
                continue

            is_meta_class_object = object_schema.meta_class == MetaClasses.CLASS_OBJECT
            base_class_name = self._resolve_base_class_name(class_name, meta_class=object_schema.meta_class)
            schema_reference = glue.SchemaReference(
                name=base_class_name,
                version='' if base_class_name == BaseClasses.OBJECT.value else Versions.LATEST,
            )
            base_class = self.schemas.get_model(base_class_name)

            action: Action = await self._check_class(
                schema_reference=schema_reference,
                object_schema=object_schema,
                base_class=base_class,
            )

            if is_meta_class_object and action in (Action.CREATE, Action.UPDATE):
                _, _is_updated = await self._create_table(
                    object_schema,
                    Versions.LATEST,
                    using=(
                        LAKEHOUSE_DB_ALIAS
                        if object_schema.title
                        in (
                            BaseClasses.CLASS_OBJECT,
                            BaseClasses.CLASS_OBJECT_META,
                        )
                        else None
                    ),
                )

                if action == Action.UPDATE and not _is_updated:
                    msg = f'Table for {object_schema.title} was not updated. Changes were not detected.'
                    raise RuntimeError(msg)

            if action != Action.NO_ACTION:
                saved_data = await self._save_class(
                    schema_reference=schema_reference,
                    base_class=base_class,
                    object_schema=object_schema,
                    action=action,
                )

                # TODO: is it for meta type classes?
                if base_class.__name__ == BaseClasses.OBJECT:
                    AsyncHistoricalSchemaVersionManager().register_object_class(saved_data)

            if base_class_name == BaseClasses.CLASS_OBJECT:
                base_meta_class = self.schemas.get_model(BaseClasses.CLASS_OBJECT_META.value)

                # Just save new class object meta schema
                await self._save_object_class_meta(
                    base_class=base_meta_class,
                    object_schema=object_schema,
                    module_type=module_type.value,
                )

            if is_meta_class_object and action == Action.UPDATE:
                await self._migrate_historical_data(
                    self.schemas,
                    class_name,
                    prior_version=saved_data[METADATA_FIELD]['prior_version'],
                    new_version=saved_data[METADATA_FIELD]['object_version'],
                )

        await super().flush_buffer()

    async def _check_class(
        self,
        schema_reference: glue.SchemaReference,
        object_schema: ObjectSchema,
        base_class: type[Model],
    ) -> Action:
        data: dict[str, Any] | None = await self._table_schemas_manager.search_latest_class_object(
            schema_reference=schema_reference,
            class_object_name=object_schema.title,
        )

        if not data:
            return Action.CREATE

        latest_class_object = base_class(**data)
        schema_dump = base_class(**object_schema.model_dump()).model_dump()
        new_class_schema = json.dumps(schema_dump, default=str, sort_keys=True)
        existing_class_schema = json.dumps(latest_class_object.model_dump(), default=str, sort_keys=True)

        if new_class_schema == existing_class_schema:
            return Action.NO_ACTION
        return Action.UPDATE

    async def _save_class(
        self,
        schema_reference: glue.SchemaReference,
        base_class: type[Model],
        object_schema: ObjectSchema,
        action: Action,
    ) -> dict[str, Any]:
        class_object = base_class(
            **object_schema.model_dump(),
            _object_id=object_schema.title,
        )
        class_object_data = model_to_data(class_object)

        if action == Action.CREATE:
            return await self._table_schemas_manager.insert_class_object_schema(
                schema_reference=schema_reference,
                class_object_data=class_object_data,
            )
        else:
            return await self._table_schemas_manager.update_class_object_schema(
                schema_reference=schema_reference,
                class_object_data=class_object_data,
            )

    async def _save_object_class_meta(
        self,
        base_class: type[Model],
        object_schema: ObjectSchema,
        module_type: str,
    ) -> None:
        schema_reference = glue.SchemaReference(
            name=BaseClasses.CLASS_OBJECT_META.value,
            version=glue.Version.LATEST,
        )
        action = await self._check_class(schema_reference, object_schema, base_class)
        object_schema.class_schema_type = module_type  # type: ignore[attr-defined]

        await self._save_class(schema_reference, base_class, object_schema, action)

    async def _create_table(
        self,
        object_schema: ObjectSchema,
        class_version: str | Versions,
        using: str | None = None,
    ) -> tuple[bool, bool]:
        from amsdal_data.application import AsyncDataApplication

        is_lakehouse_only = using == LAKEHOUSE_DB_ALIAS or AsyncDataApplication().is_lakehouse_only
        schema = object_schema_to_glue_schema(
            object_schema,
            is_lakehouse_only=is_lakehouse_only,
            use_foreign_keys=self._use_foreign_keys,
            schema_names=self.schemas.registered_model_names(),
        )
        schema.version = class_version

        return await self._table_schemas_manager.register_table(schema, using=using)

    async def _migrate_historical_data(
        self,
        schemas: BaseMigrationSchemas,
        class_name: str,
        prior_version: str,
        new_version: str,
    ) -> None:
        from amsdal_data.application import AsyncDataApplication

        if class_name in (BaseClasses.OBJECT, BaseClasses.CLASS_OBJECT):
            msg = 'Migrations for Object and ClassObject classes are not supported for now.'
            raise NotImplementedError(msg)

        schema_version_manager = AsyncHistoricalSchemaVersionManager()
        operation_manager = AsyncDataApplication().operation_manager
        migrated_class = schemas.get_model(class_name)
        mutations = []

        old_schema_reference = glue.SchemaReference(
            name=class_name,
            version=prior_version,
        )
        new_schema_reference = glue.SchemaReference(
            name=class_name,
            version=new_version,
        )

        async for old_data in self._table_schemas_manager.fetch_historical_data(old_schema_reference):  # type: ignore[attr-defined]
            _data = self._clean_data(migrated_class, old_data)
            model_data: glue.Data = model_to_data(migrated_class(**_data))
            model_data.data[METADATA_KEY] = old_data[METADATA_KEY]

            # adjust class versions in metadata
            _class_schema_ref = model_data.data[METADATA_KEY]['class_schema_reference']['ref']
            _class_schema_ref['class_version'] = await schema_version_manager.get_latest_schema_version(
                _class_schema_ref['class_name'],
            )
            _class_schema_ref['object_version'] = await schema_version_manager.get_latest_schema_version(
                _class_schema_ref['object_id'],
            )

            _meta_class_schema = model_data.data[METADATA_KEY]['class_meta_schema_reference']

            if _meta_class_schema:
                _meta_class_schema_ref = _meta_class_schema['ref']
                _meta_class_schema_ref['class_version'] = await schema_version_manager.get_latest_schema_version(
                    _meta_class_schema_ref['class_name'],
                )
                _meta_class_schema_ref['object_version'] = await schema_version_manager.get_latest_schema_version(
                    _meta_class_schema_ref['object_id'],
                )

            model_data.data[PRIMARY_PARTITION_KEY] = old_data[PRIMARY_PARTITION_KEY]
            model_data.data[SECONDARY_PARTITION_KEY] = glue.Version.LATEST

            mutations.append(
                glue.UpdateData(
                    schema=new_schema_reference,
                    data=model_data,
                ),
            )

        if not mutations:
            return

        _transaction_manager = AmsdalAsyncTransactionManager()

        result = await operation_manager.perform_data_command_lakehouse(
            command=glue.DataCommand(
                mutations=mutations,  # type: ignore[arg-type]
                root_transaction_id=_transaction_manager.get_root_transaction_id(),
                transaction_id=_transaction_manager.transaction_id,
            ),
        )

        if not result.success:
            msg = f'Failed to migrate historical data for class: {class_name}. Details: {result.message}'
            raise MigrationsError(msg) from result.exception

    def _clean_data(self, model_class: type[Model], data: dict[str, Any]) -> dict[str, Any]:
        cleaned_data: dict[str, Any] = {}

        for field_name, field in model_class.model_fields.items():
            _type_adapter = TypeAdapter(field.annotation)  # type: ignore[var-annotated]

            try:
                _type_adapter.validate_python(data.get(field_name))
            except ValidationError:
                if isinstance(data.get(field_name), (int, float)) and field.annotation in (  # noqa: UP038
                    str,
                    str | None,
                ):
                    cleaned_data[field_name] = str(data.get(field_name))

                continue
            else:
                cleaned_data[field_name] = data.get(field_name)

        return cleaned_data

    def _process_object_schema(
        self,
        object_schema: ObjectSchema,
        class_name: str,
        buffer: list[tuple[str, ObjectSchema, ModuleType]],
    ) -> ObjectSchema:
        fields = self.generate_full_object_schema(
            class_name,
            object_schema,
            buffer,
        )
        new_object_schema = object_schema.model_copy(deep=True)
        properties = new_object_schema.properties or {}
        new_object_schema.properties = {}

        for field in fields:
            field_id = field.field_id
            if not field.is_deleted and field.field_name in properties:
                new_object_schema.properties[field_id] = properties[field.field_name]
                new_object_schema.properties[field_id].field_id = field.field_id
                new_object_schema.properties[field_id].field_name = field.field_name
                new_object_schema.properties[field_id].is_deleted = False
            else:
                new_object_schema.properties[field_id] = PropertyData(
                    title=field.field_name,
                    is_deleted=field.is_deleted,
                    field_name=field.field_name,
                    field_id=field.field_id,
                    type=field.field_type,
                    default=None,
                    items=None,
                    options=None,
                    read_only=False,
                )
        return new_object_schema

    async def register_schemas(self) -> None:
        """
        Registers the schemas in the table schemas manager.

        This method retrieves the object schemas from the database, processes them, and registers
        them in the table schemas manager. It handles both `ClassObject` and `ClassObjectMeta` schemas,
        and ensures that all necessary references are loaded and processed.

        Returns:
            None
        """
        buffer = []

        object_class = self.schemas.get_model(BaseClasses.OBJECT.value)
        for object_object in await (
            object_class.objects.using(LAKEHOUSE_DB_ALIAS)
            .filter(title__in=['ClassObject', 'ClassObjectMeta'])
            .order_by('_metadata__updated_at')
            .aexecute()
        ):
            object_schema = ObjectSchema(**object_object.model_dump())
            buffer.append((object_schema.title, object_schema, ModuleType.CORE))
            schema = object_schema_to_glue_schema(
                self._process_object_schema(object_schema, object_schema.title, buffer),
                schema_names=self.schemas.registered_model_names(),
            )
            schema.version = object_object.get_metadata().object_version
            schema.name = object_schema.title

        base_meta_class = self.schemas.get_model(BaseClasses.CLASS_OBJECT_META.value)

        loaded_references = set()
        for meta_object in (
            await base_meta_class.objects.using(LAKEHOUSE_DB_ALIAS).order_by('_metadata__updated_at').aexecute()
        ):
            class_object_reference = meta_object.get_metadata().class_meta_schema_reference

            if class_object_reference in loaded_references or class_object_reference is None:
                continue

            loaded_references.add(class_object_reference)

            class_object = await ReferenceLoader(class_object_reference).aload_reference(using=LAKEHOUSE_DB_ALIAS)

            dump = meta_object.model_dump()
            dump.update(class_object.model_dump())
            object_schema = ObjectSchema(**dump)
            buffer.append((object_schema.title, object_schema, ModuleType.CORE))
            schema = object_schema_to_glue_schema(
                self._process_object_schema(object_schema, object_schema.title, buffer),
                schema_names=self.schemas.registered_model_names(),
            )
            schema.version = class_object.get_metadata().object_version
            schema.name = object_schema.title
