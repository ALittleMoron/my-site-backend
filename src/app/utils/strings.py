def has_format_brackets(value: str) -> bool:
    """Проверяет, содержит ли переданная строка такие фигурные скобки для форматирования.

    Проверяет в том числе и экранированные фигурные скобки, поэтому строка '{{}}' вернет False для
    данной функции, потому что по данным скобкам нельзя провести ``.format(value)``.

    Parameters
    ----------
    value : string
        передаваемое проверяемое значение.

    Returns
    -------
    bool
        является ли строка форматируемой (есть ли у неё нужные фигурные скобки)?

    Examples
    --------
    >>> has_format_brackets('{}')
    True
    >>> has_format_brackets('{some_variables}')
    True
    >>> has_format_brackets('{}}')
    False
    >>> has_format_brackets('{{}}')
    False
    """
    stack: list[str] = []
    mapping = {"}": "{"}
    balanced = True
    for char in value:
        if char == '}':
            top_element = stack.pop() if stack else '#'
            if mapping[char] != top_element:
                balanced = False
                break
        elif char == '{':
            stack.append(char)
    is_valid = not stack if balanced else balanced
    if not is_valid:
        return is_valid
    left_count = value.count('{')
    right_count = value.count('}')
    escaped_left = value.count('{{')
    escaped_right = value.count('}}')
    return (
        (left_count - (escaped_left * 2) != 0)
        and (right_count - (escaped_right * 2) != 0)
        and (left_count == right_count)
    )
