import os
import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.settings import base as base_settings
from app.utils import env as env_utils

SRC_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.parent.absolute()
APP_DIR: pathlib.Path = SRC_DIR / 'app'
PROJECT_ROOT_DIR: pathlib.Path = SRC_DIR.parent
STATIC_DIR = PROJECT_ROOT_DIR / 'static'
SCRIPTS_DIR = PROJECT_ROOT_DIR / 'scripts'
LOGS_DIR = PROJECT_ROOT_DIR / 'logs'
TESTS_DIR = SRC_DIR / 'tests'
TESTING_MODE = env_utils.getenv_bool('TESTING_MODE', 'true')
project_run_mode = os.environ.get('PROJECT_RUN_MODE')
env_file_base_name = os.environ.get('ENV_FILE_BASE_NAME', '.env')
env_file_name = f'{env_file_base_name}.{project_run_mode}'
env_files_dir = PROJECT_ROOT_DIR / 'dotenv'


def test_base_vars() -> None:
    """Проверка базовых переменных настроек."""
    assert SRC_DIR == base_settings.SRC_DIR
    assert APP_DIR == base_settings.APP_DIR
    assert PROJECT_ROOT_DIR == base_settings.PROJECT_ROOT_DIR
    assert TESTING_MODE == base_settings.TESTING_MODE
    assert project_run_mode == base_settings.project_run_mode
    assert env_file_base_name == base_settings.env_file_base_name
    assert env_file_name == base_settings.env_file_name
    assert env_files_dir == base_settings.env_files_dir


def test_path_settings_class() -> None:
    """Проверка работы класса настроек для путей."""

    class PathSettings(BaseSettings):
        model_config = SettingsConfigDict(env_prefix='APP_PATH_DEFAULTS_')
        project_root_dir: pathlib.Path = PROJECT_ROOT_DIR
        static_dir: pathlib.Path = STATIC_DIR
        app_dir: pathlib.Path = APP_DIR
        src_dir: pathlib.Path = SRC_DIR
        tests_dir: pathlib.Path = TESTS_DIR
        env_files_dir: pathlib.Path = env_files_dir
        scripts_dir: pathlib.Path = SCRIPTS_DIR
        logs_dir: pathlib.Path = LOGS_DIR

    instance = base_settings.PathSettings()
    fake_instance = PathSettings()

    assert instance.project_root_dir == fake_instance.project_root_dir
    assert instance.static_dir == fake_instance.static_dir
    assert instance.app_dir == fake_instance.app_dir
    assert instance.src_dir == fake_instance.src_dir
    assert instance.tests_dir == fake_instance.tests_dir
    assert instance.env_files_dir == fake_instance.env_files_dir
    assert instance.scripts_dir == fake_instance.scripts_dir
    assert instance.logs_dir == fake_instance.logs_dir
