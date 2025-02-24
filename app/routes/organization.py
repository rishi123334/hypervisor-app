from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.db.base import get_db
from app.db import db_schema
from app.services.auth import validate_user_access, get_token
router = APIRouter()

@router.post("/create/", response_model=OrganizationResponse)
def create_organization(organization: OrganizationCreate, token: str = Depends(get_token), db: Session = Depends(get_db)):
    """
    API to create a new organization
    """
    validate_user_access(token, db)
    invite_code = "org-" + str(db.query(db_schema.Organization).count() + 1)  # Simple invite code generator
    db_organization = db_schema.Organization(name=organization.name, invite_code=invite_code)

    try:
        db.add(db_organization)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Organization with the given name already exists")
    db.refresh(db_organization)
    return db_organization


@router.post("/join/")
def join_organization(invite_code: str, token: str = Depends(get_token), db: Session = Depends(get_db)):
    """
    API to make the user join an organization via an invite-code
    """
    db_user = validate_user_access(token, db)

    db_organization = db.query(db_schema.Organization).filter(db_schema.Organization.invite_code == invite_code).first()
    if not db_organization:
        raise HTTPException(status_code=400, detail="Invalid invite code")

    # Add user to the organization
    db_user.organization_id = db_organization.id
    db.commit()
    db.refresh(db_user)

    return {"message": f"User {db_user.username} joined organization {db_organization.name}"}
