from typing import List, Dict, Union, Any

from ogr.abstract import GitService, IssueStatus, PRStatus
from ogr.abstract import GitProject as OgrGitProject
from ogr.services.github import GithubService
from ogr.services.gitlab import GitlabService
from ogr.services.pagure import PagureService

from forgit.config import ConfigSchema
from forgit.enums import PostType
from forgit.exceptions import PagureGitConvertorException
from forgit.forges.github import GitHubIssue, GitHubPullRequest, GitHubRelease
from forgit.forges.gitlab import GitLabIssue, GitLabPullRequest, GitLabRelease
from forgit.forges.pagure import PagureIssue, PagurePullRequest, PagureRelease
from forgit.messages import (
    USE_SUBCLASS,
    NOT_IMPLEMENTED,
    OPENED_PR_AS_ISSUE_TITLE,
    HEADER_TEMPLATE,
    OPENED_PR_HEADER_TEMPLATE,
)

IssuesDict = Union[
    dict[int, GitHubIssue], dict[int, GitLabIssue], dict[int, PagureIssue]
]
PRsDict = Union[
    dict[int, GitHubPullRequest],
    dict[int, GitLabPullRequest],
    dict[int, PagurePullRequest],
]
ReleaseList = Union[list[GitHubRelease], list[GitLabRelease], list[PagureRelease]]


class GitProject:
    service: GitService

    def __init__(self, namespace: str, repo: str, config: ConfigSchema) -> None:
        self.project: OgrGitProject = self.service.get_project(
            namespace=namespace, repo=repo
        )
        self.config = config

    def get_issues(self) -> IssuesDict:
        raise NotImplementedError(USE_SUBCLASS)

    def get_pull_requests(self) -> PRsDict:
        raise NotImplementedError(USE_SUBCLASS)

    def get_releases(self) -> ReleaseList:
        raise NotImplementedError(USE_SUBCLASS)

    @staticmethod
    def _get_all_comments(source_issue_data: Dict[str, Any]) -> str:
        pass

    def _create_issue_template_args(
        self, source_issue_data: Dict[str, Any]
    ) -> Dict[str, str]:
        d = source_issue_data

        result = {
            "title": d["title"],
            "body": HEADER_TEMPLATE.format(
                what=PostType.issue, link=d["url"], date=d["created"], user=d["author"]
            )
            + d["description"],
        }
        if self.config.issue.shorten:
            result["body"] = result["body"] + self._get_all_comments(source_issue_data)
        if self.config.issue.assignees:
            result["assignees"] = d.get("assignees")
        if self.config.issue.labels:
            result["labels"] = d.get("labels")

        return result

    def _create_pr_template_args(
        self, source_pr_data: Dict[str, Any]
    ) -> Dict[str, str]:
        d = source_pr_data

        result = {
            "title": d["title"],
            "body": HEADER_TEMPLATE.format(
                what=PostType.pr, link=d["url"], date=d["created"], user=d["author"]
            )
            + d["description"],
            "target_branch": d["target_branch"],
            "source_branch": d["source_branch"],
        }
        # TODO: shorten body
        return result


