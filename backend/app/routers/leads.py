from fastapi import APIRouter, Depends, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.ratelimit import limiter
from app.schemas.leads import LeadCreated, LeadIn, UploadAccepted
from app.services import leads

router = APIRouter(prefix="/api/v1/public", tags=["leads"])


@router.post("/leads/uploads", response_model=UploadAccepted)
async def upload_demo(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> UploadAccepted:
    token = await leads.accept_demo(session, file)
    return UploadAccepted(upload_token=token)


@router.post("/leads", response_model=LeadCreated, status_code=201)
@limiter.limit("30/day")
@limiter.limit("5/minute")
async def create_lead(
    request: Request,
    body: LeadIn,
    session: AsyncSession = Depends(get_session),
) -> LeadCreated:
    await leads.create_lead(session, request, body)
    return LeadCreated()
