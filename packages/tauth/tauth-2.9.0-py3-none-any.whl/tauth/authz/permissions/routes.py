import re
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import unquote

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Query,
    Request,
)
from fastapi import status as s
from loguru import logger
from redbaby.pyobjectid import PyObjectId

from ...authz import privileges
from ...entities.models import EntityDAO
from ...schemas import Infostar
from ...schemas.gen_fields import GeneratedFields
from ...settings import Settings
from ...utils import creation, reading
from ..roles.models import RoleDAO
from .models import PermissionDAO
from .schemas import PermissionIn, PermissionIntermediate, PermissionUpdate

service_name = Path(__file__).parents[1].name
router = APIRouter(
    prefix=f"/{service_name}/permissions", tags=[service_name + " 🔐"]
)


@router.post("", status_code=s.HTTP_201_CREATED)
@router.post("/", status_code=s.HTTP_201_CREATED, include_in_schema=False)
async def create_one(
    permission_in: PermissionIn = Body(
        openapi_examples=PermissionIn.get_permission_create_examples()
    ),
    infostar: Infostar = Depends(privileges.is_valid_admin),
):
    logger.debug(f"Creating permission: {permission_in}.")
    logger.debug(
        f"Fetching entity ref from handle: {permission_in.entity_ref!r}"
    )
    entity_ref = EntityDAO.from_handle_to_ref(
        permission_in.entity_ref.handle,
        owner_handle=permission_in.entity_ref.owner_handle,
    )
    if not entity_ref:
        raise HTTPException(
            s.HTTP_400_BAD_REQUEST, detail="Invalid entity handle"
        )
    schema_in = PermissionIntermediate(
        entity_ref=entity_ref,
        **permission_in.model_dump(exclude={"entity_ref"}),
    )
    permission = creation.create_one(
        schema_in, PermissionDAO, infostar=infostar
    )
    return GeneratedFields(**permission.model_dump(by_alias=True))


@router.get("/{permission_id}", status_code=s.HTTP_200_OK)
@router.get(
    "/{permission_id}/", status_code=s.HTTP_200_OK, include_in_schema=False
)
async def read_one(
    permission_id: PyObjectId,
    infostar: Infostar = Depends(privileges.is_valid_user),
) -> PermissionDAO:
    logger.debug(f"Reading permission {permission_id!r}.")
    permission = reading.read_one(
        infostar=infostar,
        model=PermissionDAO,
        identifier=permission_id,
    )
    return permission


@router.get("", status_code=s.HTTP_200_OK)
@router.get("/", status_code=s.HTTP_200_OK, include_in_schema=False)
async def read_many(
    request: Request,
    infostar: Infostar = Depends(privileges.is_valid_user),
    name: str | None = Query(None),
    ends_with: str | None = Query(None),
    entity_handle: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(1024, gt=0, le=1024),
):
    logger.debug(f"Reading permissions with filters: {request.query_params}")
    # Decode the URL-encoded query parameters
    decoded_query_params = {
        key: unquote(value) if isinstance(value, str) else value
        for key, value in request.query_params.items()
    }
    if name:
        decoded_query_params["name"] = {  # type: ignore
            "$regex": re.escape(name),
            "$options": "i",
        }
    if ends_with:
        decoded_query_params.pop("ends_with")
        decoded_query_params["name"] = {  # type: ignore
            "$regex": f"{ends_with}$",
        }
    if entity_handle:
        handle = decoded_query_params.pop("entity_handle")
        decoded_query_params["entity_ref.handle"] = handle
    logger.debug(f"Decoded query params: {decoded_query_params}")
    permissions = reading.read_many(
        infostar=infostar,
        model=PermissionDAO,
        **decoded_query_params,
    )
    return permissions


@router.patch("/{permission_id}", status_code=s.HTTP_204_NO_CONTENT)
@router.patch(
    "/{permission_id}/",
    status_code=s.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
async def update(
    permission_id: PyObjectId,
    permission_update: PermissionUpdate = Body(
        openapi_examples=PermissionUpdate.get_permission_update_examples()
    ),
    infostar: Infostar = Depends(privileges.is_valid_admin),
):
    logger.debug(f"Updating permission with ID: {permission_id!r}.")
    permission = reading.read_one(
        infostar=infostar,
        model=PermissionDAO,
        identifier=permission_id,
    )

    if permission_update.name:
        permission.name = permission_update.name
    if permission_update.description:
        permission.description = permission_update.description
    if permission_update.entity_ref:
        entity_ref = EntityDAO.from_handle_to_ref(
            permission_update.entity_ref.handle,
            permission_update.entity_ref.owner_handle,
        )
        if not entity_ref:
            raise HTTPException(
                s.HTTP_400_BAD_REQUEST, detail="Invalid entity handle"
            )
        permission.entity_ref = entity_ref

    permission.updated_at = datetime.now(UTC)

    permission_coll = PermissionDAO.collection(
        alias=Settings.get().REDBABY_ALIAS
    )
    permission_coll.update_one(
        {"_id": permission.id},
        {"$set": permission.model_dump()},
    )


@router.delete("/{permission_id}", status_code=s.HTTP_204_NO_CONTENT)
@router.delete(
    "/{permission_id}/",
    status_code=s.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
async def delete(
    permission_id: PyObjectId,
    background_tasks: BackgroundTasks,
    infostar: Infostar = Depends(privileges.is_valid_user),
):
    # We need to block deleting a permission if a role is using it.
    logger.debug(f"Deleting permission with ID: {permission_id!r}.")
    logger.debug(
        f"Checking if permission {permission_id!r} is used by a role."
    )
    roles = reading.read_many(
        infostar=infostar,
        model=RoleDAO,
        limit=1024,
        offset=0,
        **{"permissions": permission_id},
    )
    if roles:
        role_names = [role.name for role in roles]
        logger.debug(
            f"Permission {permission_id!r} is used by role(s): {role_names}."
        )
        raise HTTPException(
            status_code=s.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete permission {str(permission_id)!r} because it is used by role(s): {role_names}.",
        )

    permission_coll = PermissionDAO.collection(
        alias=Settings.get().REDBABY_ALIAS
    )
    permission_coll.delete_one({"_id": permission_id})
    background_tasks.add_task(remove_permission_from_entities, permission_id)


def remove_permission_from_entities(permission_id: PyObjectId) -> None:
    logger.debug(f"Removing permission {permission_id!r} from entities.")

    entity_coll = EntityDAO.collection(alias=Settings.get().REDBABY_ALIAS)

    result = entity_coll.update_many(
        {"permissions": permission_id},
        {"$pull": {"permissions": permission_id}},
    )

    logger.debug(
        f"Removed permission {permission_id!r} from {result.modified_count} entities."
    )
