import gnupg
from eth_account import Account

from .logger import logger
from ..models import Profile

gpg = gnupg.GPG()
gpg.encoding = 'utf-8'


def encrypt(data: str, recipient: str, passphrase: str) -> str:
    status = gpg.encrypt(
        data=data,
        recipients=recipient,
        passphrase=passphrase,
        sign=recipient
    )
    logger.info(status.status)
    return status.data.decode('utf-8')


def decrypt(encoded_data: str, passphrase: str, echo: bool = False) -> str:
    status = gpg.decrypt(encoded_data, passphrase=passphrase)
    if echo:
        logger.info(status.status)
    return status.data.decode('utf-8')


def get_wallets(profiles: list[Profile], passphrase: str) -> list[Account]:
    return [Account.from_key(decrypt(profile.evm_private, passphrase)) for profile in profiles]
