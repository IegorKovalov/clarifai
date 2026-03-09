from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.rate_limiter import chat_rate_limiter
from config import settings
from db.database import get_db
from db.models import Tenant


async def get_tenant(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> Tenant:
    """Resolves X-API-Key header to a Tenant."""
    result = await db.execute(
        select(Tenant).where(Tenant.api_key == x_api_key, Tenant.is_active == True)
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    return tenant


def require_admin(x_admin_secret: str = Header(..., alias="X-Admin-Secret")) -> None:
    """Verifies the X-Admin-Secret header. Used to protect tenant creation."""
    if x_admin_secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Invalid admin secret")


def check_chat_rate_limit(tenant: Tenant = Depends(get_tenant)) -> Tenant:
    """Enforces 60 chat requests/minute per tenant. Used on chat endpoints."""
    allowed, retry_after = chat_rate_limiter.check(str(tenant.id))
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )
    return tenant
