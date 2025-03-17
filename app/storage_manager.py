import os
import uuid
from datetime import datetime
from app.metadata_manager import MetadataManager
from app.config import Config
import shutil


class StorageManager:
    """
    Handles interactions with the filesystem for storing, retrieving, and
    deleting objects.
    """

    def __init__(self, base_path: str):
        self.base_path = base_path
        # self.base_path = Config.BASE_PATH
        self.max_global_versions = Config.MAX_GLOBAL_VERSIONS
        self.object_policies = Config.OBJECT_POLICIES
        os.makedirs(self.base_path, exist_ok=True)
        self.metadata_manager = MetadataManager(base_path)

    def _get_object_path(self, object_name: str) -> str:
        """
        Return object path equivalent to the object name.
        With versionnng, the end path is the directory containing all versions.
        """

        return os.path.join(self.base_path, object_name)

    def apply_policy(self, object_name: str):
        """
        Apply the versioning policy to the specified object.
        """
        object_dir = self._get_object_path(object_name)
        if not os.path.exists(object_dir):
            raise FileNotFoundError(f"Object '{object_name}' not found")

        # Récupérer la limite de versions pour cet objet ou utiliser la limite globale
        max_versions = self.object_policies.get(object_name, self.max_global_versions)

        # Lister et supprimer les versions si nécessaire
        versions = self._get_all_versions(object_dir)
        if len(versions) > max_versions:
            for version in versions[max_versions:]:
                version_path = self._get_version_path(object_name, version)
                os.remove(version_path)

    def check_and_free_space(self):
        """
        Check available disk space and free it if below the minimum threshold.
        """
        total, used, free = shutil.disk_usage(self.base_path)
        free_mb = free // (1024 * 1024)

        obj_list = self.metadata_manager.list_objects()
        while free_mb < Config.MIN_FREE_SPACE_MB and obj_list:
            obj_name = obj_list.pop(0)
            object_dir = self._get_object_path(obj_name)
            versions = self._get_all_versions(object_dir)
            if len(versions) > 1:
                # Supprimer la version la plus ancienne
                oldest_version_path = os.path.join(object_dir, versions[0])
                os.remove(oldest_version_path)
        # TODO: check if enough space is freed
        # if not, delete more objects, or raise an exception if no more
        # objects to delete

    def _get_version_path(self, object_name: str, version_id: str) -> str:
        """Return the file path for a specific version of an object."""
        return os.path.join(self._get_object_path(object_name), version_id)

    def _get_all_versions(self, object_path: str) -> str:
        """Return sorted list of all versions path of an object."""
        versions = [
            f
            for f in os.listdir(object_path)
            if os.path.isfile(os.path.join(object_path, f))
        ]
        versions.remove(self.metadata_manager.METADATA_FILE)
        versions.sort(reverse=True)
        return versions

    def _generate_version_id(self) -> str:
        """
        Generate a unique version ID.
        First bit is the timestamp, second bit is a random UUID.
        Timestamp is used to sort versions in descending order.
        We assume no two versions are created in the same microsecond.
        """

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S-%f")
        unique_id = uuid.uuid4().hex
        return f"{timestamp}-{unique_id}"

    def get_current_version(self, object_name: str) -> str:
        """Return the version ID of the current version of an object."""
        object_path = self._get_object_path(object_name)
        if not os.path.exists(object_path):
            raise FileNotFoundError(f"Object '{object_name}' not found")
        metadata = self.metadata_manager.read_metadata(object_path)
        return metadata.get("version_id")

    def write_object(self, object_name: str, data: bytes, metadata: dict = {}) -> str:
        """Write the data to a file with the given object name and return the version ID."""
        object_path = self._get_object_path(object_name)
        os.makedirs(object_path, exist_ok=True)

        version_id = self._generate_version_id()
        version_path = self._get_version_path(object_name, version_id)
        with open(version_path, "wb") as file:
            file.write(data)
        # Update metadata
        self.metadata_manager.update_metadata(object_path, metadata, version_id)
        self.metadata_manager.add_object(object_name)

        # Appliquer la politique de versionnement
        self.apply_policy(object_name)
        # Vérifier l'espace disque disponible
        self.check_and_free_space()

        return version_id

    def read_object(self, object_name: str, version_id: str = None) -> bytes:
        """Read the data from a file with the given object name."""
        object_path = self._get_object_path(object_name)
        if not os.path.exists(object_path):
            raise FileNotFoundError(f"Object with name '{object_name}' not found")

        if version_id:
            version_path = self._get_version_path(object_name, version_id)
            if not os.path.exists(version_path):
                raise FileNotFoundError(
                    f"Version '{version_id}' of object '{object_name}' not found"
                )
            with open(version_path, "rb") as file:
                return file.read()
        else:
            # Read the latest version
            versions = self._get_all_versions(object_path)
            if not versions:
                # Should not happen if the object exists
                raise FileNotFoundError(f"No versions found for object '{object_name}'")
            latest_version_path = os.path.join(object_path, versions[0])
            with open(latest_version_path, "rb") as file:
                return file.read()

    def _delete_empty_dirs(self, dir_path: str):
        """
        Recursively delete empty directories up to the base path.
        To clean up empty directories after deleting objects named with slashes.
        """
        if not os.listdir(dir_path):
            os.rmdir(dir_path)
            parent_dir = os.path.dirname(dir_path)
            if parent_dir != self.base_path:
                self._delete_empty_dirs(parent_dir)

    def delete_object(self, object_name: str, version_id: str = None):
        """Delete the file with the given object name."""
        object_path = self._get_object_path(object_name)
        if not os.path.exists(object_path):
            raise FileNotFoundError(f"Object with name '{object_name}' not found")
        if version_id:
            version_path = self._get_version_path(object_name, version_id)
            if not os.path.exists(version_path):
                raise FileNotFoundError(
                    f"Version '{version_id}' of object '{object_name}' not found"
                )
            os.remove(version_path)
            # Check if the object directory is empty
            versions = self._get_all_versions(object_path)
            if not versions:
                # No versions left, delete metadata
                self.metadata_manager.delete_object(object_path, object_name)
                self._delete_empty_dirs(object_path)
        else:
            # Delete all versions
            versions = self._get_all_versions(object_path)
            for version in versions:
                version_path = os.path.join(object_path, version)
                os.remove(version_path)
            # Delete metadata
            self.metadata_manager.delete_object(object_path, object_name)
            self._delete_empty_dirs(object_path)

    def list_versions(self, object_name: str) -> list[str]:
        """List all versions of an object."""
        object_dir = self._get_object_path(object_name)
        if not os.path.exists(object_dir):
            raise FileNotFoundError(f"Object '{object_name}' not found")
        versions = self._get_all_versions(object_dir)
        return versions

    def list_objects(self) -> list[str]:
        """
        List all objects stored in the base directory.
        Use the metadata manager to get the list of objects.
        """

        return self.metadata_manager.list_objects()

    def list_objects_by_key(
        self, key: str, exists: bool = True, value: str = None
    ) -> list[str]:
        results = self.metadata_manager.filter_objects_by_metadata(key, exists, value)

        return results
