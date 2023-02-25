include .env
EXPORT = export PYTHONPATH=$(PWD)


migration:
	$(EXPORT) && pipenv run alembic revision --autogenerate -m "$(MIGR_NAME)"

upgrade:
	$(EXPORT) && pipenv run alembic upgrade head

downgrade:
	$(EXPORT) && pipenv run alembic downgrade -1

shell:
	$(EXPORT) && pipenv run python

checks:
	$(EXPORT) && pipenv run sh scripts/checks.sh

install:
	$(EXPORT) && pipenv install --dev

sync:
	$(EXPORT) && pipenv sync --dev

clean:
	$(EXPORT) && pipenv clean

unit:
	$(EXPORT) && pytest app/tests/unit

integration:
	$(EXPORT) && pytest app/tests/integration

e2e:
	$(EXPORT) && pytest app/tests/e2e

test:
	$(EXPORT) && pytest

test-cov:
	$(EXPORT) && pytest --cov=app

run:
	$(EXPORT) && pipenv run sh scripts/run.sh