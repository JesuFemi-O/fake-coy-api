from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from app.models import Company, Employee, CompanyWithoutEmployees, PaginatedResponse
from app.dependencies import verify_api_key
from app.data import get_fake_companies


# Initialize FastAPI app and set Swagger docs to root
app = FastAPI(docs_url="/")

# In-memory storage for fake data
companies = get_fake_companies()




@app.get("/companies", response_model=PaginatedResponse)
def get_companies(
    api_key: str = Depends(verify_api_key),
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0, le=100),
    industry: Optional[str] = None,
    created_after: Optional[datetime] = None,
    updated_after: Optional[datetime] = None,
):
    """Get paginated list of companies with optional filtering by industry and dates."""
    filtered_companies = [
        c for c in companies 
        if (industry is None or c.industry == industry) and
           (created_after is None or c.created_at > created_after) and
           (updated_after is None or c.updated_at > updated_after)
    ]
    total = len(filtered_companies)
    start = (page - 1) * size
    end = start + size
    paginated_companies = filtered_companies[start:end]
    total_pages = (total + size - 1) // size

    # Convert to CompanyWithoutEmployees model
    paginated_companies_without_employees = [
        CompanyWithoutEmployees(**company.dict(exclude={"employees"}))
        for company in paginated_companies
    ]

    return {
        "items": paginated_companies_without_employees,
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages
    }

@app.get("/companies/{company_id}/employees", response_model=PaginatedResponse)
def get_employees(
    company_id: int,
    api_key: str = Depends(verify_api_key),
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0, le=100),
    job_title: Optional[str] = None,
    created_after: Optional[datetime] = None,
    updated_after: Optional[datetime] = None,
):
    """Get paginated list of employees for a specific company with optional filtering by job title and dates."""
    company = next((c for c in companies if c.id == company_id), None)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    filtered_employees = [
        e for e in company.employees 
        if (job_title is None or e.job_title == job_title) and
           (created_after is None or e.created_at > created_after) and
           (updated_after is None or e.updated_at > updated_after)
    ]
    
    total = len(filtered_employees)
    start = (page - 1) * size
    end = start + size
    paginated_employees = filtered_employees[start:end]
    total_pages = (total + size - 1) // size

    return {
        "items": paginated_employees,
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages
    }
