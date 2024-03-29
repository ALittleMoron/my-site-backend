"""Модуль нужен только для того, чтобы исполнять его в ipython оболочке.

Здесь выводится сообщение с описанием особенностей кастомных настроек оболочки с примерами.
"""
print(  # noqa
    '\033[93m'
    '\nВнимание!'
    '\n\nДанная оболочка была запущена с пред-импортированными модулями (tables) и функцией '
    'создания сессии к базе данных (get_session - генератор). Также в оболочке установлен плагин'
    'autoreload, который автоматически перезагружает все импортированные источники, если '
    'их исходный код был изменен, поэтому не нужно перезапускать оболочку после каждого изменения.'
    '\n\nПримеры Использования пред-импортированных модулей и функций:\n\n'
    '\033[0m'
    '\033[92mIn [1]:\033[0m tables.Base\n'
    '\033[91mOut[1]:\033[0m app.core.models.tables.base.Base\n\n'
    '\033[92mIn [2]:\033[0m session = await anext(get_session())\n\n'
    '\033[92mIn [3]:\033[0m session\n'
    '\033[91mOut[2]:\033[0m <sqlalchemy.ext.asyncio.session.AsyncSession at 0x7f7996e126d0>\n\n'
    '\033[92mА теперь попробуйте сами!\033[0m',
)
