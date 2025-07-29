import logging
import os
import shutil
import uuid
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path

from minio import Minio
from minio.error import S3Error

from scorep_db.config import Config, RecordMode

logger = logging.getLogger(__name__)


class ObjectStore(ABC):
    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def upload_experiment(
        self, experiment_path: Path, new_experiment_directory_path: str
    ) -> None:
        pass

    @abstractmethod
    def download_experiment(self, source_path: str, target_path: Path) -> None:
        pass

    @abstractmethod
    def generate_new_experiment_path(self) -> str:
        pass

    @abstractmethod
    def clear_storage(self) -> None:
        pass

    @abstractmethod
    def get_storage_path(self) -> str:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the storage is reachable and configured correctly."""
        pass


class FilesystemObjectStore(ObjectStore):
    def __init__(self, config: Config):
        super().__init__(config)
        self.offline_directory: Path = Path(config.record_local_directory)

    @staticmethod
    def _copy_recursive(source, target):
        src_dir = source
        dst_dir = target
        os.makedirs(dst_dir, exist_ok=True)

        for item in os.listdir(src_dir):
            s = os.path.join(src_dir, item)
            d = os.path.join(dst_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        logging.info(f"Copied experiment directory to {dst_dir}")

    def upload_experiment(
        self, experiment_path: Path, new_experiment_directory_path: str
    ) -> None:
        target = self.offline_directory / Path(new_experiment_directory_path)
        self._copy_recursive(experiment_path, target)

    def download_experiment(self, source: Path, target: Path) -> None:
        source_ = self.offline_directory / source
        self._copy_recursive(source_, target)

    def generate_new_experiment_path(self) -> str:
        return str(uuid.uuid4())

    def clear_storage(self) -> None:
        directory_root = self.offline_directory
        if directory_root.exists():
            for item in directory_root.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            logging.info(
                f"Cleared all contents within the offline storage at {directory_root}"
            )
        else:
            logging.info(f"No offline storage found at {directory_root}")

    def get_storage_path(self) -> str:
        return str(self.offline_directory)

    def health_check(self, min_free_space_mb: int = 100) -> bool:
        """Check if the offline directory exists and is writable."""
        path = self.offline_directory
        if not path.exists():
            logger.warning("Offline storage directory '%s' does not exist.", path)
            return False

        if not os.access(path, os.R_OK):
            logger.error("Offline storage directory '%s' is not readable.", path)
            return False
        if not os.access(path, os.W_OK):
            logger.error(f"Offline storage directory '%s' is not writable.", path)
            return False

        try:
            test_file = path / ".health_check"
            with open(test_file, "w") as f:
                f.write("test")
            test_file.unlink()  # Testdatei entfernen
        except Exception as e:
            logger.error(
                "Failed to write to the offline storage directory '%s': %s",
                path,
                e,
            )
            return False

        stat = os.statvfs(path)
        free_space_mb = stat.f_bavail * stat.f_frsize / (1024 * 1024)
        if free_space_mb < min_free_space_mb:
            logger.warning(
                "Offline storage directory '%s' has low free space: %.2f MB. Minimum required: %d MB.",
                path,
                free_space_mb,
                min_free_space_mb,
            )
            return False

        logger.info(
            "Offline storage directory '%s' passed health check. Free space: %.2f MB.",
            path,
            free_space_mb,
        )
        return True


class S3ObjectStore(ObjectStore):
    def __init__(self, config: Config):
        super().__init__(config)
        self.endpoint = f"{config.record_s3_hostname}:{config.record_s3_port}"
        self.access_key = config.record_s3_user
        self.secret_key = config.record_s3_password

        self.bucket_name = config.record_s3_bucket_name

        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )

    def upload_experiment(
        self, experiment_path: Path, new_experiment_directory_path: str
    ) -> None:
        self.ensure_bucket_exists(self.bucket_name)

        base_dir = new_experiment_directory_path

        for root, dirs, files in os.walk(experiment_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                object_name = os.path.relpath(file_path, experiment_path)
                if base_dir:
                    object_name = os.path.join(base_dir, object_name)

                try:
                    self.client.fput_object(self.bucket_name, object_name, file_path)
                    logging.info(
                        f"Successfully uploaded {file_name} to {self.bucket_name}/{object_name}"
                    )
                except S3Error as e:
                    logging.error(f"Failed to upload {file_name}: {e}")

    def download_experiment(
        self, experiment_directory_path: str, local_directory: Path
    ) -> None:
        try:
            objects = self.client.list_objects(
                self.bucket_name,
                prefix=experiment_directory_path,
                recursive=True,
            )
            for obj in objects:
                # Construct the local file path
                local_file_path = local_directory / obj.object_name[
                    len(experiment_directory_path) :
                ].lstrip("/")
                local_file_path.parent.mkdir(parents=True, exist_ok=True)

                # Download the object
                self.client.fget_object(
                    self.bucket_name, obj.object_name, str(local_file_path)
                )
                logging.info(
                    f"Successfully downloaded {obj.object_name} to {local_file_path}"
                )

        except S3Error as e:
            logging.error(
                f"Failed to download experiment from {experiment_directory_path}: {e}"
            )

    def ensure_bucket_exists(self, bucket_name):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)
            logging.info(f"Bucket '{bucket_name}' created.")
        else:
            logging.info(f"Bucket '{bucket_name}' already exists.")

    def generate_new_experiment_path(self) -> str:
        return str(uuid.uuid4())

    def clear_storage(self) -> None:
        try:
            objects = self.client.list_objects(self.bucket_name, recursive=True)
            for obj in objects:
                self.client.remove_object(self.bucket_name, obj.object_name)
            logging.info(f"Cleared online storage bucket '{self.bucket_name}'")
        except S3Error as e:
            logging.error(f"Failed to clear online storage: {e}")

    def get_storage_path(self) -> str:
        return f"{self.endpoint}/{self.bucket_name}"

    def health_check(self) -> bool:
        """Check if the online object store is reachable and bucket exists."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                logger.warning(
                    "Online storage bucket '%s' does not exist.",
                    self.bucket_name,
                )
                return False

            test_object_name = "health_check_test_object"
            test_content = b"health check"
            try:
                self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=test_object_name,
                    data=BytesIO(test_content),
                    length=len(test_content),
                )
                logger.info(
                    "Successfully wrote test object '%s' to bucket '%s'.",
                    test_object_name,
                    self.bucket_name,
                )

                self.client.remove_object(self.bucket_name, test_object_name)
                logger.info(
                    "Successfully deleted test object '%s' from bucket '%s'.",
                    test_object_name,
                    self.bucket_name,
                )
            except S3Error as e:
                logger.error(
                    "Failed to write test object to bucket '%s': %s",
                    self.bucket_name,
                    e,
                )
                return False

            logger.info(
                "Online storage bucket '%s' passed health check.",
                self.bucket_name,
            )
            return True

        except S3Error as e:
            logger.error(
                "Failed to check online storage bucket '%s': %s",
                self.bucket_name,
                e,
            )
            return False


def get_object_store(config: Config, mode: RecordMode) -> ObjectStore:
    if mode == RecordMode.LOCAL:
        return FilesystemObjectStore(config)
    elif mode == RecordMode.S3:
        return S3ObjectStore(config)
    else:
        logging.error(f"Unknown mode '{mode}'. Aborting.")
        raise ValueError(f"Unknown mode '{mode}'")
