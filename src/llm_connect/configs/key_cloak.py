import os


def REALM():
    return os.environ["KEYCLOAK_REALM"]


def URL():
    return f'S{os.environ["KEYCLOAK_URL"]}/${REALM()}'


ALGORITHM = "RS256"
AUDIENCE = "account"

JWK_URL = f"{URL()}/protocol/openid-connect/certs"
