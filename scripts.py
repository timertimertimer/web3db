import asyncio
import csv
from pathlib import Path

from web3db import *
from web3db.core import create_db_instance

data_folder = Path.cwd() / 'data'
db = create_db_instance()
cexs = {
    'bybits.csv': ByBit,
    'mexcs.csv': Mexc
}


async def add_cexs(file_name: str):
    with open(data_folder / file_name, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=':', fieldnames=['email', 'password', 'totp_secret'])
        for row in reader:
            email: Email = await db.get_row_by_login(row['email'], Email)
            new_cex = cexs[file_name](email=email, password=row['password'], totp_secret=row.get('totp_secret'))
            await db.add_record(new_cex)


async def add_emails(file_name: str = 'emails.csv'):
    with open(data_folder / file_name, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=':')
        emails = []
        for row in reader:
            emails.append(Email(
                login=row['login'], password=row['password'],
                totp_secret=row.get('totp_secret'), refresh_token=row.get('refresh_token'),
                client_id=row.get('client_id')
            ))
        await db.add_record(emails)


if __name__ == '__main__':
    asyncio.run(add_emails())
