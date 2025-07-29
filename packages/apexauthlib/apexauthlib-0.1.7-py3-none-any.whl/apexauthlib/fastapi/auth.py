from dataclasses import dataclass
from typing import Annotated, Any

from apexdevkit.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status

from apexauthlib.entities import User
from apexauthlib.entities.auth import ServiceUserInfo
from apexauthlib.integration.api import AuthApiProvider, AuthCodeApi

auth_api = APIRouter(tags=["Auth"])
AuthApiProviderDependable = Annotated[AuthApiProvider[Any], inject("auth")]
AuthCodeApiDependable = Annotated[AuthCodeApi, inject("auth_code")]


def oauth2() -> OAuth2PasswordBearer:
    return OAuth2PasswordBearer(tokenUrl="auth/login")


TokenDependable = Annotated[str, Depends(oauth2())]


def get_user(
    token: TokenDependable,
    auth: AuthApiProviderDependable,
) -> User:
    try:
        api = auth.for_token(token)
        return api.user()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_metadata(
    token: TokenDependable,
    auth: AuthApiProviderDependable,
) -> Any:
    try:
        api = auth.for_token(token)
        return api.metadata_for(api.user().id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_with_metadata(
    token: TokenDependable,
    auth: AuthApiProviderDependable,
) -> tuple[User, Any]:
    try:
        api = auth.for_token(token)
        user = api.user()
        return user, api.metadata_for(api.user().id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_with_full_metadata(
    token: TokenDependable,
    auth: AuthApiProviderDependable,
) -> ServiceUserInfo[Any]:
    try:
        api = auth.for_token(token)
        return api.full_metadata_for(api.user().id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_and_service_users(
    token: TokenDependable,
    auth: AuthApiProviderDependable,
) -> tuple[ServiceUserInfo[Any], list[ServiceUserInfo[Any]]]:
    try:
        api = auth.for_token(token)
        return api.full_metadata_for(api.user().id), list(api.users_for_service())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@dataclass
class TokenResponse:
    access_token: str
    token_type: str = "Bearer"


@auth_api.post(
    "/login",
    status_code=200,
    response_model=TokenResponse,
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth: AuthApiProviderDependable,
) -> TokenResponse:
    try:
        return TokenResponse(
            access_token=auth.login(form_data.username, form_data.password)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )


@auth_api.post(
    "/login/code",
    status_code=200,
    response_model=TokenResponse,
)
def login_code(
    code: str,
    auth_code: AuthCodeApiDependable,
) -> TokenResponse:
    try:
        return TokenResponse(
            access_token=auth_code.token_for(code),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
