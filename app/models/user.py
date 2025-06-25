from typing import List
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    username: str = Field(
        description="Username of the user"
    )
    groups: List[str] = Field(
        default_factory=list,
        description="Groups the user belongs to"
    )
