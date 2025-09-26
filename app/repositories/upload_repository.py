from sqlalchemy.orm import Session
from app.entity.models import upload_model as Upload

class UploadRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, candidate_name: str, cv_file_path: str, report_file_path: str) -> Upload:
        upload = Upload(
            candidate_name=candidate_name,
            cv_file_path=cv_file_path,
            report_file_path=report_file_path
        )
        self.db.add(upload)
        self.db.commit()
        self.db.refresh(upload)
        return upload

    def get_by_id(self, upload_id: int) -> Upload | None:
        return self.db.query(Upload).filter(Upload.id == upload_id).first()

    def list_all(self) -> list[Upload]:
        return self.db.query(Upload).all()
