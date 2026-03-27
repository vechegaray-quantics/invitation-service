from fastapi import Header, HTTPException, status


def get_tenant_id(x_tenant_id: str | None = Header(default=None)) -> str:
    if x_tenant_id is None or not x_tenant_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-Id header is required",
        )

    tenant_id = x_tenant_id.strip()

    if len(tenant_id) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-Id must contain at least 3 characters",
        )

    return tenant_id