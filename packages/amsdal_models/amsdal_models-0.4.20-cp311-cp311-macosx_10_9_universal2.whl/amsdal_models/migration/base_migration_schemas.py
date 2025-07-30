from abc import ABC
from abc import abstractmethod
from typing import Any

from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager
from amsdal_utils.models.data_models.enums import CoreTypes
from amsdal_utils.models.data_models.enums import MetaClasses
from amsdal_utils.models.enums import ModuleType
from amsdal_utils.models.enums import Versions
from amsdal_utils.schemas.schema import ObjectSchema

from amsdal_models.builder.class_source_builder import ClassSourceBuilder
from amsdal_models.builder.utils import ModelModuleInfo
from amsdal_models.classes.model import Model


class BaseMigrationSchemas(ABC):
    """
    Abstract base class for migration schemas.

    This class provides the interface for managing and compiling database schema migrations.
    It includes methods for registering, unregistering, and compiling classes, as well as
    managing class versions.
    """

    def __init__(self) -> None:
        self._classes: dict[str, type[Model]] = {}
        self._classes_versions: dict[str, dict[str, type[Model]]] = {}
        self._buffered_classes: list[tuple[str, ObjectSchema, ModuleType]] = []

    def get_model(self, name: str) -> type[Model]:
        """
        Retrieves the model type for the given class name.

        Args:
            name (str): The name of the class whose model type is to be retrieved.

        Returns:
            type[Model]: The model type associated with the given class name.
        """
        return self._classes[name]

    def registered_model_names(self) -> list[str]:
        """
        Returns a list of registered model names.
        This method retrieves the names of all registered model classes.
        It filters the classes to include only those that are subclasses of the Model class.

        Returns:
            list[str]: A list of registered model names.
        """
        return [class_name for class_name, model in self._classes.items() if issubclass(model, Model)]

    @abstractmethod
    def register_model(
        self,
        class_name: str,
        object_schema: ObjectSchema,
        module_type: ModuleType,
        class_version: str | Versions = Versions.LATEST,
    ) -> None: ...

    @abstractmethod
    def unregister_model(self, class_name: str) -> None: ...

    @abstractmethod
    def compile_buffered_classes(self) -> None: ...

    @staticmethod
    def register_model_version(class_name: str, class_version: str | Versions) -> None:
        """
        Registers a specific version of a model class.

        This method registers a specific version of a model class using the ClassVersionManager.

        Args:
            class_name (str): The name of the class to register the version for.
            class_version (str | Versions): The version of the class to be registered.

        Returns:
            None
        """
        HistoricalSchemaVersionManager().register_last_version(
            schema_name=class_name,
            schema_version=class_version,
        )


class DefaultMigrationSchemas(BaseMigrationSchemas):
    """
    Default implementation of the BaseMigrationSchemas.

    This class provides the default implementation for managing and compiling database schema migrations.
    It includes methods for registering, unregistering, and compiling classes, as well as managing class versions.
    """

    def register_model(
        self,
        class_name: str,
        object_schema: ObjectSchema,
        module_type: ModuleType,
        class_version: str | Versions = Versions.LATEST,  # noqa: ARG002
    ) -> None:
        """
        Registers a model class for migration.

        This method registers a model class for migration by adding it to the buffered classes
        and registering its latest version.

        Args:
            class_name (str): The name of the class to be registered.
            object_schema (ObjectSchema): The schema of the object to be registered.
            module_type (SchemaTypes): The type of the schema.

        Returns:
            None
        """
        self._buffered_classes.append(
            (
                class_name,
                object_schema,
                module_type,
            ),
        )

    def compile_buffered_classes(self) -> None:
        """
        Compiles all buffered classes for migration.

        This method compiles all classes that have been buffered for migration and updates the
        internal class dictionary with the compiled class types. It clears the buffer after
        compilation.

        Returns:
            None
        """
        if not self._buffered_classes:
            return

        for class_name, class_type in self._compile_buffered_classes():
            self._classes[class_name] = class_type

        self._buffered_classes.clear()

    def unregister_model(self, class_name: str) -> None:
        """
        Unregisters a model class from the migration schemas.

        This method removes the specified model class from the internal class dictionary,
        effectively unregistering it from the migration schemas.

        Args:
            class_name (str): The name of the class to be unregistered.

        Returns:
            None
        """
        if class_name not in self._classes:
            return

        del self._classes[class_name]

    def _compile_buffered_classes(self) -> list[tuple[str, type[Model]]]:
        source = ''
        all_class_names: list[str] = []

        rebuild_part = ''

        for class_name, schema, module_type in self._buffered_classes:
            base_class = self._resolve_class_inheritance(schema)
            all_class_names.append(class_name)

            ast_class_generator = ClassSourceBuilder(
                module_path='',
                schema=schema,
                module_type=module_type,
                base_class=base_class,
                dependencies=ModelModuleInfo(info={}),
                indent_width=' ' * 4,
            )
            source += (
                f'{ast_class_generator.dependencies_source}\n\n'
                f'{ast_class_generator.enums_source}\n\n'
                f'{ast_class_generator.model_class_source}\n\n'
            )
            rebuild_part += f'{class_name}.model_rebuild()\n\n'

        source += f'\n\n{rebuild_part}'

        code = compile(source, 'classes', 'exec')
        globs: dict[str, Any] = dict(self._classes.items())
        eval(code, globs)  # noqa: S307
        return [(class_name, globs[class_name]) for class_name in all_class_names]

    @staticmethod
    def _resolve_class_inheritance(schema: ObjectSchema) -> type | str:
        from amsdal_models.classes.model import Model
        from amsdal_models.classes.model import TypeModel

        if schema.meta_class == MetaClasses.TYPE:
            return TypeModel

        if schema.type == CoreTypes.OBJECT.value:
            return Model

        return schema.type
