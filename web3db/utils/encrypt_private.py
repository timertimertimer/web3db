import gnupg

from .logger import logger

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


def decrypt(encoded_data: str, passphrase: str) -> str:
    status = gpg.decrypt(encoded_data, passphrase=passphrase)
    logger.info(status.status)
    return status.data.decode('utf-8')
