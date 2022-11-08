from ogr.abstract import Issue as OgrIssue
from ogr.abstract import PullRequest as OgrPullRequest
from ogr.abstract import Release as OgrRelease

from forgit.config import ConfigSchema
from forgit.forges.abstract import Issue, PullRequest, Release


class GitLabIssue(Issue):
    def __init__(self, config: ConfigSchema, issue: OgrIssue) -> None:
        super().__init__(config=config, issue=issue)


class GitLabPullRequest(PullRequest):
    def __init__(self, config: ConfigSchema, pull_request: OgrPullRequest) -> None:
        super().__init__(config=config, pull_request=pull_request)


class GitLabRelease(Release):
    def __init__(self, config: ConfigSchema, release: OgrRelease) -> None:
        super().__init__(config=config, release=release)
