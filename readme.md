Hypervisor App Documentation

## Introduction
Hypervisor App is a backend service designed to manage user authentication, organization membership, cluster resource allocation, and deployment scheduling. It optimizes deployment priority, resource utilization, and maximizes successful deployments.

---

## Problem Statement
Design a backend service that manages:

1. **User Authentication and Organization Management**
    - User Authentication: Implement a basic authentication mechanism (e.g., username and password).
    - Invite Code: Users can join an organization using an invite code.
    - Organization Membership: Once authenticated, users are added to an organization.

2. **Cluster Management**
    - Cluster Creation: Users can create a cluster with fixed resources (RAM, CPU, GPU).
    - Resource Management: Track the available and allocated resources in each cluster.

3. **Deployment Management**
    - Create Deployment: Users can create a deployment for any cluster by providing a Docker image path.
    - Resource Allocation for Deployment: Each deployment requires a certain amount of resources (RAM, CPU, GPU).
    - Queue Deployments: The deployment should be queued if the resources are unavailable in the cluster.
    - Preemption-based Scheduling: Prioritize high-priority deployments.

4. **Scheduling Algorithm**
    - The scheduling algorithm should optimize for:
        - Priority: Higher priority deployments should be scheduled first.
        - Resource Utilization: Efficiently use available resources.
        - Maximize Successful Deployments: Maximize the number of deployments that can be successfully scheduled from the queue.

---
## Technologies Used
- **FastAPI**: Web framework for building APIs.
- **PostgreSQL**: Relational database management system for storing application data.
- **Redis**: In-memory data structure store for caching and session management.
- **Docker**: Containerization tool to package the application with all dependencies.
- **Docker Compose**: Tool for defining and running multi-container Docker applications.
- **JWT**: For implementing secure authentication.

---
## Getting Started
### Development Setup
#### Prerequisites
Make sure the following are installed:
-  Docker
-  Docker Compose

To run the Hypervisor App locally, follow these steps:
- Download the provided tar file.
- Set up environment variables in the .env file.
- Build the Docker images: 
```shell
  docker-compose build .
```
- Start the containers: 
```shell
  docker-compose up
```
- Access the app at `http://localhost:8000`.

---
## Testing
You can use the provided test cases to run unit tests on the application. Follow the steps below to run the tests:
- **Install pytest**: 
```shell
  pip install pytest
```
- **Run tests**: 
```shell
  pytest
```

---
## Database Schema
The Hypervisor App uses PostgreSQL for storing data. Below are the tables used in the database:
- **Users**: Stores user credentials and organization data.
- **Organizations**: Stores organization-related information.
- **Clusters**: Stores cluster details and resource allocations.
- **Deployments**: Stores deployment data.

---
## Environment Variables
The .env file contains the configuration values for the app. Here is the list of variables:

```
JWT_SECRET_KEY: Secret key for JWT authentication.
JWT_ALGORITHM: Algorithm used for JWT signing.
ACCESS_TOKEN_EXPIRE_MINUTES: Expiration time of the JWT access token (in minutes).
SQL_DB_URL: Database URL for PostgreSQL.
POSTGRES_USER: PostgreSQL username.
POSTGRES_PASSWORD: PostgreSQL password.
POSTGRES_DB: PostgreSQL database name.
REDIS_HOST: Host for Redis.
REDIS_PORT: Port for Redis.
REDIS_DATABASE_INDEX: Database index for Redis.
```

---
## API Endpoints
### User Authentication
#### Register User
`POST /users/register/`
**Summary**: API to create a new user.
**Request**:
```json
{
  "username": "string",
  "password": "string"
}
```
**Response**:
```json
{
  "id": "integer",
  "username": "string",
  "organization_id": "integer"
}
```

#### Login User
`POST /users/login/`
**Summary**: API to authenticate the registered user.
**Request**:
```json
{
  "username": "string",
  "password": "string"
}
```
**Response**:
```json
{
  "id": "integer",
  "username": "string",
  "access_token": "string",
  "token_type": "string"
}
```

