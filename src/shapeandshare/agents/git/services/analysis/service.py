import logging
from pathlib import Path

from pydantic import BaseModel

from ....core.framework.contracts.dtos.service_response import ServiceResponse
from ..repository.service import RepositoryService

logger = logging.getLogger()


class AnalysisService(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    repository_service: RepositoryService
    default_extensions: set[str]
    default_included_files: set[str]
    default_excluded_dirs: set[str]

    def extract_repository_content(
        self,
        repository_id: str,
        allowed_extensions: set[str] | None = None,
        included_files: set[str] | None = None,
        excluded_dirs: set[str] | None = None,
    ) -> ServiceResponse:
        logger.info("extracting repository content")

        try:
            # Get all files from repository service
            files_response: ServiceResponse = self.repository_service.files_list(repository_id=repository_id)
            logger.info(f"found {len(files_response.data['files'])} files")
            if not files_response.success:
                return files_response

            # Apply filters
            filtered_files = self._filter_files(
                files_response.data["files"],
                allowed_extensions or self.default_extensions,
                included_files or self.default_included_files,
                excluded_dirs or self.default_excluded_dirs,
            )
            logger.info(f"filtered {len(filtered_files)} files")
            # Read content of filtered files
            content: dict = {}
            for file_path in filtered_files:
                logger.info(f"file {file_path}")
                content_response = self.repository_service.file_content_read(
                    repository_id=repository_id, file_path=file_path
                )
                logger.info("content {}".format(content_response))
                if content_response.success:
                    content[file_path] = content_response.data["content"]

            msg: str = f"extracted repository content {content}"
            logger.info(msg)
            return ServiceResponse(success=True, data={"content": content})
        except Exception as error:
            logger.error(str(error))
            return ServiceResponse(success=False, error=str(error))

    def _filter_files(
        self, files: list[str], allowed_extensions: set[str], included_files: set[str], excluded_dirs: set[str]
    ) -> list[str]:
        """Filter files based on rules"""
        filtered = []
        for file_path in files:
            path = Path(file_path)

            # Check excluded directories
            if any(excluded in str(path.parent) for excluded in excluded_dirs):
                continue

            # Check if file should be included
            if path.name in included_files or path.suffix.lower() in allowed_extensions:
                filtered.append(file_path)

        return filtered
