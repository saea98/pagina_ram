from app.core.errors import Conflict, Forbidden, NotFound
from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.users import User
from app.schemas.admin import UserAdminOut, UserCreateIn, UserPatchIn
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def list_users(session: AsyncSession) -> list[UserAdminOut]:
    rows = await session.scalars(select(User).order_by(User.full_name))
    return [UserAdminOut.model_validate(row) for row in rows]


async def create_user(session: AsyncSession, body: UserCreateIn) -> UserAdminOut:
    email = body.email.strip().lower()
    existing = await session.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise Conflict("Ese correo ya tiene una cuenta.")
    user = User(
        email=email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role=body.role,
        is_active=True,
    )
    session.add(user)
    await session.commit()
    return UserAdminOut.model_validate(user)


async def update_user(
    session: AsyncSession,
    actor: User,
    user_id: object,
    body: UserPatchIn,
) -> UserAdminOut:
    user = await session.get(User, user_id)
    if user is None:
        raise NotFound("No encontramos a esa persona.")
    data = body.model_dump(exclude_unset=True)
    if user.id == actor.id and data.get("is_active") is False:
        raise Forbidden("No puedes desactivar tu propia cuenta.")
    if data.get("role") is UserRole.ADMIN and user.role is UserRole.SUPERADMIN:
        others = await session.scalar(
            select(func.count())
            .select_from(User)
            .where(User.role == UserRole.SUPERADMIN, User.is_active.is_(True), User.id != user.id)
        )
        if int(others or 0) == 0:
            raise Forbidden("Tiene que quedar al menos un superadmin activo.")
    for key, value in data.items():
        setattr(user, key, value)
    await session.commit()
    return UserAdminOut.model_validate(user)


async def reset_password(session: AsyncSession, user_id: object, new_password: str) -> None:
    user = await session.get(User, user_id)
    if user is None:
        raise NotFound("No encontramos a esa persona.")
    user.password_hash = hash_password(new_password)
    user.failed_logins = 0
    user.locked_until = None
    await session.commit()
