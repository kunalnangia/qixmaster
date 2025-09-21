from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db_sync
from app.models.db_models import Project
from app.schemas.project import ProjectInDB

router = APIRouter()

@router.get("/temp", response_model=List[ProjectInDB])
def read_projects_temp(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db_sync)
):
    """
    Temporary endpoint to retrieve projects without authentication.
    This is for debugging the projects dropdown issue.
    """
    projects = db.query(Project).filter(
        Project.is_active == True
    ).offset(skip).limit(limit).all()
    return projects