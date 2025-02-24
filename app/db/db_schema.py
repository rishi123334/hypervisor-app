from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    organization = relationship("Organization", back_populates="members")


# Organization Model
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    invite_code = Column(String, unique=True, index=True)

    members = relationship("User", back_populates="organization")


# Cluster Model
class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    total_cpu = Column(Integer)
    total_ram = Column(Integer)
    total_gpu = Column(Integer)
    available_cpu = Column(Integer)
    available_ram = Column(Integer)
    available_gpu = Column(Integer)

# Deployment Model
class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    image_path = Column(String)
    cpu_required = Column(Integer)
    ram_required = Column(Integer)
    gpu_required = Column(Integer)
    priority = Column(Integer, unique=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"))
    status = Column(String)

    cluster = relationship("Cluster")
