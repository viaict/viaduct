from app import db
from app.models.company import Company


def find_company_by_id(company_id: int) -> Company:
    return db.session.query(Company).filter_by(id=company_id).one_or_none()
