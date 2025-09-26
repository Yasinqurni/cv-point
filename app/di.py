from fastapi import Depends
from sqlalchemy.orm import Session

from .pkg.db import get_auth_session, get_mdm_session
from .repositories.nero_auth_repository import NeroAuthUserRepository, UserReader
from .repositories.mdm_repository import MdmRepository, MdmAccountRepo
from .services.migration_user_aeris_service import MigrationUserAerisService, UsersToMdmService
from .controllers.migration_user_aeris_controller import MigrationUserAerisController, UsersToMdmController


def provide_user_reader() -> UserReader:
    return NeroAuthUserRepository()


def provide_mdm_repo() -> MdmAccountRepo:
    return MdmRepository()


def provide_service(
    user_reader: UserReader = Depends(provide_user_reader),
    mdm_repo: MdmAccountRepo = Depends(provide_mdm_repo),
) -> UsersToMdmService:
    return MigrationUserAerisService(user_reader, mdm_repo)


def provide_controller(
    service: UsersToMdmService = Depends(provide_service),
) -> UsersToMdmController:
    return MigrationUserAerisController(service)


# Convenience re-exports for sessions
get_auth_session_dep = get_auth_session
get_mdm_session_dep = get_mdm_session
