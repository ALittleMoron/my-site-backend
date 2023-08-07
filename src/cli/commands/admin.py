from typer import secho

from app.core.meta import Session
from app.core.models.tables.admins import Admin


async def create_admin_command(username: str, password: str):
    """Функция создания нового администратора в базе данных."""
    async with Session() as session:
        try:
            admin = Admin(username=username, password=password)
            session.add(admin)
            await session.commit()
        except Exception as exc:
            secho(f'Внутренняя ошибка: {exc}', fg='red')
        else:
            secho('Администратор успешно создан.', fg='green')
