import random


def coin_flip() -> bool:
    """Возвращает случайное булево значение."""
    return bool(random.getrandbits(1))
