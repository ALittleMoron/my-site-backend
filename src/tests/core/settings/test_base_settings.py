import os
import pathlib

from pydantic import BaseSettings

from app.core.settings import base as base_settings
from app.utils import env as env_utils

SRC_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.parent.absolute()
APP_DIR: pathlib.Path = SRC_DIR / 'app'
PROJECT_ROOT_DIR: pathlib.Path = SRC_DIR.parent
TESTING_MODE = env_utils.getenv_bool('TESTING_MODE', 'true')
project_run_mode = os.environ.get('PROJECT_RUN_MODE')
env_file_base_name = os.environ.get('ENV_FILE_BASE_NAME', '.env')
env_file_name = f'{env_file_base_name}.{project_run_mode}'


def test_base_vars() -> None:
    """Проверка базовых переменных настроек."""
    assert SRC_DIR == base_settings.SRC_DIR
    assert APP_DIR == base_settings.APP_DIR
    assert PROJECT_ROOT_DIR == base_settings.PROJECT_ROOT_DIR
    assert TESTING_MODE == base_settings.TESTING_MODE
    assert project_run_mode == base_settings.project_run_mode
    assert env_file_base_name == base_settings.env_file_base_name
    assert env_file_name == base_settings.env_file_name


def test_path_settings_class() -> None:
    """Проверка работы класса настроек для путей."""

    class PathSettings(BaseSettings):
        """Настройки, содержащие базовые пути проекта."""

        app_dir: pathlib.Path = APP_DIR
        src_dir: pathlib.Path = SRC_DIR
        project_root_dir: pathlib.Path = PROJECT_ROOT_DIR

    instance = base_settings.PathSettings()
    fake_instance = PathSettings()

    assert instance.app_dir == fake_instance.app_dir
    assert instance.src_dir == fake_instance.src_dir
    assert instance.project_root_dir == fake_instance.project_root_dir
