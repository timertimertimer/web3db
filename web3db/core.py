from sqlalchemy import Result, func, Sequence, delete, and_, not_, Table
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
            record: Email | Discord | Twitter | Profile | Proxy
    ) -> Email | Discord | Twitter | Profile | Proxy | None:
        async with self.session_factory() as session:
            try:
                session.add(record)
                await session.commit()
                logger.info(record)
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

    async def _check_record(self, login: str, table) -> Email | Twitter | Discord | Proxy | None:
        async with self.session_factory() as session:
            result = (await session.execute(
                select(table).where(table.proxy_string == login))).first() if table == Proxy else (
                await session.execute(select(table).where(table.login == login))).first()
            return result[0] if result else None

    async def add_email(self, login: str, password: str) -> None:
        logger.info(f'adding Email {login}:{password}')
        await self._add_record(Email(login=login, password=password))

    async def add_twitter(
            self,
            auth_token: str,
            login: str = None,
            password: str = None,
            email: str = None,
            email_password: str = None
    ) -> None:
        logger.info(f'adding Twitter {auth_token}')
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
            user_agent: str = DEFAULT_UA,
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
                user_agent=user_agent,
                proxy=proxy,
                email=email,
                discord=discord,
                twitter=twitter,
                evm_private=evm_private_encoded
            )
        )

    async def edit(self, edited_table: Twitter | Discord | Email | Profile | Proxy) -> None:
        logger.info(f'Editing {edited_table.id} profile')
        await self._add_record(edited_table)

    async def delete(self, table: Twitter | Discord | Email | Profile | Proxy) -> None:
        logger.info(f'Deleting {table.__tablename__}')
        query = delete(type(table)).where(table.id == type(table).id)
        await self._exec_stmt(query)

    async def get_all_from_table(self, table) -> Sequence[Profile]:
        logger.info(f'Getting all {table.__tablename__}')
        query = select(table).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_profile_by_id(self, id_: int) -> Profile:
        logger.info(f'Getting {id_} profile')
        query = select(Profile).where(Profile.id == id_).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().first()

    async def get_profiles_by_id(self, ids: list[int]) -> Sequence[Profile]:
        logger.info(f'Getting profiles by id')
        query = select(Profile).filter(Profile.id.in_(ids)).order_by(Profile.id).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_profiles_by_id_light(self, social: str, ids: list[int] = None) -> list:
        logger.info(f'Getting profiles by id (light with social)')
        match social:
            case 'twitter':
                query = select(Profile.id, Twitter.login, Profile.proxy.proxy_string).join(Profile.twitter).join(
                    Profile.proxy)
            case 'discord':
                query = select(Profile.id, Discord.login, Profile.proxy.proxy_string).join(Profile.discord).join(
                    Profile.proxy)
            case _:
                query = ()
        query = query.order_by(Profile.id)
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

    async def get_random_profiles_by_proxy_distinct(self) -> Sequence[Profile]:
        logger.info(f'Getting random profiles by proxy distinct')
        query = (select(Profile).join(Profile.proxy).distinct(Proxy.proxy_string)
                 .order_by(Proxy.proxy_string, func.random()).options(joinedload('*')))
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_random_profiles_by_proxy_distinct_light(self, social: str) -> list:
        logger.info(f'Getting random profiles by proxy distinct (light with social)')
        match social:
            case 'twitter':
                query = (select(Profile.id, Twitter.login, Profile.proxy.proxy_string)
                         .join(Profile.twitter).join(Profile.proxy))
            case 'discord':
                query = (select(Profile.id, Discord.login, Profile.proxy.proxy_string)
                         .join(Profile.discord).join(Profile.proxy))
            case _:
                query = ()
        query = (
            query.distinct(Profile.proxy.proxy_string)
            .order_by(Profile.proxy.proxy_string, func.random())
            .subquery('random_proxy_profiles')
        )
        query = select(query).order_by(query.c.id)
        result = await self._exec_stmt(query)
        return [tuple(el) for el in result.all()]

    async def get_potential_profiles(self, n: int = None) -> list[Profile]:
        free_proxies = (await self.get_free_proxies(limit=n))
        free_emails = (await self.get_free_emails(limit=n))
        free_discords = (await self.get_free_discords(limit=n))
        free_twitters = (await self.get_free_twitters(limit=n))
        return [
            Profile(email=free_email, proxy=free_proxy, discord=free_discord, twitter=free_twitter)
            for free_email, free_proxy, free_discord, free_twitter in
            zip(free_emails, free_proxies, free_discords, free_twitters)
        ]

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
        query = (select(Twitter).where(~Twitter.id.in_(select(Profile.twitter_id)))
                 .options(joinedload(Twitter.email)).limit(limit))
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_free_proxies(self, limit: int = None) -> Sequence[Proxy]:
        logger.info(f'Getting free twitters')
        query = select(Proxy).where(~Proxy.id.in_(select(Profile.proxy_id))).limit(limit)
        result = await self._exec_stmt(query)
        return result.scalars().all()


async def add_encrypted_private_to_profile(db: DBHelper, id_: int, private_key: str, recipient: str) -> None:
    profile: Profile = await db.get_profile_by_id(id_)
    profile.evm_private = encrypt(private_key, recipient)
    await db.edit(profile)
