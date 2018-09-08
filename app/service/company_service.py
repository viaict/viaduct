from app.exceptions.base import ResourceNotFoundException
from app.models.company import Company
from app.repository import company_repository


def find_company_by_id(company_id: int) -> Company:
    return company_repository.find_company_by_id(company_id)


def get_company_by_id(company_id: int) -> Company:
    company = find_company_by_id(company_id)
    if not company:
        raise ResourceNotFoundException("company", company_id)
    return company
