from typing import Type

from sqlalchemy import Select, Delete, Update, Result, delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, selectinload
from web3db.utils import my_logger


class BaseDBHelper:
    def __init__(self, url: str, engine_echo: bool = False, query_echo: bool = False):
        self.engine = create_async_engine(url=url, echo=engine_echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )
        self.query_echo = query_echo

    async def create_all_tables(self, base: Type[DeclarativeBase]):
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    async def add_record(self, record: type(DeclarativeBase) | list) -> type(DeclarativeBase) | None:
        if self.query_echo:
            if not record:
                my_logger.info(f'Nothing to add. Record - {record}')
                return
            if isinstance(record, list):
                my_logger.info(f'Adding rows {[el.id for el in record]} in "{record[0].__tablename__}" table')
            else:
                my_logger.info(f'Adding row with {record.id} id in "{record.__tablename__}" table')
        async with self.session_factory() as session:
            try:
                if isinstance(record, list):
                    session.add_all(record)
                else:
                    session.add(record)
                await session.commit()
                return record
            except IntegrityError as e:
                await session.rollback()
                if self.query_echo:
                    my_logger.debug(e)

    async def execute_query(self, stmt: Select | Delete | Update | list[Select | Delete | Update]) -> Result:
        if self.query_echo:
            my_logger.info(stmt)
        async with self.session_factory() as session:
            if not isinstance(stmt, list):
                stmt = [stmt]
            for s in stmt:
                result = await session.execute(s)
            await session.commit()
            return result

    async def edit(self, edited_model: type(DeclarativeBase) | list) -> type(DeclarativeBase) | None:
        if self.query_echo:
            if isinstance(edited_model, list):
                my_logger.info(
                    f'Editing rows {[el.id for el in edited_model]} in "{edited_model[0].__tablename__}" table')
            else:
                my_logger.info(f'Editing row with {edited_model.id} id in "{edited_model.__tablename__}" table')
        return await self.add_record(edited_model)

    async def delete(self, models: type(DeclarativeBase) | list) -> None:
        if not isinstance(models, list):
            models = [models]
        ids = [model.id for model in models]
        if self.query_echo:
            my_logger.info(f'Deleting rows with {", ".join(map(str, ids))} ids from "{models[0].__tablename__}" table')
        query = delete(type(models[0])).where(type(models[0]).id.in_(ids))
        await self.execute_query(query)

    async def get_all_from_table(self, model: type(DeclarativeBase), limit: int = None):
        if self.query_echo:
            my_logger.info(f'Getting all rows from "{model.__tablename__}" table')
        query = select(model).options(selectinload('*')).limit(limit).order_by(model.id)
        result = await self.execute_query(query)
        return result.scalars().all()

    async def get_row_by_id(self, id_: int, model: type(DeclarativeBase)) -> type(DeclarativeBase):
        if self.query_echo:
            my_logger.info(f'Getting row with {id_} id from "{model.__tablename__}" table')
        query = select(model).where(model.id == id_).options(selectinload('*'))
        result = await self.execute_query(query)
        return result.scalars().first()

    async def get_rows_by_id(self, ids: list[int], model: type(DeclarativeBase)) -> list[type(DeclarativeBase)]:
        if self.query_echo:
            my_logger.info(f'Getting rows with {", ".join(map(str, ids))} ids from "{model.__tablename__}" table')
        query = select(model).filter(model.id.in_(ids)).order_by(model.id).options(selectinload('*'))
        result = await self.execute_query(query)
        return result.scalars().unique().all()
