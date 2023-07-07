from dateutil.relativedelta import relativedelta

from app.core.models.enums import base as base_model_enums


def test_str_delta_enum() -> None:
    """Проверка StrTimedeltaEnum."""
    assert base_model_enums.StrTimedeltaEnum.__annotations__['timedelta'] == relativedelta

    class TestEnum(base_model_enums.StrTimedeltaEnum):
        NEVER = 'never'
        DAILY = 'daily', relativedelta(days=1)

    assert TestEnum.NEVER.name == 'NEVER'
    assert TestEnum.NEVER.value == 'never'
    assert TestEnum.NEVER.timedelta == relativedelta()
    assert TestEnum.DAILY.name == 'DAILY'
    assert TestEnum.DAILY.value == 'daily'
    assert TestEnum.DAILY.timedelta == relativedelta(days=1)
