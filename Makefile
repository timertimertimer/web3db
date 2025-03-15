ALEMBIC = alembic
LOCAL_CONFIG = alembic_local\alembic.ini
REMOTE_CONFIG = alembic_remote\alembic.ini

revision_local:
	$(ALEMBIC) -c $(LOCAL_CONFIG) revision --autogenerate

revision_remote:
	$(ALEMBIC) -c $(REMOTE_CONFIG) revision --autogenerate

migrate_local:
	$(ALEMBIC) -c $(LOCAL_CONFIG) upgrade head

migrate_remote:
	$(ALEMBIC) -c $(REMOTE_CONFIG) upgrade head

downgrade_local:
	$(ALEMBIC) -c $(LOCAL_CONFIG) downgrade -1

downgrade_remote:
	$(ALEMBIC) -c $(REMOTE_CONFIG) downgrade -1
