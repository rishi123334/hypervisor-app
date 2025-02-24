from pydantic import BaseModel

class ClusterCreate(BaseModel):
    name: str
    total_ram: int
    total_cpu: float
    total_gpu: int


class ClusterResponse(BaseModel):
    id: int
    name: str
    total_ram: int
    total_cpu: float
    total_gpu: int
    available_ram: int
    available_cpu: float
    available_gpu: int

