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
    auth_time: int = None
    jti: str = None
    iss: str = None
    aud: str = None
    sub: str = None
    typ: str = None
    azp: str = None
    sid: str = None
    acr: str = None
    allowed_origins: List[str] = None
    realm_access: RealmAccess = None
    resource_access: ResourceAccess = None
    scope: str = None
    email_verified: bool = None
    name: str = None
    preferred_username: str = None
    given_name: str = None
    family_name: str = None
    email: str = None
    accountId: str = None
