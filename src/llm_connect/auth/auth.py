from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jwt import PyJWKClient, PyJWKClientError, get_unverified_header

from llm_connect import logger
from llm_connect.configs import key_cloak
from llm_connect.configs.auth import SECRET
from llm_connect.types import Payload

# fetch the public key
jwk_client = PyJWKClient(key_cloak.JWK_URL)


def get_public_key(token: str):

    logger.debug(key_cloak.JWK_URL)

    signing_key = jwk_client.get_signing_key_from_jwt(token)
    return signing_key.key


security = HTTPBearer()


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Payload:
    token = credentials.credentials

    try:
        header = get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token format")

    if header.get("kid"):
        try:
            public_key = get_public_key(token)
            return jwt.decode(
                token,
                public_key,
                algorithms=[key_cloak.ALGORITHM],
                audience=key_cloak.AUDIENCE,
                issuer=f"{key_cloak.URL()}",
            )
        except (JWTError, PyJWKClientError):
            raise HTTPException(status_code=401, detail="Invalid Keycloak token")

    # custom token
    try:
        return jwt.decode(
            token,
            SECRET(),
            algorithms=["HS256"],
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid custom token")
