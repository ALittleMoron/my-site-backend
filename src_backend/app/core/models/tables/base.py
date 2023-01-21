from tortoise import fields, models


class Base(models.Model):
    """Базовый абстрактный класс для модели таблицы."""

    id = fields.UUIDField(pk=True, description='Уникальный идентификатор модели')  # noqa: VNE003

    class Meta:  # type: ignore
        """Мета-класс базового абстрактного класса."""

        abstract = True


class TimedMixin:
    """Примесь модели для хранения даты и времени создания и обновления."""

    created_at = fields.DatetimeField(auto_now_add=True, description='Дата и время создания модели')
    updated_at = fields.DatetimeField(auto_now=True, description='Дата и время обновления модели')
