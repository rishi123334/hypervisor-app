from app.db.db_schema import Cluster, Deployment

def check_resource_availability(cluster: Cluster, deployment: Deployment):
    """
    Check if the cluster has sufficient resources for the deployment
    """
    if (cluster.available_ram >= deployment.ram_required and
        cluster.available_cpu >= deployment.cpu_required and
        cluster.available_gpu >= deployment.gpu_required):
        return True
    return False

def allocate_resources(cluster: Cluster, deployment: Deployment):
    """
    Allocates resources for a deployment and updates the cluster's resource availability.
    """
    cluster.available_ram -= deployment.ram_required
    cluster.available_cpu -= deployment.cpu_required
    cluster.available_gpu -= deployment.gpu_required

    deployment.status = "Running"

    print(f"Resources allocated for deployment {deployment.id} on cluster {cluster.id}")

def free_resources(cluster: Cluster, deployment: Deployment):
    """
    Free resources for a deployment and updates the cluster's resource availability.
    """
    cluster.available_ram += deployment.ram_required
    cluster.available_cpu += deployment.cpu_required
    cluster.available_gpu += deployment.gpu_required

    print(f"Resources free on cluster {cluster.id} of deployment {deployment.id}")