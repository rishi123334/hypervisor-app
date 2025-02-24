import os

import redis
from app.services.resource_management import check_resource_availability, allocate_resources, free_resources
from app.db.db_schema import Deployment, Cluster


def _make_key(deployment: Deployment):
    """
    Create a key to store deployment information in redis sorted set
    """
    return (f"{deployment.id}|{deployment.image_path}|{deployment.cpu_required}|{deployment.ram_required}|"
            f"{deployment.gpu_required}|{deployment.priority}|{deployment.cluster_id}|{deployment.status}|"
            f"{deployment.name}")

def _from_key(key: str):
    """
    Create deployment object based on db schema from the value stored in redis sorted set
    """
    key = key.split('|')
    return Deployment(
        id=int(key[0]),
        image_path=key[1],
        cpu_required=int(key[2]),
        ram_required = int(key[3]),
        gpu_required = int(key[4]),
        priority = int(key[5]),
        cluster_id = int(key[6]),
        status = key[7],
        name=key[8]
    )

def _get_redis_info():
    """
    To create a redis connection and required pending queue and running queue information
    """
    host = os.environ.get('REDIS_HOST', 'localhost')
    port = int(os.environ.get('REDIS_PORT', '6379'))
    redis_db_index = int(os.environ.get('REDIS_DATABASE_INDEX', '0'))
    redis_client = redis.StrictRedis(host=host, port=port, db=redis_db_index, decode_responses=True)

    if redis_client.zcard("PENDING_QUEUE_1"):
        pending_queue = "PENDING_QUEUE_1"
        temp_queue = "PENDING_QUEUE_2"
    else:
        pending_queue = "PENDING_QUEUE_2"
        temp_queue = "PENDING_QUEUE_1"
    running_queue = "RUNNING_QUEUE"

    return redis_client, pending_queue, running_queue, temp_queue

def _update_status_change(status_change, deployment, new_status):
    """
    To keep a track of deployments whose status have changed
    """
    state = status_change.get(deployment.id, (deployment.status, deployment.status))
    status_change[deployment.id] = (state[0], new_status)
    if state[0] == new_status:
        del status_change[deployment.id]


def _deploy_pending_resource(redis_client, pending_queue, running_queue, temp_queue, cluster, status_change):
    """
    To fill in lower priority deployment of the pending queue if possible for max utilization
    """
    while redis_client.zcard(pending_queue) != 0:
        pending_deployment_key, _ = redis_client.zpopmax(pending_queue)[0]
        pending_deployment = _from_key(pending_deployment_key)

        if check_resource_availability(cluster, pending_deployment):
            _update_status_change(status_change, pending_deployment, "Running")
            allocate_resources(cluster, pending_deployment)
            redis_client.zadd(running_queue, {_make_key(pending_deployment): pending_deployment.priority})
        else:
            redis_client.zadd(temp_queue, {_make_key(pending_deployment): pending_deployment.priority})

def new_deploy(new_deployment: Deployment, cluster: Cluster):
    """
    To deploy new deployment
    Algorithm:
        1. Checks if cluster is having resource or not. If resource available, then deploy and return
        2. Checks the running queue for lower priority deployments than the new deployment and add them pending queue
        until enough sources are freed or there are no lower priority deployments left
        3. If enough resources freed, then deploy this and check the pending queue to fill other possible
        deployments (_deploy_pending_resource takes care of this)
        4. If not lower priority left, then add this to pending queue and check the pending queue to fill other
        possible deployments (_deploy_pending_resource takes care of this)
        5. Return a dict of status_change containing deployment ids which have change of the course of preempting
    """
    status_change = {}
    redis_client, pending_queue, running_queue, temp_queue = _get_redis_info()

    if check_resource_availability(cluster, new_deployment):
        allocate_resources(cluster, new_deployment)
        redis_client.zadd(running_queue, {_make_key(new_deployment): new_deployment.priority})
        return status_change

    while redis_client.zcard(running_queue) != 0:
        running_deployment_key, running_priority = redis_client.zpopmin(running_queue)[0]

        if running_priority > new_deployment.priority:
            redis_client.zadd(running_queue, {running_deployment_key: running_priority})
            redis_client.zadd(pending_queue, {_make_key(new_deployment): new_deployment.priority})
            break

        running_deployment = _from_key(running_deployment_key)
        free_resources(cluster, running_deployment)
        _update_status_change(status_change, running_deployment, "Pending")
        running_deployment.status = "Pending"
        redis_client.zadd(pending_queue, {_make_key(running_deployment): running_deployment.priority})

        if check_resource_availability(cluster, new_deployment):
            allocate_resources(cluster, new_deployment)
            redis_client.zadd(running_queue, {_make_key(new_deployment): new_deployment.priority})
            break

    _deploy_pending_resource(redis_client, pending_queue, running_queue, temp_queue, cluster, status_change)

    return status_change


def complete_deploy(deployment: Deployment, cluster: Cluster):
    """
    To remove running deployment from running queue and mark it as complete
    Algorithm:
        1. Remove the deployment from running queue and free resources from the cluster related to it
        2. Check any lower priority deployments from the pending queue to fill other possible
        deployments (_deploy_pending_resource takes care of this)
        3. Return a dict of status_change containing deployment ids which have changed from pending to running
    """
    status_change = {}
    redis_client, pending_queue, running_queue, temp_queue = _get_redis_info()

    redis_client.zrem(running_queue, _make_key(deployment))
    deployment.status = 'Completed'

    free_resources(cluster, deployment)

    _deploy_pending_resource(redis_client, pending_queue, running_queue, temp_queue, cluster, status_change)

    return status_change