class GitHubProject(GitProject):
    def __init__(
        self, token: str, namespace: str, repo: str, config: ConfigSchema
    ) -> None:
        self.service = GithubService(token=token)
        super().__init__(namespace=namespace, repo=repo, config=config)

    def get_issues(self) -> Dict[int, GitHubIssue]:
        ogr_issues = self.project.get_issue_list()
        return {
            ogr_issue.id: GitHubIssue(self.config, ogr_issue)
            for ogr_issue in ogr_issues
        }

    def get_pull_requests(self) -> Dict[int, GitHubPullRequest]:
        ogr_prs = self.project.get_pr_list()
        return {ogr_pr.id: GitHubPullRequest(self.config, ogr_pr) for ogr_pr in ogr_prs}

    def get_releases(self) -> List[GitHubRelease]:
        ogr_releases = self.project.get_releases()
        return [GitHubRelease(self.config, ogr_release) for ogr_release in ogr_releases]

    # TODO: code of these three will probably move to superclass with GL implementation
    def post_issue(self, source_issue_data: Dict[str, Any]) -> bool:
        kwargs = super()._create_issue_template_args(source_issue_data)
        issue = self.project.create_issue(**kwargs)

        if source_issue_data["status"] == IssueStatus.closed:
            issue.close()

        if self.config.issue.shorten:
            return True

        for comment in sorted(
            source_issue_data["comments"], key=lambda item: item.created
        ):
            issue.comment(comment.get_comment())

        return True

    def post_pull_request(self, source_pr_data: Dict[str, Any]) -> bool:
        if self.config.pr.as_issue:
            prev = self.config.issue.shorten
            self.config.issue.shorten = self.config.pr.shorten
            self.post_issue(source_pr_data)
            self.config.issue.shorten = prev
            return True

        d = source_pr_data
        if d["status"] == PRStatus.open and self.config.pr.open_prs_as_issues:
            self.project.create_issue(
                title=OPENED_PR_AS_ISSUE_TITLE.format(pr_id=d["id"]),
                body=OPENED_PR_HEADER_TEMPLATE.format(
                    what=PostType.pr,
                    link=d["url"],
                    date=d["created"],
                    user=d["author"],
                ),
            ).close()
            return True

        kwargs = super()._create_pr_template_args(source_pr_data)
        pr = self.project.create_pr(**kwargs)
        pr.close()

        if self.config.pr.shorten:
            return True

        # TODO: comments
        return True

    def post_release(self, source_release_data: Dict[str, Any]) -> bool:
        raise NotImplementedError(NOT_IMPLEMENTED)


class GitLabProject(GitProject):
    def __init__(
        self, token: str, namespace: str, repo: str, config: ConfigSchema
    ) -> None:
        self.service = GitlabService(token=token)
        super().__init__(namespace=namespace, repo=repo, config=config)

    def get_issues(self) -> Dict[int, GitLabIssue]:
        ogr_issues = self.project.get_issue_list()
        return {
            ogr_issue.id: GitLabIssue(self.config, ogr_issue)
            for ogr_issue in ogr_issues
        }

    def get_pull_requests(self) -> Dict[int, GitLabPullRequest]:
        ogr_prs = self.project.get_pr_list()
        return {ogr_pr.id: GitLabPullRequest(self.config, ogr_pr) for ogr_pr in ogr_prs}

    def get_releases(self) -> List[GitLabRelease]:
        ogr_releases = self.project.get_releases()
        return [GitLabRelease(self.config, ogr_release) for ogr_release in ogr_releases]

    def post_issue(self, source_issue_data: Dict[str, Any]) -> bool:
        raise NotImplementedError(NOT_IMPLEMENTED)

    def post_pull_request(self, source_pr_data: Dict[str, Any]) -> bool:
        raise NotImplementedError(NOT_IMPLEMENTED)

    def post_release(self, source_release_data: Dict[str, Any]) -> bool:
        raise NotImplementedError(NOT_IMPLEMENTED)


class PagureProject(GitProject):
    def __init__(
        self, token: str, namespace: str, repo: str, config: ConfigSchema
    ) -> None:
        self.service = PagureService(token=token)
        super().__init__(namespace=namespace, repo=repo, config=config)

    def get_issues(self) -> Dict[int, PagureIssue]:
        ogr_issues = self.project.get_issue_list()
        return {
            ogr_issue.id: PagureIssue(self.config, ogr_issue)
            for ogr_issue in ogr_issues
        }

    def get_pull_requests(self) -> Dict[int, PagurePullRequest]:
        ogr_prs = self.project.get_pr_list()
        return {ogr_pr.id: PagurePullRequest(self.config, ogr_pr) for ogr_pr in ogr_prs}

    def get_releases(self) -> List[PagureRelease]:
        ogr_releases = self.project.get_releases()
        return [PagureRelease(self.config, ogr_release) for ogr_release in ogr_releases]

    def post_issue(self, source_issue_data: Dict[str, Any]) -> bool:
        raise PagureGitConvertorException("We don't do that here")

    def post_pull_request(self, source_pr_data: Dict[str, Any]) -> bool:
        raise PagureGitConvertorException("We don't do that here")

    def post_release(self, source_release_data: Dict[str, Any]) -> bool:
        raise PagureGitConvertorException("We don't do that here")
