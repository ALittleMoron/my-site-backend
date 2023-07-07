from typing import TYPE_CHECKING

import freezegun
import pytest
from mimesis import Datetime
from mimesis.locales import Locale

from app.utils import datetime as datetime_utils

if TYPE_CHECKING:
    import datetime


fake_datetimes = Datetime(Locale.EN)


@pytest.mark.parametrize('freeze_dt', [fake_datetimes.datetime(timezone='UTC') for _ in range(30)])
def test_utc_now(freeze_dt: 'datetime.datetime') -> None:
    """Проверка работы метода получения текущего времени в UTC."""
    with freezegun.freeze_time(freeze_dt):
        assert datetime_utils.get_utc_now() == freeze_dt
