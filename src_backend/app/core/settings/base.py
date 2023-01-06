import os
import pathlib

from pydantic import BaseConfig as BasePydanticConfig
from pydantic import BaseSettings

APP_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.absolute()
SRC_DIR: pathlib.Path = APP_DIR.parent
PROJECT_ROOT_DIR: pathlib.Path = SRC_DIR.parent

from app.core.exceptions.content import PROJECT_RUN_MODE_NOT_SET  # noqa: E402

project_run_mode = os.environ.get('PROJECT_RUN_MODE')
if not project_run_mode:
    raise NotImplementedError(PROJECT_RUN_MODE_NOT_SET)

env_file_base_name = os.environ.get('ENV_FILE_BASE_NAME', '.env')
env_file_name = '{base_name}.{mode}'.format(base_name=env_file_base_name, mode=project_run_mode)


class PathSettings(BaseSettings):
    """Настройки, содержащие базовые пути проекта."""

    app_dir: pathlib.Path = APP_DIR
    src_dir: pathlib.Path = SRC_DIR
    project_root_dir: pathlib.Path = PROJECT_ROOT_DIR


class BaseConfig(BasePydanticConfig):
    """Базовый класс конфига для настроек и моделей Pydantic."""

    env_file = SRC_DIR / env_file_name
    validate_assignment = True
