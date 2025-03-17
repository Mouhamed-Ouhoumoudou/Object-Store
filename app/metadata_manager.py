import json
import os
from datetime import datetime


class MetadataManager:
    """Handles metadatas for objects stored in the storage manager."""

    METADATA_FILE = "metadata.json"

    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        # Create a metadata file for the base path if it doesn't exist
        metadata_path = self._get_metadata_path(self.base_path)
        if not os.path.exists(metadata_path):
            self._write_metadata(metadata_path, {"objects": {}})

    # Same as StorageManager.get_object_path, how to avoid duplication?
    def _get_object_path(self, object_name: str) -> str:
        """Return the path to the object."""
        return os.path.join(self.base_path, object_name)

    def _get_metadata_path(self, object_path: str) -> str:
        """Return metadata path equivalent to the object name."""
        return f"{object_path}/{self.METADATA_FILE}"

    def _read_metadata(self, metadata_path: str) -> dict:
        """Read the metadata from a file."""
        current_metadata = {}
        if os.path.exists(metadata_path) and os.path.getsize(metadata_path) > 0:
            with open(metadata_path, "r") as file:
                current_metadata = json.load(file)
        return current_metadata

    def _write_metadata(self, metadata_path: str, metadata: dict):
        """Write the metadata to a file."""
        with open(metadata_path, "w") as file:
            json.dump(metadata, file)

    def get_current_version(self, object_name: str) -> str:
        """Return the version ID of the current version of an object."""
        object_path = self._get_object_path(object_name)
        if not os.path.exists(object_path):
            raise FileNotFoundError(f"Object '{object_name}' not found")
        metadata = self.metadata_manager.read_metadata(object_path)
        return metadata.get("version_id")

    def update_metadata(self, object_path: str, metadata: dict, version_id: str = None):
        # Check if the object exists

        metadata_path = self._get_metadata_path(object_path)
        current_metadata = self._read_metadata(metadata_path)
        current_metadata.update(metadata)
        if version_id:
            current_metadata["version_id"] = version_id
            current_metadata["last_modified"] = datetime.now().isoformat()
        self._write_metadata(metadata_path, current_metadata)

    def read_metadata(self, object_path: str) -> dict:
        metadata_path = self._get_metadata_path(object_path)
        metadata = self._read_metadata(metadata_path)
        return metadata

    def filter_objects_by_metadata(
        self, key: str, exist: bool = True, value: str = None
    ) -> list:
        """
        Filter objects by a specific metadata key/value pair.
        If value is None, return all objects with the key.
        """
        results = []
        global_metadata_path = self._get_metadata_path(self.base_path)
        global_metadata = self._read_metadata(global_metadata_path)

        # Search for the key in each object's metadata
        for object_name, _ in global_metadata["objects"].items():
            object_path = self._get_object_path(object_name)
            object_metadata = self.read_metadata(object_path)
            if key in object_metadata:
                if exist:
                    if value is None or object_metadata[key] == value:
                        results.append(object_name)
                else:
                    if value is None or object_metadata[key] != value:
                        results.append(object_name)

        return results

    def delete_metadata_key(self, object_name: str, key: str):
        object_path = self._get_object_path(object_name)
        metadata_path = self._get_metadata_path(object_path)
        metadata = self._read_metadata(metadata_path)
        metadata.pop(key)
        self._write_metadata(metadata_path, metadata)

    # Global metadata operations
    # We keep list of all objects and global parameters (number of versions, etc.)
    def add_object(self, object_name: str):
        global_metadata = self.read_metadata(self.base_path)
        if "objects" not in global_metadata:
            global_metadata["objects"] = {}
        global_metadata["objects"].update({object_name: {}})

        global_metadata_path = self._get_metadata_path(self.base_path)
        self._write_metadata(global_metadata_path, global_metadata)

    def delete_object(self, object_path: str, object_name: str):
        # Delete metadata file
        metadata_path = self._get_metadata_path(object_path)
        os.remove(metadata_path)
        # Remove object from global metadata
        global_metadata = self.read_metadata(self.base_path)
        global_metadata["objects"].pop(object_name)
        global_metadata_path = self._get_metadata_path(self.base_path)
        self._write_metadata(global_metadata_path, global_metadata)

    def list_objects(self) -> list:
        metadata = self.read_metadata(self.base_path)
        return list(metadata["objects"].keys())