### Organization Management
#### Create Organization
`POST /organizations/create/`
**Summary**: API to create a new organization.
**Request**:
```json
{
  "name": "string"
}
```
**Response**:
```json
{
  "id": "integer",
  "name": "string",
  "invite_code": "string"
}
```

#### Join Organization
`POST /organizations/join/`
**Summary**: API to make the user join an organization via an invite-code.
**Request**:
```json
{
  "invite_code": "string"
}
```
**Response**:
```json
{}
```

### Cluster Management
#### Create Cluster
`POST /clusters/create/`
**Summary**: API to create a new cluster.
**Request**:
```json
{
  "name": "string",
  "total_ram": "integer",
  "total_cpu": "number",
  "total_gpu": "integer"
}
```
**Response**:
```json
{
  "id": "integer",
  "name": "string",
  "total_ram": "integer",
  "total_cpu": "number",
  "total_gpu": "integer",
  "available_ram": "integer",
  "available_cpu": "number",
  "available_gpu": "integer"
}
```

#### Get Cluster
`GET /clusters/get_cluster/`
**Summary**: API to get cluster details based on either name or id of the cluster.
**Request**:
```json
{
  "id": "integer",
  "cluster_name": "string"
}
```
**Response**:
```json
{
  "id": "integer",
  "name": "string",
  "total_ram": "integer",
  "total_cpu": "number",
  "total_gpu": "integer",
  "available_ram": "integer",
  "available_cpu": "number",
  "available_gpu": "integer"
}
```

### Deployment Management
#### Create Deployment
`POST /deployments/create/`
**Summary**: API to create a new deployment within the given cluster.
**Request**:
```json
{
  "name": "string",
  "cluster_id": "integer",
  "image_path": "string",
  "ram_required": "integer",
  "cpu_required": "integer",
  "gpu_required": "integer",
  "priority": "integer"
}
```
**Response**:
```json
{
  "id": "integer",
  "name": "string",
  "cluster_id": "integer",
  "image_path": "string",
  "ram_required": "integer",
  "cpu_required": "integer",
  "gpu_required": "integer",
  "status": "string",
  "priority": "integer"
}
```

#### Get Deployment
`GET /deployments/get_deployment/`
**Summary**: API to fetch details of a given deployment within a given cluster.
**Request**:
```json
{
  "id": "integer",
  "deployment_name": "string"
}
```
**Response**:
```json
{
  "id": "integer",
  "name": "string",
  "cluster_id": "integer",
  "image_path": "string",
  "ram_required": "integer",
  "cpu_required": "integer",
  "gpu_required": "integer",
  "status": "string",
  "priority": "integer"
}
```

#### Finish Deployment
`POST /deployments/complete/`
**Summary**: API to change the deployment status to complete.
**Request**:
```json
{
  "id": "integer",
  "deployment_name": "string"
}
```
**Response**:
```json
{
  "id": "integer",
  "name": "string",
  "cluster_id": "integer",
  "image_path": "string",
  "ram_required": "integer",
  "cpu_required": "integer",
  "gpu_required": "integer",
  "status": "string",
  "priority": "integer"
}
```

### Root Endpoint
#### Read Root
`GET /`
**Summary**: Root endpoint for checking if the service is running.
**Response**:
```json
{
  "message": "string"
}
```

---
## Assumptions and Future Recommendations:
- Organization creation will return an invite-code. This invite code can be used by users join organization
- One user can only join one organization
- Priority of deployment is unique i.e, two deployments cannot have the same priority
- Currently, all authenticated users can user all apis without any restriction
- Information related to deployment (whether penning queue or running queue) stored in redis has simple string 
creation approach (instead libraries like pickle and help stored python objects to string and deserialize them as well)
- Deployment status is using string which can be changed to enums
- Usage of logger library to log instead of print statements needs to be implemented
- In the current implementation, the completed deployment api, when called, taken into assumption that the deployment
is in running state
