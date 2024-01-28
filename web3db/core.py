import random

from eth_account import Account
from sqlalchemy import Result, func, Sequence, delete, and_, not_, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from web3db.models import *
from web3db.utils import logger, DEFAULT_UA
from web3db.utils.encrypt_private import encrypt


class DBHelper:

    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    async def _add_record(
            self,
            record: Email | Discord | Twitter | Profile | Proxy | list
    ) -> Email | Discord | Twitter | Profile | Proxy | None:
        logger.info(record)
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
                logger.debug(e)

    async def _exec_stmt(
            self,
            stmt
    ) -> Result:
        logger.info(stmt)
        async with self.session_factory() as session:
            result = await session.execute(stmt)
            await session.commit()
            return result

    async def _check_record(self, login: str, model) -> Email | Twitter | Discord | Proxy | None:
        async with self.session_factory() as session:
            result = (await session.execute(
                select(model).where(model.proxy_string == login))).first() if model == Proxy else (
                await session.execute(select(model).where(model.login == login))).first()
            return result[0] if result else None

    async def add_email(self, login: str, password: str) -> None:
        logger.info(f'Adding Email {login}:{password}')
        await self._add_record(Email(login=login, password=password))

    async def add_twitter(
            self,
            auth_token: str,
            login: str = None,
            password: str = None,
            email: str = None,
            email_password: str = None
    ) -> None:
        logger.info(f'Adding Twitter {auth_token}')
        mail = (await self._check_record(email, Email)
                or Email(login=email, password=email_password)) if email else None
        await self._add_record(
            Twitter(
                login=login,
                password=password,
                auth_token=auth_token,
                mail=mail
            )
        )

    async def add_discord(
            self,
            auth_token: str,
            login: str = None,
            password: str = None,
            email_password: str = None
    ) -> None:
        logger.info(f'Adding Discord {auth_token}')
        email = ((await self._check_record(login, Email))
                 or Email(login=login, password=email_password)) if login else None
        await self._add_record(
            Discord(
                login=login,
                password=password,
                token=auth_token,
                email=email
            )
        )

    async def add_proxy(self, proxy_string: str) -> None:
        logger.info(f'Adding Proxy {proxy_string}')
        await self._add_record(Proxy(proxy_string=proxy_string))

    async def add_profile(
            self,
            proxy_string: str,
            email: str,
            discord_login: str,
            twitter_login: str,
            evm_private_encoded: str,
    ) -> None:
        logger.info(f'Adding Profile {email}:{proxy_string}')
        mail = await self._check_record(email, Email)
        if not mail:
            logger.error(f'Need email {email}')
            return
        discord = await self._check_record(discord_login, Discord)
        if not discord:
            logger.error(f'Need discord {discord_login}')
            return
        twitter = await self._check_record(twitter_login, Twitter)
        if not twitter:
            logger.error(f'Need twitter {twitter_login}')
            return
        proxy = await self._check_record(proxy_string, Proxy)
        if not proxy:
            logger.error(f'Need proxy {proxy_string}')
            return
        await self._add_record(
            Profile(
                proxy=proxy,
                email=email,
                discord=discord,
                twitter=twitter,
                evm_private=evm_private_encoded
            )
        )

    async def edit(self, edited_model: Twitter | Discord | Email | Profile | Proxy) -> None:
        logger.info(f'Editing row with {edited_model.id} id from {edited_model.__tablename__} table')
        await self._add_record(edited_model)

    async def delete(self, model) -> None:
        logger.info(f'Deleting row with {model.id} id from {model.__tablename__} table')
        query = delete(type(model)).where(model.id == type(model).id)
        await self._exec_stmt(query)

    async def get_all_from_table(self, model, limit: int = None):
        logger.info(f'Getting all rows from {model.__tablename__} table')
        query = select(model).options(joinedload('*')).limit(limit)
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_row_by_id(self, id_: int, model) -> Twitter | Discord | Email | Profile | Proxy:
        logger.info(f'Getting row with {id_} id from {model.__tablename__} table')
        query = select(model).where(model.id == id_).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().first()

    async def get_rows_by_id(self, ids: list[int], model) -> Sequence[Email | Twitter | Discord | Proxy | Profile]:
        logger.info(f'Getting rows with {", ".join(map(str, ids))} ids from {model.__tablename__} table')
        query = select(model).filter(model.id.in_(ids)).order_by(model.id).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_profiles_by_id_light(self, model, ids: list[int] = None) -> list:
        logger.info(f'Getting profiles by id (light with social)')
        query = select(Profile.id, model.login, Proxy.proxy_string).join(model).join(Proxy).order_by(Profile.id)
        if ids:
            query = query.filter(Profile.id.in_(ids))
        result = await self._exec_stmt(query)
        return [tuple(el) for el in result.all()]

    async def get_profile_by_twitter_login(self, login: str) -> Profile:
        logger.info(f'Getting twitter {login}')
        query = select(Profile).where(Profile.twitter.has(Twitter.login == login)).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().first()

    async def get_profile_by_discord_login(self, login: str) -> Profile:
        logger.info(f'Getting discord {login}')
        query = select(Profile).where(Profile.discord.has(Discord.login == login)).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().first()

    async def get_random_profile(self) -> Profile:
        logger.info(f'Getting random profile')
        query = select(Profile).order_by(func.random()).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().first()

    async def get_random_profiles_by_proxy_distinct(self, limit: int = None) -> Sequence[Profile]:
        logger.info(f'Getting random profiles by proxy distinct')
        subquery = (
            select(
                func.row_number().over(
                    partition_by=Profile.proxy_id,
                    order_by=Profile.id
                ).label('row_num'),
                Profile
            )
            .distinct(Profile.proxy_id)
            .alias('subq')
        )
        query = (
            select(Profile)
            .join(subquery, Profile.id == subquery.c.id)
            .options(joinedload('*'))
            .where(subquery.c.row_num == 1)
            .order_by(Profile.id)
            .limit(limit)
        )
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_random_profiles_by_proxy_distinct_light(self, model, limit: int = None) -> list:
        logger.info(f'Getting random profiles by proxy distinct (light with social)')
        query = select(Profile.id, model.login, Proxy.proxy_string).join(model).join(Proxy).distinct(
            Proxy.proxy_string).limit(limit)
        result = await self._exec_stmt(query)
        return [tuple(el) for el in result.all()]

    async def get_potential_profiles(self, limit: int = None, n_for_proxy: int = 3) -> list[Profile]:
        free_proxies = await self.get_free_proxies(limit=limit, n_for_proxy=n_for_proxy)
        free_proxies_count = sum([el[-1] for el in free_proxies])
        free_emails = await self.get_free_emails(limit=limit or free_proxies_count)
        free_discords = await self.get_free_discords(limit=limit or min(len(free_emails), free_proxies_count))
        free_twitters = await self.get_free_twitters(
            limit=limit or min(len(free_emails), len(free_discords), free_proxies_count)
        )
        free_proxies_all = []
        for free_proxy, n in free_proxies:
            free_proxies_all += [free_proxy] * n
        random.shuffle(free_proxies_all)
        potential_profiles = []
        for free_email, free_discord, free_twitter, free_proxy \
                in zip(free_emails, free_discords, free_twitters, free_proxies_all):
            potential_profiles.append(Profile(
                email=free_email,
                discord=free_discord,
                twitter=free_twitter,
                proxy=free_proxy
            ))
        return potential_profiles

    async def create_profiles_from_free(
            self,
            recipient: str,
            passphrase: str,
            evm_privates=None,
            limit: int = None,
            n_for_proxy: int = 3
    ) -> list[Profile]:
        if evm_privates is None:
            evm_privates = []
        potential_profiles = await self.get_potential_profiles(limit, n_for_proxy)
        for i, profile in enumerate(potential_profiles):
            if i < len(evm_privates):
                profile.evm_private = encrypt(evm_privates[i], recipient, passphrase)
            else:
                profile.evm_private = encrypt(Account.create().key.hex(), recipient, passphrase)
        result = await self._add_record(potential_profiles)
        return result

    async def get_free_emails(self, limit: int = None) -> Sequence[Email]:
        logger.info(f'Getting free mails')
        subquery = (
            select(Twitter.email_id)
            .where(Twitter.email_id.isnot(None))
            .union(select(Profile.email_id).where(Profile.email_id.isnot(None)))
        )
        query = select(Email).where(and_(~Email.id.in_(subquery), not_(Email.login.ilike('%.ru')))).limit(limit)
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_free_discords(self, limit: int = None) -> Sequence[Discord]:
        logger.info(f'Getting free discords')
        query = select(Discord).where(
            ~Discord.id.in_(
                select(Profile.discord_id).where(Profile.discord_id.isnot(None))
            )
        ).limit(limit)
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_free_twitters(self, limit: int = None) -> Sequence[Twitter]:
        logger.info(f'Getting free twitters')
        query = (select(Twitter).where(~Twitter.id.in_(select(Profile.twitter_id))).order_by(Twitter.id)
                 .options(joinedload(Twitter.email)).limit(limit))
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_free_proxies(self, limit: int = None, n_for_proxy: int = 3) -> Sequence[Proxy]:
        logger.info(f'Getting free proxies')
        query = (
            select(Proxy, (n_for_proxy - func.count(Profile.proxy_id)).label('count_1')).outerjoin(Profile)
            .group_by(Proxy).having(func.count(Profile.proxy_id) < n_for_proxy).order_by(desc('count_1')).limit(limit)
        )
        result = await self._exec_stmt(query)
        return result.all()


async def add_encrypted_private_to_profile(
        db: DBHelper, id_: int, private_key: str,
        recipient: str, passphrase: str
) -> None:
    existing_profile: Profile = await db.get_row_by_id(id_, Profile)
    existing_profile.evm_private = encrypt(private_key, recipient, passphrase)
    await db.edit(existing_profile)
