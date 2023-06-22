SIZEOF_UNIT = ["", "K", "M", "G", "T", "P", "E", "Z"]


def sizeof_fmt(num: int | float, *, suffix: str = "b", force_float: bool = False) -> str:
    """Преобразует байты в понятный вид.

    Parameters
    ----------
    num
        число для преобразования (из байт в нужный формат).
    suffix
        суффикс форматированного значения (Kb -> suffix = 'b').

    Returns
    -------
    str
        число байт в нужном формате.
    """
    for unit in SIZEOF_UNIT:
        if abs(num) < 1024.0:
            if force_float or int(num) != num:
                return f"{num:3.1f}{unit}{suffix}"
            return f"{int(num)}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"
