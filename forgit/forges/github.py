from __future__ import annotations

from typing import TYPE_CHECKING

from ogr.abstract import PullRequest as OgrPullRequest
from ogr.abstract import Release as OgrRelease

from forgit.config import ConfigSchema
from forgit.forges.abstract import Issue, PullRequest, Release

if TYPE_CHECKING:
    from ogr.services.github import GithubIssue


class GitHubIssue(Issue):
    def __init__(self, config: ConfigSchema, issue: GithubIssue) -> None:
        super().__init__(config=config, issue=issue)

    @property
    def assignees(self) -> list | None:  # TODO
        if self.config.issue.assignees is None:
            return None
        return self.issue.assignees


class GitHubPullRequest(PullRequest):
    def __init__(self, config: ConfigSchema, pull_request: OgrPullRequest) -> None:
        super().__init__(config=config, pull_request=pull_request)


class GitHubRelease(Release):
    def __init__(self, config: ConfigSchema, release: OgrRelease) -> None:
        super().__init__(config=config, release=release)
