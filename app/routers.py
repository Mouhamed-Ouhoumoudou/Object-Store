from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
from app.storage_manager import StorageManager
from app.config import Config


router = APIRouter()
data_dir = "data"
storage_manager = StorageManager(base_path=data_dir)
metadata_manager = storage_manager.metadata_manager


# Object name can contain any character, including slashes
@router.put("/objects/{object_name:path}")
async def create_object(
    object_name: str, object: UploadFile = File(...), metadata: dict = {}
):
    data = await object.read()
    version_id = storage_manager.write_object(object_name, data, metadata)
    return {
        "message": f"Object '{object_name}' has been stored.",
        "version_id": version_id,
    }


@router.get("/objects/{object_name:path}")
async def read_object(object_name: str, version_id: str = None):
    data = storage_manager.read_object(object_name, version_id)
    return Response(content=data, media_type="application/octet-stream")


# Can search for objects with a specific key/value pair in their metadata
# ?key=...&value=...&exists=.. each can contain multiple values
@router.get("/objects")
def list_objects(
    with_versions: bool = False, key: str = None, value: str = None, exists: bool = True
):
    """
    List all objects stored in the system.
    If with_versions is True, list all versions of each object and the
    current version.
    If key and value are provided, filter objects by metadata key/value pair.
    """
    if key:
        objects = storage_manager.list_objects_by_key(key, exists, value)
    else:
        objects = storage_manager.list_objects()

    if with_versions:
        objects_with_versions = {}
        for object_name in objects:
            versions = storage_manager.list_versions(object_name)
            version_id = metadata_manager.get_version_id(object_name)
            objects_with_versions[object_name] = {
                "version_id": version_id,  # current version
                "versions": versions,
            }

            objects = objects_with_versions

    return {"objects": objects}


@router.delete("/objects/{object_name:path}")
def delete_object(object_name: str, version_id: str = None):
    if version_id:
        storage_manager.delete_object(object_name, version_id)
        return {
            "message": f"Version '{version_id}' of object '{object_name}' has been deleted."
        }
    else:
        storage_manager.delete_object(object_name)
        return {"message": f"All versions of object '{object_name}' have been deleted."}


# put arbitrary key/value pairs in the metadata of an object
@router.put("/metadata/{object_name:path}")
async def update_metadata(object_name: str, metadata: dict):
    """Add or update a key/value pair in the metadata of an object."""
    # TODO: Check unmutable metadata keys
    metadata_manager.update_metadata(object_name, metadata)
    return {"message": f"Metadata updated for object '{object_name}'."}


@router.get("/metadata/{object_name:path}")
async def read_metadata(object_name: str):
    metadata = metadata_manager.read_metadata(object_name)
    return {"metadata": metadata}


@router.delete("/metadata/{object_name:path}")
async def delete_metadata(object_name: str, keys: list[str]):
    for key in keys:
        metadata_manager.delete_metadata_key(object_name, key)
    return {"message": f"Metadata keys {keys} deleted for object '{object_name}'."}


from pydantic import BaseModel


class ObjectPolicyUpdate(BaseModel):
    max_versions: int


@router.put("/config/object-policy/{object_name}")
def update_object_policy(object_name: str, policy: ObjectPolicyUpdate):
    """
    Update the versioning policy for a specific object.
    """
    Config.OBJECT_POLICIES[object_name] = policy.max_versions
    return {
        "message": f"Policy for '{object_name}' updated to keep max {policy.max_versions} versions"
    }


@router.get("/config/object-policies")
def list_object_policies():
    """
    List all object-specific policies and global configuration.
    """
    return {
        "global_max_versions": Config.MAX_GLOBAL_VERSIONS,
        "min_free_space_mb": Config.MIN_FREE_SPACE_MB,
        "object_policies": Config.OBJECT_POLICIES,
    }
