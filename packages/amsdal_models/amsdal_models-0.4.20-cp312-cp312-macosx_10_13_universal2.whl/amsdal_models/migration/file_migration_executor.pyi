from _typeshed import Incomplete
from amsdal_data.transactions import async_transaction, transaction
from amsdal_models.migration.data_classes import MigrationDirection as MigrationDirection, MigrationFile as MigrationFile, MigrationResult as MigrationResult
from amsdal_models.migration.executors.base import AsyncBaseMigrationExecutor as AsyncBaseMigrationExecutor, BaseMigrationExecutor as BaseMigrationExecutor
from amsdal_models.migration.executors.state_executor import AsyncStateMigrationExecutor as AsyncStateMigrationExecutor, StateMigrationExecutor as StateMigrationExecutor
from amsdal_models.migration.file_migration_store import AsyncBaseMigrationStore as AsyncBaseMigrationStore, AsyncFileMigrationStore as AsyncFileMigrationStore, BaseMigrationStore as BaseMigrationStore, FileMigrationStore as FileMigrationStore
from amsdal_models.migration.migrations import MigrateData as MigrateData, Migration as Migration
from amsdal_models.migration.migrations_loader import MigrationsLoader as MigrationsLoader
from amsdal_models.migration.utils import contrib_to_module_root_path as contrib_to_module_root_path
from amsdal_utils.models.data_models.address import Address
from amsdal_utils.models.enums import ModuleType
from pathlib import Path

logger: Incomplete

class FileMigrationExecutorManager:
    """
    Manager class for executing file migrations.

    Attributes:
        migration_address (Address): The address associated with the migration.
        core_loader (MigrationsLoader): Loader for core migrations.
        contrib_loaders (list[MigrationsLoader]): List of loaders for contributed migrations.
        app_loader (MigrationsLoader): Loader for application migrations.
        executor (BaseMigrationExecutor): The executor responsible for running migrations.
        store (BaseMigrationStore): The store for managing migration files.
    """
    migration_address: Address
    core_loader: Incomplete
    contrib_loaders: Incomplete
    app_loader: Incomplete
    executor: Incomplete
    _applied_migration_files: list[MigrationFile]
    store: Incomplete
    def __init__(self, core_migrations_path: Path, app_migrations_loader: MigrationsLoader, executor: BaseMigrationExecutor, store: BaseMigrationStore | None = None, contrib: list[str] | None = None, contrib_migrations_directory_name: str = '__migrations__') -> None: ...
    def execute(self, migration_number: int | None = None, module_type: ModuleType | None = None, *, fake: bool = False, skip_data_migrations: bool = False) -> list[MigrationResult]:
        """
        Executes the migrations.

        Args:
            migration_number (int | None): The migration number to execute up to. Defaults to None.
            module_type (ModuleType | None): The type of module to migrate. Defaults to None.
            fake (bool): If True, simulates the migration without applying changes. Defaults to False.
            skip_data_migrations (bool): If True, skips data migrations. Defaults to False.

        Returns:
            list[MigrationResult]: List of results from the migration execution.
        """
    @staticmethod
    def _get_contrib_loaders(contrib: list[str], contrib_migrations_directory_name: str) -> list[MigrationsLoader]: ...
    @transaction
    def _apply(self, migration_number: int | None = None, module_type: ModuleType | None = None, *, fake: bool = False, skip_data_migrations: bool = False) -> list[MigrationResult]: ...
    def _apply_migrations(self, loader: MigrationsLoader, module_type: ModuleType, migration_number: int | None = None, *, fake: bool = False, skip_data_migrations: bool = False) -> list[MigrationResult]: ...
    def _register_schemas(self, executor: BaseMigrationExecutor) -> None: ...
    def _init_state_from_applied_migrations(self, migrations: list[MigrationFile], module_type: ModuleType) -> None: ...
    @staticmethod
    def get_migration_class(migration: MigrationFile) -> type['Migration']:
        """
        Retrieves the migration class from the migration file.

        Args:
            migration (MigrationFile): The migration file.

        Returns:
            type[Migration]: The migration class.
        """
    def _is_migration_applied(self, migration: MigrationFile, module_type: ModuleType) -> bool: ...

class AsyncFileMigrationExecutorManager:
    """
    Manager class for executing file migrations.

    Attributes:
        migration_address (Address): The address associated with the migration.
        core_loader (MigrationsLoader): Loader for core migrations.
        contrib_loaders (list[MigrationsLoader]): List of loaders for contributed migrations.
        app_loader (MigrationsLoader): Loader for application migrations.
        executor (BaseMigrationExecutor): The executor responsible for running migrations.
        store (BaseMigrationStore): The store for managing migration files.
    """
    migration_address: Address
    core_loader: Incomplete
    contrib_loaders: Incomplete
    app_loader: Incomplete
    executor: Incomplete
    _applied_migration_files: list[MigrationFile]
    store: Incomplete
    def __init__(self, core_migrations_path: Path, app_migrations_loader: MigrationsLoader, executor: AsyncBaseMigrationExecutor, store: AsyncBaseMigrationStore | None = None, contrib: list[str] | None = None, contrib_migrations_directory_name: str = '__migrations__') -> None: ...
    async def execute(self, migration_number: int | None = None, module_type: ModuleType | None = None, *, fake: bool = False, skip_data_migrations: bool = False) -> list[MigrationResult]:
        """
        Executes the migrations.

        Args:
            migration_number (int | None): The migration number to execute up to. Defaults to None.
            module_type (ModuleTypes | None): The type of module to migrate. Defaults to None.
            fake (bool): If True, simulates the migration without applying changes. Defaults to False.
            skip_data_migrations (bool): If True, skips data migrations. Defaults to False.

        Returns:
            list[MigrationResult]: List of results from the migration execution.
        """
    @staticmethod
    def _get_contrib_loaders(contrib: list[str], contrib_migrations_directory_name: str) -> list[MigrationsLoader]: ...
    @async_transaction
    async def _apply(self, migration_number: int | None = None, module_type: ModuleType | None = None, *, fake: bool = False, skip_data_migrations: bool = False) -> list[MigrationResult]: ...
    async def _apply_migrations(self, loader: MigrationsLoader, module_type: ModuleType, migration_number: int | None = None, *, fake: bool = False, skip_data_migrations: bool = False) -> list[MigrationResult]: ...
    async def _register_schemas(self, executor: BaseMigrationExecutor) -> None: ...
    async def _init_state_from_applied_migrations(self, migrations: list[MigrationFile], module_type: ModuleType) -> None: ...
    @staticmethod
    def get_migration_class(migration: MigrationFile) -> type['Migration']:
        """
        Retrieves the migration class from the migration file.

        Args:
            migration (MigrationFile): The migration file.

        Returns:
            type[Migration]: The migration class.
        """
    def _is_migration_applied(self, migration: MigrationFile, module_type: ModuleType) -> bool: ...
