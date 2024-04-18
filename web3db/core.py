import random
from typing import Union, Callable

import base58
from mnemonic import Mnemonic
from eth_account import Account as EVMAccount
from aptos_sdk.account import Account as AptosAccount
from solana.rpc.api import Keypair
from bitcoinutils.hdwallet import HDWallet
from bitcoinutils.setup import setup
from sqlalchemy import Result, func, delete, and_, not_, desc, Select, Update, Delete, case
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
setup('mainnet')


def prepare_strings(*s):
    return [string.strip() if string else string for string in s]


class DBHelper:

    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    def prepare_values(func: Callable):
        async def wrapper(self, *args):
            return await func(self, *prepare_strings(*args))

        return wrapper

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

    async def get_rows_by_id(self, ids: list[int], model: ModelType) -> list[ModelType]:
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

    async def get_random_profiles_by_proxy(self, limit: int = None) -> list[Profile]:
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

    async def get_random_profiles_ids_by_proxy(self, limit: int = None) -> list[int]:
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

    async def get_ready_profiles_by_model(self, model: ModelType, limit: int = None) -> list[Profile]:
        logger.info(f'Getting ready {model.__name__.lower()} profiles')
        query = (
            select(Profile).join(model).where(model.ready).options(joinedload('*')).limit(limit).order_by(Profile.id)
        )
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_ready_profiles_ids_by_model(self, model: ModelType, limit: int = None) -> list[int]:
        logger.info(f'Getting ready {model.__name__.lower()} profiles (light with social)')
        query = select(Profile.id).join(model).where(model.ready).limit(limit)
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_profiles_with_totp_by_model(self, model: ModelType, limit: int = None) -> list[Profile]:
        logger.info(f'Getting {model.__name__.lower()} profiles with totp (light with social)')
        query = (
            select(Profile)
            .join(model)
            .where(model.totp_secret != None)
            .options(joinedload(getattr(Profile, model.__name__.lower())))
            .limit(limit)
            .order_by(Profile.id)
        )
        result = await self._exec_stmt(query)
        return result.scalars().all()

    async def get_potential_profiles(self, limit: int = None) -> list[Profile]:
        unused_proxies: list[tuple[Proxy, int]] = await self.get_unused_proxies(limit=limit)
        unused_proxies_count = sum([el[-1] for el in unused_proxies])
        unused_emails: list[Email] = await self.get_unused_emails(limit=limit or unused_proxies_count)
        unused_discords: list[Discord] = await self.get_unused_model(Discord, limit=limit or unused_proxies_count)
        unused_twitters: list[Twitter] = await self.get_unused_model(Twitter, limit=limit or unused_proxies_count)
        unused_proxies_all = []
        for unused_proxy, n in unused_proxies:
            unused_proxies_all += [unused_proxy] * n
        random.shuffle(unused_proxies_all)
        potential_profiles = []
        for i, unused_proxy in enumerate(unused_proxies_all):
            potential_profiles.append(Profile(
                email=unused_emails[i] if i < len(unused_emails) else None,
                discord=unused_discords[i] if i < len(unused_discords) else None,
                twitter=unused_twitters[i] if i < len(unused_twitters) else None,
                proxy=unused_proxy
            ))
        return potential_profiles

    async def create_profiles(
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
            btc_mnemo = Mnemonic().generate(256)
            btc_hdwallet = HDWallet(mnemonic=btc_mnemo)
            profile.evm_private = encrypt(evm_account.key.hex(), recipient, passphrase)
            profile.evm_address = evm_account.address
            profile.aptos_private = encrypt(aptos_account.private_key.hex(), recipient, passphrase)
            profile.aptos_address = str(aptos_account.address())
            profile.solana_private = encrypt(
                base58.b58encode(solana_keypair.secret() + bytes(solana_keypair.pubkey())).decode(),
                recipient, passphrase
            )
            profile.solana_address = str(solana_keypair.pubkey())
            profile.btc_mnemo = encrypt(btc_mnemo, recipient, passphrase)
            btc_hdwallet.from_path("m/84'/0'/0'/0/0")
            profile.btc_native_segwit_address = (
                btc_hdwallet.get_private_key().get_public_key().get_segwit_address().to_string()
            )
            btc_hdwallet.from_path("m/86'/0'/0'/0/0")
            profile.btc_taproot_address = (
                btc_hdwallet.get_private_key().get_public_key().get_taproot_address().to_string()
            )
        result = await self.add_record(potential_profiles)
        return result

    async def get_unused_emails(self, limit: int = None) -> list[Email]:
        logger.info(f'Getting unused mails')
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

    async def get_unused_model(
            self,
            model: type(Twitter) | type(Discord) | type(Github),
            limit: int = None
    ) -> list[Twitter | Discord | Github]:
        logger.info(f'Getting unused {model.__tablename__}')
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

    async def get_unused_proxies(self, limit: int = None) -> list[tuple[Proxy, int]]:
        logger.info(f'Getting unused proxies')
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
        unused_models_rows = []
        if model in (Twitter, Discord, Github):
            unused_models_rows = await self.get_unused_model(model, limit=len(profile_ids))
        elif model == Proxy:
            unused_models_rows = await self.get_unused_proxies(limit=len(profile_ids))
        elif model == Email:
            unused_models_rows = await self.get_unused_emails(limit=len(profile_ids))
        for profile, model in zip(profiles, unused_models_rows):
            logger.info(
                f'{profile.id} | Old {type(model).__name__.lower()} {getattr(profile, type(model).__name__.lower())}')
            setattr(profile, type(model).__name__.lower(), model)
            logger.info(
                f'{profile.id} | New {type(model).__name__.lower()} {getattr(profile, type(model).__name__.lower())}')
        edited_profile = await self.edit(profiles)
        if delete_model:
            logger.info(f"{model.__tablename__.capitalize()} {models_to_delete} will be deleted")
            emails_to_delete = [getattr(model, 'email') for model in models_to_delete]
            await self.delete(models_to_delete)
            if delete_models_email:
                logger.info(f'Emails {emails_to_delete} will be deleted')
                await self.delete(emails_to_delete)
        return edited_profile
