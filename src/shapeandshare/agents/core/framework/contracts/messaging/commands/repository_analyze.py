from .base import BaseCommand


class RepositoryAnalyzeCommand(BaseCommand):
    """Command to analyze a repository"""

    repository_id: str
    collection_id: str
    analysis_config: dict
