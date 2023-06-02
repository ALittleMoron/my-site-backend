NAME := src
POETRY := $(shell command -v poetry 2> /dev/null)

.DEFAULT_GOAL := help
mode ?= "dev"
message ?= "default message"
ENV_VARS_PREFIX := PROJECT_RUN_MODE=$(mode)

.PHONY: help
help:
	@echo -e "Пожалуйста, испольйте \033[0;33m'make <target>'\033[0m где <target> одна из"
	@echo ""
	@echo -e "  \033[0;33minstall\033[0m         запускает установку пакеты и подготовку окружение"
	@echo -e "  \033[0;33mclean\033[0m           удаляет все временные файлы"
	@echo -e "  \033[0;33mlint\033[0m            запускает проверку кода"
	@echo -e "  \033[0;33mformat\033[0m          запускает форматирование кода"
	@echo -e "  \033[0;33mtest\033[0m            запускает все тесты проекта"
	@echo -e "  \033[0;33mrevision\033[0m        запускает генерацию пустой миграции"
	@echo -e "  \033[0;33mauto_revision\033[0m   запускает генерацию автоматической миграции"
	@echo -e "  \033[0;33mupgrade\033[0m         запускает применение одной миграции"
	@echo -e "  \033[0;33mupgrade_head\033[0m    запускает применение всех миграций"
	@echo -e "  \033[0;33mdowngrade\033[0m       запускает отмену одной миграции"
	@echo -e "  \033[0;33mdowngrade_base\033[0m  запускает отмену всех миграций"
	@echo ""
	@echo -e "Проверьте \033[0;33mMakefile\033[0m, чтобы понимать, что какая команда делает."

install:
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install

.PHONY: clean
clean:
	find . -type d -name "__pycache__" | xargs rm -rf {};
	rm -rf ./logs/*

.PHONY: lint
lint:
	$(POETRY) run isort --settings-path ./pyproject.toml --check-only $(NAME)
	$(POETRY) run black --config ./pyproject.toml --check $(NAME) --diff
	$(POETRY) run flake8 --config ./.flake8 --ignore=W503,E501 $(NAME)
	$(POETRY) run bandit -r $(NAME) -s B608

.PHONY: format
format:
	$(POETRY) run isort --settings-path ./pyproject.toml $(NAME)
	$(POETRY) run black --config ./pyproject.toml $(NAME)

.PHONY: test
test:
	$(ENV_VARS_PREFIX) $(POETRY) run pytest ./$(NAME)/tests --cov-report term-missing --cov-fail-under 60 --cov ./$(NAME)/app

.PHONY: revision
revision:
	$(ENV_VARS_PREFIX) $(POETRY) run alembic -c $(NAME)/alembic.ini revision -m "$(message)"

.PHONY: auto_revision
auto_revision:
	$(ENV_VARS_PREFIX) $(RUN_PREFIX) $(POETRY) run alembic -c $(NAME)/alembic.ini revision --autogenerate -m "$(message)"

.PHONY: upgrade
upgrade:
	$(ENV_VARS_PREFIX) $(POETRY) run alembic -c $(NAME)/alembic.ini upgrade +1

.PHONY: upgrade_head
upgrade_head:
	$(ENV_VARS_PREFIX) $(POETRY) run alembic -c $(NAME)/alembic.ini upgrade head

.PHONY: downgrade
downgrade:
	$(ENV_VARS_PREFIX) $(POETRY) run alembic -c $(NAME)/alembic.ini downgrade -1

.PHONY: downgrade_base
downgrade_base:
	$(ENV_VARS_PREFIX) $(POETRY) run alembic -c $(NAME)/alembic.ini downgrade base