from .base import BaseCommand


class RepositoryDeleteCommand(BaseCommand):
    """Command to clone a repository"""

    repository_id: str
