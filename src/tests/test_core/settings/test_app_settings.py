import os

import pytest

from app.core.settings import app as app_settings

TEST_ENV_1 = dict(
    APP_DEBUG='false',
    APP_DOCS_URL='/docs',
    APP_OPENAPI_PREFIX='',
    APP_OPENAPI_URL='openapi.json',
    APP_REDOC_URL='/redoc',
    APP_TITLE='FastAPI example application',
    APP_VERSION='0.0.0',
    APP_SWAGGER_UI_OAUTH2_REDIRECT_URL='/docs/oauth2-redirect',
    APP_SWAGGER_UI_SYNTAX_HIGHLIGHT='true',
    APP_SWAGGER_UI_DEEP_LINKING='true',
    APP_SWAGGER_UI_DOM_ID='#swagger-ui',
    APP_SWAGGER_UI_LAYOUT='BaseLayout',
    APP_SWAGGER_UI_SHOW_EXTENSIONS='true',
    APP_SWAGGER_UI_SHOW_COMMON_EXTENSIONS='true',
    APP_SWAGGER_UI_SYNTAX_HIGHLIGHT_THEME='obsidian',
    APP_ROOT_PATH='',
    APP_ROOT_PATH_IN_SERVERS='true',
)
TEST_ENV_2 = dict(
    APP_DEBUG='true',
    APP_DOCS_URL='/docs-changed',
    APP_OPENAPI_PREFIX='/abc/',
    APP_OPENAPI_URL='openapi-changed.json',
    APP_REDOC_URL='/redoc-changed',
    APP_TITLE='Changed title',
    APP_VERSION='1.1.1',
    APP_SWAGGER_UI_OAUTH2_REDIRECT_URL='/docs/oauth2-redirect',
    APP_SWAGGER_UI_SYNTAX_HIGHLIGHT='true',
    APP_SWAGGER_UI_DEEP_LINKING='true',
    APP_SWAGGER_UI_DOM_ID='#swagger-ui',
    APP_SWAGGER_UI_LAYOUT='BaseLayout',
    APP_SWAGGER_UI_SHOW_EXTENSIONS='true',
    APP_SWAGGER_UI_SHOW_COMMON_EXTENSIONS='true',
    APP_SWAGGER_UI_SYNTAX_HIGHLIGHT_THEME='obsidian',
    APP_ROOT_PATH='',
    APP_ROOT_PATH_IN_SERVERS='true',
    APP_TERM_OF_SERVICE='https://example.com/term-of-service',
    APP_CONTACT='{"name": "abc", "url": "http://abc.com", "email": "example@mail.ru"}',
    APP_LICENSE='{"name": "Apache 2.0", "url": "http://abc.com"}',
    APP_SERVERS='[{"url": "http://abc.com", "description": "abc"}]',
)


@pytest.mark.parametrize('dict_env', [TEST_ENV_1, TEST_ENV_2])
def test_app_settings_contains(dict_env: dict[str, str]) -> None:
    """Проверка значений настроек приложения."""
    os.environ.update(dict_env)
    settings = app_settings.AppSettings()

    assert settings.debug == (dict_env.get('APP_DEBUG') == 'true')
    assert settings.docs_url == dict_env.get('APP_DOCS_URL')
    assert settings.openapi_prefix == dict_env.get('APP_OPENAPI_PREFIX')
    assert settings.openapi_url == dict_env.get('APP_OPENAPI_URL')
    assert settings.redoc_url == dict_env.get('APP_REDOC_URL')
    assert settings.title == dict_env.get('APP_TITLE')
    assert settings.swagger_ui_oauth2_redirect_url == dict_env.get(
        'APP_SWAGGER_UI_OAUTH2_REDIRECT_URL',
    )
    assert settings.swagger_ui_syntax_highlight == (
        dict_env.get('APP_SWAGGER_UI_SYNTAX_HIGHLIGHT') == 'true'
    )
    assert settings.swagger_ui_deep_linking == (
        dict_env.get('APP_SWAGGER_UI_DEEP_LINKING') == 'true'
    )
    assert settings.swagger_ui_dom_id == dict_env.get('APP_SWAGGER_UI_DOM_ID')
    assert settings.swagger_ui_layout == dict_env.get('APP_SWAGGER_UI_LAYOUT')
    assert settings.swagger_ui_show_extensions == (
        dict_env.get('APP_SWAGGER_UI_SHOW_EXTENSIONS') == 'true'
    )
    assert settings.swagger_ui_show_common_extensions == (
        dict_env.get(
            'APP_SWAGGER_UI_SHOW_COMMON_EXTENSIONS',
        )
        == 'true'
    )
    assert settings.root_path == dict_env.get('APP_ROOT_PATH')
    assert settings.root_path_in_servers == (dict_env.get('APP_ROOT_PATH_IN_SERVERS') == 'true')
    assert (str(settings.term_of_service) if settings.term_of_service else None) == dict_env.get(
        'APP_TERM_OF_SERVICE',
    )
    assert settings.contact == (
        app_settings.Contact.model_validate_json(dict_env['APP_CONTACT'])
        if 'APP_CONTACT' in dict_env
        else None
    )
    assert settings.license == (
        app_settings.License.model_validate_json(dict_env['APP_LICENSE'])
        if 'APP_LICENSE' in dict_env
        else None
    )


@pytest.mark.parametrize('dict_env', [TEST_ENV_1, TEST_ENV_2])
def test_app_settings_fastapi_kwargs(dict_env: dict[str, str]) -> None:
    """Проверка значений свойства fastapi_kwargs."""
    os.environ.update(dict_env)
    settings = app_settings.AppSettings()
    fastapi_kwargs = settings.fastapi_kwargs

    assert settings.debug == fastapi_kwargs['debug']
    assert settings.docs_url == fastapi_kwargs['docs_url']
    assert settings.openapi_prefix == fastapi_kwargs['openapi_prefix']
    assert settings.openapi_url == fastapi_kwargs['openapi_url']
    assert settings.redoc_url == fastapi_kwargs['redoc_url']
    assert settings.title == fastapi_kwargs['title']
    assert settings.version == fastapi_kwargs['version']
