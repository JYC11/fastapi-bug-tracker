include .env
EXPORT = export PYTHONPATH=$(PWD)


migration:
	$(EXPORT) && pipenv run alembic revision --autogenerate -m "initial tables"

upgrade:
	$(EXPORT) && pipenv run alembic upgrade head

downgrade:
	$(EXPORT) && pipenv run alembic downgrade -1

shell:
	$(EXPORT) && pipenv run python

checks:
	$(EXPORT) && pipenv run sh scripts/checks.sh
