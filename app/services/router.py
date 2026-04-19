from typing import Optional
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.base import AppointmentProvider
from app.providers.local import LocalProvider
from app.providers.apphealth import AppHealthProvider
from app.models.provider_route import ProviderRoute
from app.models.professional import Professional

logger = structlog.get_logger()


class ProviderRouter:
    """Routes requests to correct provider based on specialty/professional."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def resolve_provider(
        self,
        specialty_slug: Optional[str] = None,
        professional_id: Optional[str] = None,
    ) -> AppointmentProvider:
        """Resolve which provider to use based on specialty or professional."""

        # If we have a professional_id, check their provider field
        if professional_id:
            prof = await self.db.get(Professional, UUID(professional_id))
            if prof:
                if prof.provider == "apphealth":
                    logger.info("routing_to_apphealth", professional_id=professional_id)
                    return AppHealthProvider()
                else:
                    logger.info("routing_to_local", professional_id=professional_id)
                    return LocalProvider(self.db)

        # Check provider_routes table for specialty
        if specialty_slug:
            route_result = await self.db.execute(
                select(ProviderRoute).where(
                    ProviderRoute.specialty_slug == specialty_slug.lower(),
                    ProviderRoute.active == True,
                )
            )
            route = route_result.scalar_one_or_none()

            if route:
                if route.provider == "apphealth":
                    logger.info("routing_to_apphealth_via_route", specialty_slug=specialty_slug)
                    return AppHealthProvider()
                else:
                    logger.info("routing_to_local_via_route", specialty_slug=specialty_slug)
                    return LocalProvider(self.db)

        # Default to local
        logger.info("routing_to_local_default", specialty_slug=specialty_slug)
        return LocalProvider(self.db)

    async def get_professional_provider(self, professional_id: str) -> str:
        """Get the provider type for a specific professional."""
        prof = await self.db.get(Professional, UUID(professional_id))
        if prof:
            return prof.provider
        return "local"
