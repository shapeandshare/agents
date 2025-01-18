from .base import BaseCommand


class RepositoryCloneCommand(BaseCommand):
    """Command to clone a repository"""

    url: str
    repository_id: str
    collection_id: str
