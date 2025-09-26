import time
from typing import Dict, Any, Protocol
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..repositories.nero_auth_repository import NeroAuthRepository
from ..repositories.mdm_repository import MdmRepository
from ..entity.requests.migration_aeris_request import MigrationAerisQuery


class MigrationUserAerisService(Protocol):
    def migrate(self, auth_db: Session, mdm_db: Session, req: MigrationAerisQuery) -> Dict[str, Any]:
        ...


class MigrationUserAerisServiceImpl(MigrationUserAerisService):
    def __init__(self, nero_repo: NeroAuthRepository, mdm_repo: MdmRepository) -> None:
        self.nero_repo = nero_repo
        self.mdm_repo = mdm_repo

    def migrate(self, auth_db: Session, mdm_db: Session, req: MigrationAerisQuery) -> Dict[str, Any]:
        results = []

        users = self.nero_repo.get_list_user(auth_db, req.limit, req.email)
        if len(users) == 0:
            raise HTTPException(
                status_code=404,
                detail="no user found"
            )

        for each in users:
            employee = self.mdm_repo.find_employee_by_email(mdm_db, each.email)
            
            if not employee:
                results.append({
                    "email": each.email,
                    "reason": "email from mdm not found"
                })
                continue

            if employee.status != "ACTIVE":
                results.append({
                    "email": each.email,
                    "reason": "employee status is not active"
                })
                continue
            
            if employee.identity: 
                results.append({
                    "email": each.email,
                    "reason": "identity access already exist"
                })
                continue

            user_role = self.nero_repo.get_user_role_employee(auth_db, employee.id)
            if not user_role:
                self.nero_repo.create_user_role(auth_db, employee.id)

            self.mdm_repo.create_identity_management_employee(
                mdm_db,
                id_employee=employee.id,
                password=each.password
            )
            
            results.append({
                "email": each.email,
                "reason": "success adding identity access"
            })

        auth_db.flush()
        mdm_db.flush()

        mdm_db.commit()
        mdm_db.commit()
        

        return {"results": results}
