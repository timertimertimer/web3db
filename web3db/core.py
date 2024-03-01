import random
from typing import Union

import base58
from eth_account import Account as EVMAccount
from aptos_sdk.account import Account as AptosAccount
from solana.rpc.api import Keypair
from sqlalchemy import Result, func, Sequence, delete, and_, not_, desc, Select, Update, Delete, case
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from web3db.models import *
from web3db.utils import logger
from web3db.utils.encrypt_private import encrypt

ModelType = Union[type(Email), type(Discord), type(Twitter), type(Github), type(Proxy), type(Profile)]
INDIVIDUAL_PROXY_LIMIT = 3
SHARED_PROXY_LIMIT = 1


class DBHelper:

    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    async def add_record(self, record: ModelType | list) -> ModelType | None:
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
            stmt: Select | Delete | Update | list
    ) -> Result:
        logger.info(stmt)
        async with self.session_factory() as session:
            if not isinstance(stmt, list):
                stmt = [stmt]
            for s in stmt:
                result = await session.execute(s)
            await session.commit()
            return result

    async def get_row_by_login(self, login: str, model) -> ModelType | None:
        if model == Proxy:
            query = select(model).where(model.proxy_string == login).options(joinedload('*'))
        else:
            query = select(model).where(model.login == login).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().first()

    async def add_email(self, login: str, password: str) -> None:
        logger.info(f'Adding Email {login}:{password}')
        await self.add_record(Email(login=login, password=password))

    async def add_twitter(
            self,
            auth_token: str,
            login: str = None,
            password: str = None,
            email: str = None,
            email_password: str = None
    ) -> None:
        logger.info(f'Adding Twitter {auth_token}')
        mail = (await self.get_row_by_login(email, Email)
                or Email(login=email, password=email_password)) if email else None
        await self.add_record(
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
        email = ((await self.get_row_by_login(login, Email))
                 or Email(login=login, password=email_password)) if login else None
        await self.add_record(
            Discord(
                login=login,
                password=password,
                auth_token=auth_token,
                email=email
            )
        )

    async def add_proxy(self, proxy_string: str) -> None:
        logger.info(f'Adding Proxy {proxy_string}')
        await self.add_record(Proxy(proxy_string=proxy_string))

    async def add_github(self, login: str, password: str, email_password: str = None):
        logger.info(f'Adding Github {login}')
        email = (await self.get_row_by_login(login=login, model=Email)) or Email(login=login, password=email_password)
        await self.add_record(Github(login=login, password=password, email=email))

    async def add_profile(
            self,
            proxy_string: str,
            email: str,
            discord_login: str,
            twitter_login: str,
            evm_private: str,
            aptos_private: str,
            solana_private: str,
            recipient: str,
            passphrase: str
    ) -> None:
        logger.info(f'Adding Profile {email}:{proxy_string}')
        mail = await self.get_row_by_login(email, Email)
        if not mail:
            logger.error(f'Need email {email}')
            return
        discord = await self.get_row_by_login(discord_login, Discord)
        if not discord:
            logger.error(f'Need discord {discord_login}')
            return
        twitter = await self.get_row_by_login(twitter_login, Twitter)
        if not twitter:
            logger.error(f'Need twitter {twitter_login}')
            return
        proxy = await self.get_row_by_login(proxy_string, Proxy)
        if not proxy:
            logger.error(f'Need proxy {proxy_string}')
            return
        evm_account = EVMAccount.from_key(evm_private)
        aptos_account = AptosAccount.load_key(aptos_private)
        solana_keypair = Keypair.from_base58_string(solana_private)
        evm_private_encoded = encrypt(evm_private, recipient, passphrase)
        aptos_private_encoded = encrypt(aptos_private, recipient, passphrase)
        solana_private_encoded = encrypt(solana_private, recipient, passphrase)
        await self.add_record(
            Profile(
                proxy=proxy,
                email=email,
                discord=discord,
                twitter=twitter,
                evm_address=evm_account.address,
                aptos_address=str(aptos_account.address()),
                solana_address=str(solana_keypair.pubkey()),
                evm_private=evm_private_encoded,
                aptos_private=aptos_private_encoded,
                solana_private=solana_private_encoded
            )
        )

    async def edit(self, edited_model: ModelType | list) -> ModelType | None:
        if isinstance(edited_model, list):
            logger.info(f'Editing rows {[el.id for el in edited_model]} in "{edited_model[0].__tablename__}" table')
        else:
            logger.info(f'Editing row with {edited_model.id} id in "{edited_model.__tablename__}" table')
        return await self.add_record(edited_model)

    async def delete(self, models: ModelType | list) -> None:
        if not isinstance(models, list):
            models = [models]
        ids = [model.id for model in models]
        logger.info(f'Deleting rows with {", ".join(map(str, ids))} ids from "{models[0].__tablename__}" table')
        query = delete(type(models[0])).where(type(models[0]).id.in_(ids))
        await self._exec_stmt(query)

    async def get_all_from_table(self, model: ModelType, limit: int = None):
        logger.info(f'Getting all rows from "{model.__tablename__}" table')
        query = select(model).options(joinedload('*')).limit(limit).order_by(model.id)
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_row_by_id(self, id_: int, model: ModelType) -> ModelType:
        logger.info(f'Getting row with {id_} id from "{model.__tablename__}" table')
        query = select(model).where(model.id == id_).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().first()

    async def get_rows_by_id(self, ids: list[int], model: ModelType) -> Sequence[ModelType]:
        logger.info(f'Getting rows with {", ".join(map(str, ids))} ids from "{model.__tablename__}" table')
        query = select(model).filter(model.id.in_(ids)).order_by(model.id).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_profiles_light_by_model(
            self,
            model: ModelType,
            ids: list[int] = None,
            limit: int = None
    ) -> list[tuple[int, str, bool]]:
        logger.info(f'Getting profiles by id (light with model)')
        query = (
            select(Profile.id, model.proxy_string if model == Proxy else model.login, model.ready)
            .join(model).order_by(Profile.id)
        )
        if ids:
            query = query.filter(Profile.id.in_(ids))
        result = await self._exec_stmt(query.limit(limit))
        return [tuple(el) for el in result.all()]

    async def get_profile_by_models_login(self, model: ModelType, login: str) -> Profile:
        logger.info(f'Getting {model.__name__} by login - {login}')
        query = select(Profile).where(model.login == login).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().first()

    async def get_random_profile(self) -> Profile:
        logger.info(f'Getting random profile')
        query = select(Profile).order_by(func.random()).options(joinedload('*'))
        result = await self._exec_stmt(query)
        return result.scalars().first()

    async def get_random_profiles_by_proxy(self, limit: int = None) -> Sequence[Profile]:
        logger.info(f'Getting random profiles by proxy')
        subquery = (
            select(
                func.row_number().over(
                    partition_by=Profile.proxy_id,
                    order_by=func.random()
                ).label('rn'),
                Profile
            )
            .alias('subquery')
        )
        query = (
            select(Profile)
            .join(subquery, subquery.c.id == Profile.id)
            .where(subquery.c.rn == 1)
            .options(joinedload('*'))
            .limit(limit)
        )
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_random_profiles_ids_by_proxy(self, limit: int = None) -> Sequence[int]:
        logger.info(f'Getting random profiles by proxy (light with social)')
        subquery = (
            select(
                func.row_number().over(
                    partition_by=Profile.proxy_id,
                    order_by=func.random()
                ).label('rn'),
                Profile
            )
            .alias('subquery')
        )
        query = (
            select(Profile.id)
            .join(Proxy)
            .join(subquery, subquery.c.id == Profile.id)
            .where(subquery.c.rn == 1)
            .limit(limit)
        )
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_ready_profiles_by_model(self, model: ModelType, limit: int = None) -> Sequence[Profile]:
        logger.info(f'Getting ready {model.__name__.lower()} profiles')
        query = (
            select(Profile).join(model).where(model.ready).options(joinedload('*')).limit(limit).order_by(Profile.id)
        )
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_ready_profiles_ids_by_model(self, model: ModelType, limit: int = None) -> Sequence[int]:
        logger.info(f'Getting ready {model.__name__.lower()} profiles (light with social)')
        query = select(Profile.id).join(model).where(model.ready).limit(limit)
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_potential_profiles(self, limit: int = None) -> list[Profile]:
        free_proxies: list[Proxy] = await self.get_free_proxies(limit=limit)
        free_proxies_count = sum([el[-1] for el in free_proxies])
        free_emails: list[Email] = await self.get_free_emails(limit=limit or free_proxies_count)
        free_discords: list[Discord] = await self.get_free_model(Discord, limit=limit or free_proxies_count)
        free_twitters: list[Twitter] = await self.get_free_model(Twitter, limit=limit or free_proxies_count)
        free_proxies_all = []
        for free_proxy, n in free_proxies:
            free_proxies_all += [free_proxy] * n
        random.shuffle(free_proxies_all)
        potential_profiles = []
        for i, free_proxy in enumerate(free_proxies_all):
            potential_profiles.append(Profile(
                email=free_emails[i] if i < len(free_emails) else None,
                discord=free_discords[i] if i < len(free_discords) else None,
                twitter=free_twitters[i] if i < len(free_twitters) else None,
                proxy=free_proxy
            ))
        return potential_profiles

    async def create_profiles_from_free(
            self,
            recipient: str,
            passphrase: str,
            limit: int = None
    ) -> list[Profile]:
        potential_profiles = await self.get_potential_profiles(limit)
        for i, profile in enumerate(potential_profiles):
            evm_account = EVMAccount.create()
            aptos_account = AptosAccount.generate()
            solana_keypair = Keypair()
            profile.evm_private = encrypt(evm_account.key.hex(), recipient, passphrase)
            profile.evm_address = evm_account.address
            profile.aptos_private = encrypt(aptos_account.private_key.hex(), recipient, passphrase)
            profile.aptos_address = str(aptos_account.address())
            profile.solana_private = encrypt(
                base58.b58encode(solana_keypair.secret() + bytes(solana_keypair.pubkey())).decode(),
                recipient, passphrase
            )
            profile.solana_address = str(solana_keypair.pubkey())
        result = await self.add_record(potential_profiles)
        return result

    async def get_free_emails(self, limit: int = None) -> Sequence[Email]:
        logger.info(f'Getting free mails')
        subquery = (
            select(Twitter.email_id)
            .where(Twitter.email_id.isnot(None))
            .union(select(Profile.email_id).where(Profile.email_id.isnot(None)))
        )
        query = (
            select(Email)
            .where(and_(~Email.id.in_(subquery), not_(Email.login.ilike('%.ru'))))
            .order_by(Email.id)
            .limit(limit)
        )
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_free_model(
            self,
            model: type(Twitter) | type(Discord) | type(Github),
            limit: int = None
    ) -> Sequence[Twitter | Discord | Github]:
        logger.info(f'Getting free {model.__tablename__}')
        query = (
            select(model)
            .where(~model.id.in_(
                select(getattr(Profile, model.__name__.lower() + '_id'))
                .where(getattr(Profile, model.__name__.lower() + '_id').isnot(None))))
            .order_by(model.id)
            .options(joinedload(model.email))
            .limit(limit)
        )
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_free_proxies(self, limit: int = None) -> Sequence[Proxy]:
        logger.info(f'Getting free proxies')
        query = (
            select(Proxy, case(
                (Proxy.proxy_type == 'individual', INDIVIDUAL_PROXY_LIMIT - func.count(Profile.proxy_id)),
                (Proxy.proxy_type == 'shared', SHARED_PROXY_LIMIT - func.count(Profile.proxy_id))
            ).label('count_1')).outerjoin(Profile).group_by(Proxy).having(
                (Proxy.proxy_type == 'individual' and func.count(Profile.proxy_id) < 3) or
                (Proxy.proxy_type == 'shared' and func.count(Profile.proxy_id) < 2)
            ).order_by(desc('count_1')).limit(limit)
        )
        result = await self._exec_stmt(query)
        return result.all()

    async def change_profile_model(
            self,
            profile_ids: int | list[int],
            model: ModelType,
            delete_model: bool = False,
            delete_models_email: bool = False
    ) -> ModelType | None:
        if isinstance(profile_ids, int):
            profile_ids = [profile_ids]
        logger.info(f'Changing {model.__name__.lower()} for {profile_ids} profiles')
        profiles: list[Profile] = await self.get_rows_by_id(profile_ids, Profile)
        models_to_delete: list[model] = [getattr(profile, model.__name__.lower()) for profile in profiles]
        if model in (Twitter, Discord, Github):
            free_models_rows = await self.get_free_model(model, limit=len(profile_ids))
        elif model == Proxy:
            free_models_rows = await self.get_free_proxies(limit=len(profile_ids))
        elif model == Email:
            free_models_rows = await self.get_free_emails(limit=len(profile_ids))
        for profile, model in zip(profiles, free_models_rows):
            logger.info(f'{profile.id} | Old {type(model).__name__.lower()} {getattr(profile, type(model).__name__.lower())}')
            setattr(profile, type(model).__name__.lower(), model)
            logger.info(f'{profile.id} | New {type(model).__name__.lower()} {getattr(profile, type(model).__name__.lower())}')
        edited_profile = await self.edit(profiles)
        if delete_model:
            logger.info(f"{model.__tablename__.capitalize()} {models_to_delete} will be deleted")
            emails_to_delete = [getattr(model, 'email') for model in models_to_delete]
            await self.delete(models_to_delete)
            if delete_models_email:
                logger.info(f'Emails {emails_to_delete} will be deleted')
                await self.delete(emails_to_delete)
        return edited_profile
