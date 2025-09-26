from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from typing import Optional

from ..pkg.db import get_auth_session, get_mdm_session
from ..repositories.nero_auth_repository import NeroAuthUserRepositoryImpl, NeroAuthRepository
from ..repositories.mdm_repository import MdmRepository, MdmRepositoryImpl
from ..services.migration_user_aeris_service import MigrationUserAerisService, MigrationUserAerisServiceImpl
from ..controllers.migration_user_aeris_controller import MigrationUserAerisController, MigrationUserAerisControllerImpl
from ..entity.requests.migration_aeris_request import MigrationAerisQuery
from ..entity.responses.migration_aeris_response import MigrationAerisResponse

router = APIRouter()


def get_service() -> MigrationUserAerisService:
    user_repo: NeroAuthRepository = NeroAuthUserRepositoryImpl()
    mdm_repo: MdmRepository = MdmRepositoryImpl()
    return MigrationUserAerisServiceImpl(user_repo, mdm_repo)


def get_controller(service: MigrationUserAerisService = Depends(get_service)) -> MigrationUserAerisControllerImpl:
    return MigrationUserAerisControllerImpl(service)



@router.get("/migrate/aeris", response_model=MigrationAerisResponse)
async def migrate_users_to_mdm_get_endpoint(
    email: Optional[str] = Query(None, description="Filter users by email (optional)"),
    limit: int = Query(100, ge=1, le=10000, description="Max number of records to process"),
    auth_db: Session = Depends(get_auth_session),
    mdm_db: Session = Depends(get_mdm_session),
    controller: MigrationUserAerisController = Depends(get_controller),
) -> MigrationAerisResponse:
    try:
        req = MigrationAerisQuery(email=email, limit=limit)
        return await controller.run(req, auth_db, mdm_db)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
