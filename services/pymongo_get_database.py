from pymongo import MongoClient
from dotenv import load_dotenv

import os


# load .env vars in every file we use them
load_dotenv()
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")


def get_database():
    client = MongoClient(MONGODB_CONNECTION_STRING)
    database = client["db1"]

    return database
