import asyncio
import csv
from pathlib import Path
from web3db import *
from web3db.utils.env import Web3dbENV

data_folder = Path.cwd() / 'data'
db = DBHelper(Web3dbENV.REMOTE_CONNECTION_STRING)
cexs = {
    'bybits.csv': ByBit,
    'mexcs.csv': Mexc
}


async def add_cexs(cex_file_name: str):
    with open(data_folder / cex_file_name, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=':', fieldnames=['email', 'password', 'totp_secret'])
        for row in reader:
            email: Email = await db.get_row_by_login(row['email'], Email)
            new_cex = cexs[cex_file_name](email=email, password=row['password'])
            new_cex.totp_secret = row['totp_secret'] if row['totp_secret'] else None
            await db.add_record(new_cex)


if __name__ == '__main__':
    asyncio.run(add_cexs('mexcs.csv'))
