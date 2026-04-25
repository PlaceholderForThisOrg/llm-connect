import os


def MONGODB_CONNECTION_STRING():
    return os.environ["MONGODB_CONNECTION_STRING"]


def MONGODB_DBNAME():
    return os.environ["MONGODB_DBNAME"]
