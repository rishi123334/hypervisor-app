from fastapi import FastAPI
from app.routes import user, cluster, deployment, organization
from app.db.base import engine, Base

app = FastAPI()

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(organization.router, prefix="/organizations", tags=["organizations"])
app.include_router(cluster.router, prefix="/clusters", tags=["clusters"])
app.include_router(deployment.router, prefix="/deployments", tags=["deployments"])


def on_startup():
    """
    Create all tables in the database (if they don't already exist)
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")

app.add_event_handler("startup", on_startup)


# Root route
@app.get("/")
def read_root():
    return {"message": "Welcome to the HyperVisor Service"}
