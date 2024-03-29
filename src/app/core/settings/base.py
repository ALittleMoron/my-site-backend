"""Модуль базовых настроек проекта."""
import os
import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils import env as env_utils

APP_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.absolute()
SRC_DIR: pathlib.Path = APP_DIR.parent
TESTS_DIR = SRC_DIR / 'tests'
MIGRATIONS_DIR = SRC_DIR / 'migrations'
CLI_DIR = SRC_DIR / 'cli'
PROJECT_ROOT_DIR: pathlib.Path = SRC_DIR.parent
STATIC_DIR = PROJECT_ROOT_DIR / 'static'
SCRIPTS_DIR = PROJECT_ROOT_DIR / 'scripts'
LOGS_DIR = PROJECT_ROOT_DIR / 'logs'
TESTING_MODE = env_utils.getenv_bool('TESTING_MODE', 'true')

project_run_mode = os.environ.get('PROJECT_RUN_MODE', 'dev')

env_file_base_name = os.environ.get('ENV_FILE_BASE_NAME', '.env')
env_file_name = f'{env_file_base_name}.{project_run_mode}'
env_files_dir = PROJECT_ROOT_DIR / 'dotenv'


class ProjectBaseSettings(BaseSettings):
    """Базовые настройки проекта."""

    model_config = SettingsConfigDict(
        extra='ignore',
        env_file=env_files_dir / env_file_name,
        validate_assignment=True,
        env_nested_delimiter='_',
    )


class PathSettings(ProjectBaseSettings):
    """Настройки, содержащие базовые пути проекта."""

    model_config = SettingsConfigDict(env_prefix='APP_PATH_DEFAULTS_')

    project_root_dir: pathlib.Path = PROJECT_ROOT_DIR
    static_dir: pathlib.Path = STATIC_DIR
    app_dir: pathlib.Path = APP_DIR
    src_dir: pathlib.Path = SRC_DIR
    tests_dir: pathlib.Path = TESTS_DIR
    migrations_dir: pathlib.Path = MIGRATIONS_DIR
    cli_dir: pathlib.Path = CLI_DIR
    env_files_dir: pathlib.Path = env_files_dir
    scripts_dir: pathlib.Path = SCRIPTS_DIR
    logs_dir: pathlib.Path = LOGS_DIR
