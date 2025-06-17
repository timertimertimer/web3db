import gnupg

from .logger import logger


def encrypt(data: str, passphrase: str, recipient: str) -> str:
    gpg = gnupg.GPG()
    gpg.encoding = 'utf-8'
    status = gpg.encrypt(
        data=data,
        recipients=recipient,
        passphrase=passphrase,
        sign=recipient
    )
    logger.info(status.status)
    return status.data.decode('utf-8')


def decrypt(encoded_data: str, passphrase: str, echo: bool = False) -> str:
    gpg = gnupg.GPG()
    gpg.encoding = 'utf-8'
    status = gpg.decrypt(encoded_data, passphrase=passphrase)
    if echo:
        logger.info(status.status)
    return status.data.decode('utf-8')
