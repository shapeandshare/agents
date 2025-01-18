import os

from git import Repo


class GitDao:
    def clone_repository(self, git_url: str, local_path: str) -> Repo:
        """
        Clone a git repository to local storage.

        Args:
            git_url (str): URL of the git repository
            local_path (str): Local path to clone the repository

        Returns:
            Repo: The cloned git repository object
        """
        if os.path.exists(local_path):
            return Repo(local_path)
        return Repo.clone_from(git_url, local_path)
