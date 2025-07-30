from pydantic import BaseModel
from redbaby.pyobjectid import PyObjectId

from tauth.entities.schemas import EntityRefIn


class GrantIn(BaseModel):
    resource_id: PyObjectId
    entity_ref: EntityRefIn
    permission_name: str


class GrantResponse(BaseModel):
    msg: str = "Granted Access to entity with permission."
    permission: str
    entity_id: str
