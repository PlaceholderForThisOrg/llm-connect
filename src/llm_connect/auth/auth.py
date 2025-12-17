from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jwt import PyJWKClient

from llm_connect.configs import key_cloak
from llm_connect.types import Payload

# fetch the public key
jwk_client = PyJWKClient(key_cloak.JWK_URL)


def get_public_key(token: str):
    signing_key = jwk_client.get_signing_key_from_jwt(token)
    return signing_key.key


security = HTTPBearer()


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Payload:
    token = credentials.credentials

    public_key = get_public_key(token)
    payload: Payload = jwt.decode(
        token,
        public_key,
        algorithms=[key_cloak.ALGORITHM],
        # audience=key_cloak.AUDIENCE,
        # issuer=f"{key_cloak.URL()}",
    )
    return payload
