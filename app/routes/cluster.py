from app.services.auth import validate_user_access, get_token
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.schemas.cluster import ClusterCreate, ClusterResponse
from app.db import db_schema
from app.db.base import get_db
from sqlalchemy import or_


router = APIRouter()

@router.post("/create/", response_model=ClusterResponse)
def create_cluster(cluster: ClusterCreate, token: str = Depends(get_token), db: Session = Depends(get_db)):
    """
    API to create a new cluster
    """
    validate_user_access(token, db)
    new_cluster = db_schema.Cluster(
        name=cluster.name,
        total_ram=cluster.total_ram,
        total_cpu=cluster.total_cpu,
        total_gpu=cluster.total_gpu,
        available_ram=cluster.total_ram,
        available_cpu=cluster.total_cpu,
        available_gpu=cluster.total_gpu
    )
    db.add(new_cluster)
    db.commit()
    db.refresh(new_cluster)
    return new_cluster

@router.get("/get_cluster/", response_model=ClusterResponse)
def get_cluster(token: str = Depends(get_token), cluster_id: int = Query(None, alias="id"),
                cluster_name: str = Query(None), db: Session = Depends(get_db)):
    """
    API to get cluster details based on either name or id of the cluster
    """
    if not cluster_id and not cluster_name:
        raise HTTPException(status_code=400, detail="Either 'cluster_id' or 'cluster_name' must be provided")
    validate_user_access(token, db)
    cluster = db.query(db_schema.Cluster).filter(
        or_(
            db_schema.Cluster.id == cluster_id,
            db_schema.Cluster.name == cluster_name
        )
    ).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    if cluster_id and cluster_name and (cluster.id != cluster_id or cluster.name != cluster_name):
        raise HTTPException(status_code=400, detail="Given Cluster id and Cluster name do not correspond "
                                                    "to the same cluster")
    return cluster
