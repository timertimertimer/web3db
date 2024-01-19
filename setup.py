from setuptools import setup, find_packages

DESCRIPTION = 'Streaming video data via networks'
LONG_DESCRIPTION = 'A package that allows to build simple streams of video, audio and camera data.'

# Setting up
setup(
    name="web3db",
    version='0.0.1',
    author="timer",
    author_email="timerkhan2002@gmail.com",
    description='Web3 database',
    packages=find_packages(),
    install_requires=['python-gnupg', 'loguru', 'sqlalchemy', 'asyncpg'],
    keywords=['web3', 'database', 'db', 'twitter', 'discord'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ]
)