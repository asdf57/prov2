from pydantic import BaseModel, Field

class FlagModel(BaseModel):
    """Base model for flags"""
    ...

class ServerFlagModel(FlagModel):
    enable_k8s: bool = Field(
        False, description="Enable Kubernetes on the server"
    )

class DropletFlagModel(FlagModel):
    ...

FLAGS_VALIDATOR = {
    "server": ServerFlagModel,
}
