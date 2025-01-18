import logging
import os
import shutil
from pathlib import Path

from pydantic import BaseModel

from ....core.framework.contracts.dtos.service_response import ServiceResponse
from ....core.infrastructure.persistence.git.dao import GitDao

logger = logging.getLogger()


class RepositoryService(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    """Handles repository operations"""

    git: GitDao

    def clone(self, url: str, repository_id: str, retry: int = 10) -> ServiceResponse:
        """Clone a repository"""
        count: int = 0
        try:
            if count >= retry:
                return ServiceResponse(success=False, error="Exceeded maximum retries while cloning")
            # Create temporary directory for repository
            logger.info("cloning repository")
            repo_metadata_dir: Path = Path(os.environ["DATA_BASE_DIR"]) / "repos" / repository_id
            if repo_metadata_dir.exists():
                shutil.rmtree(repo_metadata_dir)
            repo_metadata_dir.mkdir(parents=True, exist_ok=True)

            # Clone repository
            self.git.clone_repository(url, (repo_metadata_dir / "repo"))

            return ServiceResponse(success=True, data={"repository_id": repository_id})
        except Exception as error:
            return ServiceResponse(success=False, error=str(error))

    def delete(self, repository_id: str) -> ServiceResponse:
        """Delete a repository"""
        try:
            # Create temporary directory for repository
            logger.info("deleting repository")
            repo_metadata_dir: Path = Path(os.environ["DATA_BASE_DIR"]) / "repos" / repository_id

            msg: str = f"cleaning up {repo_metadata_dir}"
            logger.info(msg)
            shutil.rmtree(repo_metadata_dir)

            return ServiceResponse(success=True, data={"repository_id": repository_id})
        except Exception as e:
            return ServiceResponse(success=False, error=str(e))

    def files_list(self, repository_id: str) -> ServiceResponse:
        """List all files in repository"""
        repo_path: Path = Path(os.environ["DATA_BASE_DIR"]) / "repos" / repository_id
        try:
            files = []
            for item in Path(repo_path).glob("**/*"):
                if item.is_file():
                    files.append(str(item.relative_to(repo_path)))
            return ServiceResponse(success=True, data={"files": files})
        except Exception as e:
            return ServiceResponse(success=False, error=str(e))

    def file_content_read(self, repository_id: str, file_path: str) -> ServiceResponse:
        """Read content of a specific file"""
        repo_path: Path = Path(os.environ["DATA_BASE_DIR"]) / "repos" / repository_id
        full_path: Path = repo_path / file_path
        try:
            with open(file=full_path, mode="r", encoding="utf-8") as file:
                content = file.read()
            return ServiceResponse(success=True, data={"content": content})
        except Exception as e:
            return ServiceResponse(success=False, error=str(e))
