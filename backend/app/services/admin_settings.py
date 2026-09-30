import nh3
from app.core.errors import Forbidden, NotFound
from app.models.enums import UserRole
from app.models.users import SiteSettings, User
from app.schemas.site import SiteSettingsSchema
from app.services.revalidate import enqueue
from sqlalchemy.ext.asyncio import AsyncSession


async def read_settings(session: AsyncSession) -> SiteSettingsSchema:
    row = await session.get(SiteSettings, 1)
    if row is None:
        raise NotFound("Todavía no hay ajustes del sitio.")
    return SiteSettingsSchema.model_validate(row.data)


async def write_settings(
    session: AsyncSession,
    user: User,
    body: SiteSettingsSchema,
) -> SiteSettingsSchema:
    row = await session.get(SiteSettings, 1)
    if row is None:
        raise NotFound("Todavía no hay ajustes del sitio.")
    current = SiteSettingsSchema.model_validate(row.data)
    if body.features != current.features and user.role is not UserRole.SUPERADMIN:
        raise Forbidden("Solo un superadmin puede cambiar las funciones técnicas.")
    legal = body.legal.model_copy(update={"privacy_html": nh3.clean(body.legal.privacy_html)})
    saved = body.model_copy(update={"legal": legal})
    row.data = saved.model_dump(mode="json")
    row.updated_by = user.id
    enqueue(session, ["/", "/aviso-de-privacidad", "/links", "/sitemap.xml"])
    await session.commit()
    return saved
