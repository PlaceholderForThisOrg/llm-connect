import os

HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
APP = os.environ["APP"]

ORIGINS = [
    "*",
    "http://localhost:3000",
    "null",
    "http://*:3000",
    "http://localhost:5173",
]
