from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar
from uuid import uuid4

ItemT = TypeVar("ItemT")


@dataclass(frozen=True)
class User:
    username: str
    hashed_password: str
    first_name: str
    last_name: str
    email: str
    phone_number: str

    is_admin: bool

    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class Service:
    service: str
    superuser: str


@dataclass(frozen=True)
class ServiceMetadata:
    user_id: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class UserMetadata:
    service: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class Client:
    client_id: str
    hashed_secret: str


@dataclass(frozen=True)
class ServiceUserInfo(Generic[ItemT]):
    user: User
    is_superuser: bool
    metadata: ItemT
