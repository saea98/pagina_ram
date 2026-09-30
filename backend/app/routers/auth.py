from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import current_user, require_csrf
from app.models.users import User
from app.schemas.auth import LoginIn, PasswordForgotIn, PasswordResetIn, UserOut
from app.services import auth as auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=UserOut)
async def login(
    body: LoginIn,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserOut:
    return await auth_service.login(session, response, body.email, body.password)


@router.post("/refresh", response_model=UserOut, dependencies=[Depends(require_csrf)])
async def refresh(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserOut:
    return await auth_service.refresh_session(session, request, response)


@router.post("/logout", status_code=204, dependencies=[Depends(require_csrf)])
async def logout(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    await auth_service.logout(session, request, response)


@router.get("/me", response_model=UserOut)
async def me(user: Annotated[User, Depends(current_user)]) -> User:
    return user


@router.post("/password/forgot", status_code=204)
async def forgot(
    body: PasswordForgotIn,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    await auth_service.forgot_password(session, body.email)


@router.post("/password/reset", status_code=204)
async def reset(
    body: PasswordResetIn,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    await auth_service.reset_password(session, body.token, body.new_password)
