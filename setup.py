from setuptools import setup, find_packages

setup(
    name="web3db",
    version='1.0.1',
    author="timer",
    author_email="timerkhan2002@gmail.com",
    description='Web3 database',
    packages=find_packages(),
    url='https://github.com/timertimertimer/web3db',
    install_requires=[
        'python-gnupg', 'loguru',
        'sqlalchemy', 'asyncpg',
        'eth_account', 'aptos-sdk', 'solana', 'base58', 'bitcoin-utils'
    ],
    project_urls={
        "GitHub": "https://github.com/timertimertimer/web3db",
        "Source": "https://github.com/timertimertimer/web3db"
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ]
)
