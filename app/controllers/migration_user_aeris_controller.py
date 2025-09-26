from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from typing import Protocol

from ..entity.requests.migration_aeris_request import MigrationAerisQuery
from ..entity.responses.migration_aeris_response import MigrationAerisResponse
from ..pkg.db import get_auth_session, get_mdm_session
from ..services.migration_user_aeris_service import MigrationUserAerisService


class MigrationUserAerisController(Protocol):
    async def run(
        self, req: MigrationAerisQuery, auth_db: Session, mdm_db: Session
    ) -> any:
        ...


class MigrationUserAerisControllerImpl(MigrationUserAerisController):
    def __init__(self, service: MigrationUserAerisService) -> None:
        self.service = service

    async def run(
        self, req: MigrationAerisQuery, auth_db: Session, mdm_db: Session
    ) -> MigrationAerisResponse:
        stats = await run_in_threadpool(
            lambda: self.service.migrate(auth_db, mdm_db, req)
        )
        return MigrationAerisResponse(status="ok", result=stats)
