from fastapi import HTTPException
from app.db import db_schema
from sqlalchemy.orm import Session
from app.schemas.deployment import DeploymentCreate

def validate_deployment_details(deployment: DeploymentCreate, db: Session):
    cluster = db.query(db_schema.Cluster).filter(db_schema.Cluster.id == deployment.cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster ID not found")
    if (
            deployment.ram_required > cluster.total_ram or
            deployment.cpu_required > cluster.total_cpu or
            deployment.gpu_required > cluster.total_gpu
    ):
        raise HTTPException(status_code=422, detail="Not Enough Resources on the cluster for this deployment")
    return cluster

def update_status_in_db(status_change: dict, db: Session):
    print(status_change)
    updates = [{"id": deployment_id, "status": new_status[1]} for deployment_id, new_status in status_change.items()]
    db.bulk_update_mappings(db_schema.Deployment, updates)
    return