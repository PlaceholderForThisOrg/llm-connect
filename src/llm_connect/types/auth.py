from typing import List, TypedDict


class RealmAccess(TypedDict):
    roles: List[str]


class ResourceRoles(TypedDict):
    roles: List[str]


class ResourceAccess(TypedDict):
    account: ResourceRoles


class Payload(TypedDict):
    exp: int
    iat: int
    auth_time: int
    jti: str
    iss: str
    aud: str
    sub: str
    typ: str
    azp: str
    sid: str
    acr: str
    allowed_origins: List[str]
    realm_access: RealmAccess
    resource_access: ResourceAccess
    scope: str
    email_verified: bool
    name: str
    preferred_username: str
    given_name: str
    family_name: str
    email: str
