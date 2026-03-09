import logging
import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.dependencies import get_tenant, require_admin
from db.database import get_db
from db.models import Tenant
from schemas.pydantic_models import TenantCreate, TenantResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tenants", tags=["tenants"])


def _generate_api_key() -> str:
    return f"sk_{secrets.token_urlsafe(32)}"


@router.post("", response_model=TenantResponse, status_code=201)
async def create_tenant(
    request: TenantCreate,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new tenant. Requires X-Admin-Secret header."""
    tenant = Tenant(
        id=uuid.uuid4(),
        name=request.name,
        api_key=_generate_api_key(),
        escalation_email=request.escalation_email,
        bot_name=request.bot_name or "Assistant",
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    logger.info(f"Created tenant {tenant.id} ({tenant.name})")
    return tenant


@router.get("/me", response_model=TenantResponse)
async def get_my_tenant(tenant: Tenant = Depends(get_tenant)):
    """Returns the authenticated tenant's own record. Requires X-API-Key header."""
    return tenant


@router.post("/me/regenerate-key", response_model=TenantResponse)
async def regenerate_my_api_key(
    tenant: Tenant = Depends(get_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Regenerates the authenticated tenant's API key. Requires X-API-Key header."""
    tenant.api_key = _generate_api_key()
    await db.commit()
    await db.refresh(tenant)
    logger.info(f"Regenerated API key for tenant {tenant.id}")
    return tenant


@router.delete("/me", status_code=204)
async def deactivate_my_tenant(
    tenant: Tenant = Depends(get_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivates the tenant. The record is kept in the DB (soft delete).
    All subsequent API key lookups for this tenant will return 401.
    Requires X-API-Key header.
    """
    tenant.is_active = False
    await db.commit()
    logger.info(f"Deactivated tenant {tenant.id}")
