from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas.deployment import DeploymentCreate, DeploymentResponse
from app.utils import validate_deployment_details, update_status_in_db
from app.services.auth import validate_user_access, get_token
from app.services.scheduler import new_deploy, complete_deploy
from app.db.base import get_db
from app.db import db_schema
from sqlalchemy import or_


router = APIRouter()

@router.post("/create/", response_model=DeploymentResponse)
def create_deployment(deployment: DeploymentCreate, token:str = Depends(get_token), db: Session = Depends(get_db)):
    """
    API to create a new deployment within the given cluster
    """
    validate_user_access(token, db)
    cluster = validate_deployment_details(deployment, db)
    new_deployment = db_schema.Deployment(
        name=deployment.name,
        image_path=deployment.image_path,
        cpu_required=deployment.cpu_required,
        ram_required=deployment.ram_required,
        gpu_required=deployment.gpu_required,
        priority=deployment.priority,
        cluster_id=deployment.cluster_id,
        status="Pending"
    )
    if new_deployment is None:
        raise HTTPException(status_code=400, detail="Failed to create deployment")
    try:
        db.add(new_deployment)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Priority should be unique")
    db.refresh(new_deployment)
    status_change = new_deploy(new_deployment, cluster)
    update_status_in_db(status_change, db)
    db.commit()
    return new_deployment

@router.get("/get_deployment/", response_model=DeploymentResponse)
def get_deployment(token: str = Depends(get_token), deployment_id: int = Query(None, alias="id"), deployment_name: str = Query(None),
                db: Session = Depends(get_db)):
    """
    API to fetch details of a given deployment within a given cluster
    """
    if not deployment_id and not deployment_name:
        raise HTTPException(status_code=400, detail="Either 'deployment_id' or 'deployment_name' must be provided")
    validate_user_access(token, db)
    deployment = db.query(db_schema.Deployment).filter(
        or_(
            db_schema.Deployment.id == deployment_id,
            db_schema.Deployment.name == deployment_name
        )
    ).first()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment

@router.post("/complete/", response_model=DeploymentResponse)
def finish_deployment(token: str = Depends(get_token), deployment_id: int = Query(None, alias="id"),
                      deployment_name: str = Query(None), db: Session = Depends(get_db)):
    """
    API to change the deployment status to complete
    """
    if not deployment_id and not deployment_name:
        raise HTTPException(status_code=400, detail="Either 'deployment_id' or 'deployment_name' must be provided")
    validate_user_access(token, db)
    deployment = db.query(db_schema.Deployment).filter(
        or_(
            db_schema.Deployment.id == deployment_id,
            db_schema.Deployment.name == deployment_name
        )
    ).first()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    cluster = db.query(db_schema.Cluster).filter(db_schema.Cluster.id == deployment.cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster ID not found")

    status_change = complete_deploy(deployment, cluster)
    update_status_in_db(status_change, db)
    db.commit()
    db.refresh(deployment)
    return deployment
