import os

SERVICE_NAME = "s3"


def ENDPOINT_URL():
    return os.environ["ENDPOINT_URL"]


def AWS_ACCESS_KEY_ID():
    return os.environ["AWS_ACCESS_KEY_ID"]


def AWS_SECRET_ACCESS_KEY_ID():
    return os.environ["AWS_SECRET_ACCESS_KEY_ID"]
