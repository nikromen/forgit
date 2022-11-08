from datetime import datetime
from typing import Optional, List

from ogr.abstract import Comment as OgrComment, IssueStatus, PRStatus
from ogr.abstract import Issue as OgrIssue
from ogr.abstract import PullRequest as OgrPullRequest
from ogr.abstract import Release as OgrRelease

from forgit.config import ConfigSchema
from forgit.forges.comment import IssueComment
from forgit.messages import USE_SUBCLASS


class Comment:
    def __init__(self, comment: OgrComment) -> None:
        self.comment = comment

    @property
    def created(self) -> datetime:
        return self.comment.created

    def get_comment(self) -> str:
        raise NotImplementedError(USE_SUBCLASS)


class Schema:
    def __init__(self, config: ConfigSchema) -> None:
        self.config = config


class Issue(Schema):
    def __init__(self, config: ConfigSchema, issue: OgrIssue) -> None:
        super().__init__(config=config)
        self.issue = issue

        # basic attributes which are required
        self.id: int = issue.id
        self.title: str = issue.title
        self.status: IssueStatus = issue.status
        self.description: str = issue.description
        self.author: str = issue.author

        # Lazy required properties
        self._comments: List[IssueComment] = []

    @property
    def comments(self) -> List[IssueComment]:
        if not self._comments:
            return self._comments

        result = []
        for ogr_issue_comment in self.issue.get_comments():
            result.append(IssueComment(ogr_issue_comment))

        self._comments = result
        return self._comments

    @property
    def created(self) -> Optional[datetime]:
        if not self.config.preserve_datetime:
            return None
        return self.issue.created

    @property
    def labels(self) -> Optional[List[str]]:
        # TODO: unify type
        if not self.config.issue.labels:
            return None
        return self.issue.labels

    @property
    def url(self) -> Optional[str]:
        if not self.config.track_urls:
            return None
        return self.issue.url


class PullRequest(Schema):
    def __init__(self, config: ConfigSchema, pull_request: OgrPullRequest) -> None:
        super().__init__(config=config)
        self.pull_request = pull_request

        # basic attributes which are required
        self.id: int = pull_request.id
        self.title: str = pull_request.title
        self.status: PRStatus = pull_request.status
        self.description: str = pull_request.description
        self.author: str = pull_request.author

        # Lazy required properties
        self._comments: List[IssueComment] = []

    @property
    def url(self) -> Optional[str]:
        if not self.config.track_urls:
            return None
        return self.pull_request.url

    @property
    def source_branch(self) -> Optional[str]:
        if not self.config.pr.track_branches:
            return None
        return self.pull_request.source_branch

    @property
    def target_branch(self) -> Optional[str]:
        if not self.config.pr.track_branches:
            return None
        return self.pull_request.target_branch

    @property
    def created(self) -> Optional[datetime]:
        if not self.config.preserve_datetime:
            return None
        return self.pull_request.created

    @property
    def labels(self) -> Optional[List]:
        # TODO: unify type
        if not self.config.pr.labels:
            return None
        return self.pull_request.labels

    @property
    def comments(self) -> List[IssueComment]:
        if not self._comments:
            return self._comments

        result = []  # TODO: convert to pr comments
        for ogr_issue_comment in self.pull_request.get_comments():
            result.append(IssueComment(ogr_issue_comment))

        self._comments = result
        return self._comments

    @property
    def new_sha(self) -> str:
        pass

    @property
    def old_sha(self) -> str:
        pass


class Release(Schema):
    def __init__(self, config: ConfigSchema, release: OgrRelease) -> None:
        super().__init__(config=config)
        self.release = release

        # basic attributes which are required

    @property
    def tag(self) -> str:
        return self.release.tag_name
