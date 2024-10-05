import os
from dotenv import load_dotenv

load_dotenv()


class Web3dbENV:
    PASSPHRASE = os.getenv("PASSPHRASE")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    CAPMONSTER_API_KEY = os.getenv("CAPMONSTER_API_KEY")

    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    REMOTE_CONNECTION_STRING = os.getenv("REMOTE_CONNECTION_STRING")
    LOCAL_CONNECTION_STRING = os.getenv("LOCAL_CONNECTION_STRING")
