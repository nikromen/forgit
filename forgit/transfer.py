from typing import Union, List, Optional, Dict, Any

from forgit.config import ConfigSchema
from forgit.constants import SOURCE_PR_BRANCH, TARGET_PR_BRANCH
from forgit.enums import TargetTypes
from forgit.forges.github import GitHubIssue, GitHubPullRequest, GitHubRelease
from forgit.forges.gitlab import GitLabIssue, GitLabPullRequest, GitLabRelease
from forgit.forges.pagure import PagurePullRequest
from forgit.forges.git_cli_api import GitCliApi
from forgit.forges.project import (
    GitHubProject,
    GitLabProject,
    PagureProject,
    IssuesDict,
    PRsDict,
)
from forgit.parser import parse_data

ForgeClient = Union[GitHubProject, GitLabProject, PagureProject]
PRsList = Union[
    list[tuple[int, GitHubPullRequest]],
    list[tuple[int, GitLabPullRequest]],
    list[tuple[int, PagurePullRequest]],
]


MAP_TARGET_CLS_TO_TYPE: Dict[TargetTypes, Dict[str, Any]] = {
    TargetTypes.issue: {
        GitHubProject.__name__: GitHubIssue,
        GitLabProject.__name__: GitLabIssue,
    },
    TargetTypes.pr: {
        GitHubProject.__name__: GitHubPullRequest,
        GitLabProject.__name__: GitLabPullRequest,
    },
    TargetTypes.release: {
        GitHubProject.__name__: GitHubRelease,
        GitLabProject.__name__: GitLabRelease,
    },
}


class Transferator3000:
    """
    Transferator makes sure your project transfers just fine, so you can take a nap.
    """

    def __init__(
        self, source: ForgeClient, target: ForgeClient, config: ConfigSchema
    ) -> None:
        self.source = source
        self.target = target
        self.config = config
        self.source_prs = self.source.get_pull_requests()

        self._branches: Optional[List[str]] = None
        self._branches_were_prepared: bool = False

        # Lazy properties
        self._sorted_source_prs: Optional[PRsList] = None
        self._git_cli_api: Optional[GitCliApi] = None

    @property
    def sorted_source_prs(self) -> PRsList:
        if self._sorted_source_prs is not None:
            return self._sorted_source_prs

        self._sorted_source_prs = sorted(
            list(self.source_prs.items()), key=lambda tpl: tpl[0]
        )
        return self._sorted_source_prs

    @property
    def git_cli_api(self) -> GitCliApi:
        if self._git_cli_api is not None:
            return self._git_cli_api

        self._git_cli_api = GitCliApi(self.config.pr.ssh_url)
        return self._git_cli_api

    def check_user_map(self) -> None:
        # TODO: check tokens and user-map
        pass

    def _fill_gap(self, from_: int, issues: IssuesDict, prs: PRsDict) -> int:
        to = from_
        while not (issues.get(to) or prs.get(to)):
            dummy_issue = self.target.project.create_issue(
                title="'[forgit] Dummy issue to fill space between IDs",
                body="Dummy issue to fill space between IDs.",
            )
            dummy_issue.close()
            to += 1

        return to - 1

    def _transfer_releases(self) -> None:
        releases = sorted(self.source.get_releases(), key=lambda release: release.tag)
        for rel in releases:
            source_release_data = parse_data(
                rel,
                MAP_TARGET_CLS_TO_TYPE[TargetTypes.release][
                    self.target.__class__.__name__
                ],
            )
            self.target.post_release(source_release_data)

    def _prepare_branches_for_pulls(self, id_matcher: int) -> List[str]:
        start = 0
        for index, _ in self.sorted_source_prs:
            if index == id_matcher:
                start = index

        branches = []
        for pr_id, pr in self.sorted_source_prs[start : len(self.sorted_source_prs)]:
            self.git_cli_api.create_branch_and_reset_to(
                SOURCE_PR_BRANCH.format(pr_id=pr_id), pr.new_sha
            )
            self.git_cli_api.create_branch_and_reset_to(
                TARGET_PR_BRANCH.format(pr_id=pr_id), pr.old_sha
            )

            branches.extend(
                [
                    SOURCE_PR_BRANCH.format(pr_id=pr_id),
                    TARGET_PR_BRANCH.format(pr_id=pr_id),
                ]
            )

        self.git_cli_api.push_branches(branches)
        return branches

    def _clear_branches(self, branches: List[str]) -> None:
        # TODO: retry mechanism
        self.git_cli_api.delete_branches(branches)

    def _transfer_issue_or_pr(
        self, id_matcher: int, sources: Union[IssuesDict, PRsDict], posting_issue: bool
    ) -> bool:
        target_type = TargetTypes.issue if posting_issue else TargetTypes.pr

        source = sources.get(id_matcher)
        if source is None:
            return False

        source_data = parse_data(
            source, MAP_TARGET_CLS_TO_TYPE[target_type][self.target.__class__.__name__]
        )
        if posting_issue:
            self.target.post_issue(source_data)
            return True

        if not self._branches_were_prepared:
            self._branches = self._prepare_branches_for_pulls(id_matcher)
            self._branches_were_prepared = True

        self.target.post_pull_request(source_data)
        return True

    def transfer(self, id_matcher: int = 0) -> None:
        # TODO: retry mechanism
        self.check_user_map()

        # TODO: while
        source_issues = self.source.get_issues()
        for _ in range(len(source_issues) + len(self.source_prs)):
            id_matcher += 1

            if self._transfer_issue_or_pr(id_matcher, source_issues, True):
                continue

            if self._transfer_issue_or_pr(id_matcher, self.source_prs, False):
                continue

            if self.config.match_ids:
                id_matcher = self._fill_gap(id_matcher, source_issues, self.source_prs)

        if self._branches is not None:
            self._clear_branches(self._branches)

        if self.config.transfer_releases:
            self._transfer_releases()
