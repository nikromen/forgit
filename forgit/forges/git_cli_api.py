"""
Prepare branches for creating PRs.
"""

from pathlib import Path
from tempfile import mkdtemp
from typing import List

from git import Repo


class GitCliApi:
    def __init__(self, ssh_url: str) -> None:
        self.ssh_url = ssh_url
        self._repo_location = Path(mkdtemp())

        # Lazy properties
        self._repo = None

    @property
    def repo(self) -> Repo:
        if self._repo is not None:
            return self._repo

        self._repo = Repo.clone_from(self.ssh_url, self._repo_location)
        return self._repo

    def create_branch_and_reset_to(self, branch_name: str, commit_sha: str) -> None:
        new_branch = self.repo.create_head(branch_name)
        new_branch.checkout()
        # index and working_tree -> --hard
        self.repo.head.reset(commit_sha, index=True, working_tree=True)

    def push_branches(self, branches: List[str]) -> None:
        # TODO: error handling
        self.repo.git.push("origin", *branches)

    def delete_branches(self, branches: List[str]) -> None:
        # TODO: error handling
        self.repo.git.push("origin", "--delete", *branches)
