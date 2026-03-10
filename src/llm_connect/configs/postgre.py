import os


def POSTGRE_URI():
    return os.environ["POSTGRE_URI"]


def POSTGRE_URL_v1():
    return os.environ["POSTGRE_URI_v1"]
