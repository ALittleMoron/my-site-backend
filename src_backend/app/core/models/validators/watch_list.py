from tortoise.exceptions import ValidationError
from tortoise.validators import Validator


class ScoreValidator(Validator):
    """Класс валидатора для проверки оценки на вхождение в диапазон от 0 до 10."""

    def __call__(self, value: int):
        """Проверка оценки на вхождение в диапазон.

        Args:
            value (int): значение для проверки.

        Raises:
            ValidationError: число не в диапазоне [0...10].
        """
        if not 0 <= value <= 10:
            raise ValidationError(f"Значение '{value}' не входит в диапазон [0...10].")
