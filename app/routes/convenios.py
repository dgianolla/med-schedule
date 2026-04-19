from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.convenio import Convenio as ConvenioModel
from app.schemas.convenio import (
    ConvenioCreate,
    ConvenioUpdate,
    ConvenioResponse,
)
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/convenios", tags=["Convenios"])


@router.get(
    "",
    response_model=PaginatedResponse[ConvenioResponse],
    summary="List convenios",
)
async def list_convenios(
    active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(ConvenioModel)

    if active is not None:
        query = query.where(ConvenioModel.active == active)
    if search:
        query = query.where(ConvenioModel.name.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(ConvenioModel.name)
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    convenios = result.scalars().all()

    pages = (total + per_page - 1) // per_page if total else 0

    return PaginatedResponse(
        items=[ConvenioResponse.model_validate(c) for c in convenios],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get(
    "/{convenio_id}",
    response_model=ConvenioResponse,
    summary="Get convenio details",
)
async def get_convenio(
    convenio_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    convenio = await db.get(ConvenioModel, convenio_id)
    if not convenio:
        raise HTTPException(status_code=404, detail="Convenio not found")
    return ConvenioResponse.model_validate(convenio)


@router.post(
    "",
    response_model=ConvenioResponse,
    status_code=201,
    summary="Create convenio",
)
async def create_convenio(
    request: ConvenioCreate,
    db: AsyncSession = Depends(get_db),
):
    convenio = ConvenioModel(**request.model_dump())
    db.add(convenio)
    await db.commit()
    await db.refresh(convenio)
    return ConvenioResponse.model_validate(convenio)


@router.put(
    "/{convenio_id}",
    response_model=ConvenioResponse,
    summary="Update convenio",
)
async def update_convenio(
    convenio_id: UUID,
    request: ConvenioUpdate,
    db: AsyncSession = Depends(get_db),
):
    convenio = await db.get(ConvenioModel, convenio_id)
    if not convenio:
        raise HTTPException(status_code=404, detail="Convenio not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(convenio, field, value)

    await db.commit()
    await db.refresh(convenio)
    return ConvenioResponse.model_validate(convenio)


@router.delete(
    "/{convenio_id}",
    status_code=204,
    summary="Delete convenio",
)
async def delete_convenio(
    convenio_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    convenio = await db.get(ConvenioModel, convenio_id)
    if not convenio:
        raise HTTPException(status_code=404, detail="Convenio not found")

    await db.delete(convenio)
    await db.commit()
    return None
