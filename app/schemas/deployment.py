from pydantic import BaseModel

class DeploymentCreate(BaseModel):
    name: str
    cluster_id: int
    image_path: str
    ram_required: int
    cpu_required: int
    gpu_required: int
    priority: int


class DeploymentResponse(BaseModel):
    id: int
    name: str
    cluster_id: int
    image_path: str
    ram_required: int
    cpu_required: float
    gpu_required: int
    status: str
    priority: int
