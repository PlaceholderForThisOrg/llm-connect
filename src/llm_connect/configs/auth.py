import os


def SECRET():
    return os.environ["JWT_SECRET"]
