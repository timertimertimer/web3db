ALEMBIC = alembic
CONFIG = alembic\alembic.ini

revision:
	$(ALEMBIC) -c $(CONFIG) revision --autogenerate

migrate:
	$(ALEMBIC) -c $(CONFIG) upgrade head

downgrade_local:
	$(ALEMBIC) -c $(CONFIG) downgrade -1
