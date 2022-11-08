from typing import Optional

from ogr.services.pagure import PagureIssue as OgrPagureIssue
from ogr.services.pagure import PagurePullRequest as OgrPagurePullRequest
from ogr.services.pagure import PagureRelease as OgrPagureRelease

from forgit.config import ConfigSchema
from forgit.forges.abstract import Issue, PullRequest, Release


class PagureIssue(Issue):
    def __init__(self, config: ConfigSchema, issue: OgrPagureIssue) -> None:
        super().__init__(config=config, issue=issue)

    @property
    def assignee(self) -> Optional[str]:
        if self.config.issue.assignees is None:
            return None
        return self.issue.assignee


class PagurePullRequest(PullRequest):
    def __init__(
        self, config: ConfigSchema, pull_request: OgrPagurePullRequest
    ) -> None:
        super().__init__(config=config, pull_request=pull_request)


class PagureRelease(Release):
    def __init__(self, config: ConfigSchema, release: OgrPagureRelease) -> None:
        super().__init__(config=config, release=release)
