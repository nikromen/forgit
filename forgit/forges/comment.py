from forgit.forges.abstract import Comment
from forgit.messages import NOT_IMPLEMENTED


class IssueComment(Comment):
    def get_comment(self) -> str:
        raise NotImplementedError(NOT_IMPLEMENTED)


class PullRequestComment(Comment):
    def get_comment(self) -> str:
        raise NotImplementedError(NOT_IMPLEMENTED)
