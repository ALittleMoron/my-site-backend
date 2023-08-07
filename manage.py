"""Пакет менеджера командного интерфейса для приложения.

Написан с использованием библиотеки typer: https://typer.tiangolo.com
"""
import pathlib
import sys

sys.path.insert(0, (pathlib.Path(__file__).absolute().parent / 'src').as_posix())


from cli import cli

cli()
