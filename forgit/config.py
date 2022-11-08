from pathlib import Path
from tempfile import mkdtemp
from typing import Optional, Any, List, Dict, Union, Type

from git import Repo
from pydantic import BaseModel, root_validator, validator
from yaml import safe_load

from forgit.constants import POSSIBLE_CONFIG_FILE_NAMES
from forgit.messages import (
    CONFIG_FILE_NOT_FOUND_DEFAULT_LOCATION,
    DIFF_STORAGE_CONFIG_ERROR,
    DIFF_NOT_ENABLED_ERROR,
)
from forgit.utils import nested_get


class IssueSchema(BaseModel):
    shorten: bool = False
    assignees: bool = True
    labels: bool = True


class PRSchema(IssueSchema):
    make_pr_comments: bool = True
    track_branches: bool = True
    as_issue: bool = False
    ssh_url: str = ""
    open_prs_as_issues: bool = True

    @validator("ssh_url")
    def ssh_url_must_be_correct(self, ssh_url) -> str:
        if not ssh_url:
            return ssh_url

        # if url is invalid - unable to clone, this will throw an exception about it
        Repo.clone_from(ssh_url, mkdtemp())
        return ssh_url


class ConfigSchema(BaseModel):
    source_project_key: str
    target_project_key: str
    user_map: list[dict[str, str]]
    issue: IssueSchema = IssueSchema()
    pr: PRSchema = PRSchema()
    preserve_datetime: bool = True
    track_urls: bool = True
    match_ids: bool = True
    make_diffs: bool = True
    path_to_store_diffs: str = ""
    transfer_releases: bool = False
    post_message_about_migration: bool = True
    ignore_first_n_ids: int = 0

    @root_validator
    def diffs_must_be_stored_somewhere(cls, values: dict[str, Any]) -> dict[str, Any]:
        make_diffs = values.get("make_diffs")
        make_pr_comments = nested_get(values, "pr", "make_pr_comments")
        path_to_store_diffs = values.get("path_to_store_diffs")
        if make_diffs and (not make_pr_comments or not path_to_store_diffs):
            raise ValueError(DIFF_STORAGE_CONFIG_ERROR)

        if not make_diffs and (make_pr_comments or path_to_store_diffs):
            enabled_options = []
            if make_pr_comments:
                enabled_options.append("make_pr_comments")

            if path_to_store_diffs:
                enabled_options.append("path_to_store_diffs")

            raise ValueError(
                DIFF_NOT_ENABLED_ERROR.format(
                    enabled_options=set(enabled_options),
                    grammar="is" if len(enabled_options) == 1 else "are",
                )
            )

        return values

    @validator("path_to_store_diffs")
    def path_should_be_directory(cls, path_to_store_diffs: str) -> str:
        if path_to_store_diffs and not Path(path_to_store_diffs).is_dir():
            raise ValueError(f"{path_to_store_diffs} is not a directory.")

        return path_to_store_diffs


class Config:
    def __init__(self, config_file_path: Optional[Path] = None) -> None:
        self._config_file_path = config_file_path

    @staticmethod
    def _get_config_placed_in_default_location() -> Optional[Path]:
        default_location = Path.home() / ".config"
        for possible_name in POSSIBLE_CONFIG_FILE_NAMES:
            config_file_path = default_location / possible_name
            if config_file_path.is_file():
                return config_file_path

        return None

    def _get_config_file_path(self) -> Path:
        if self._config_file_path is not None:
            if not self._config_file_path.is_file():
                raise FileNotFoundError(
                    f"Config file {self._config_file_path} not found."
                )

            return self._config_file_path

        config_file_path = self._get_config_placed_in_default_location()
        if config_file_path is None:
            raise FileNotFoundError(CONFIG_FILE_NOT_FOUND_DEFAULT_LOCATION)

        return config_file_path

    @staticmethod
    def _get_parsed_sub_schema(
        config_items: List[Dict[str, bool]],
        schema_type: Type[Union[IssueSchema, PRSchema]],
    ) -> Union[IssueSchema, PRSchema]:
        flatten_dict = {}
        for item in config_items:
            flatten_dict.update(item)

        return schema_type.parse_obj(flatten_dict)

    @classmethod
    def _parse_config_file(cls, config_dict: dict) -> "ConfigSchema":
        if config_dict.get("issue") is not None:
            config_dict["issue"] = cls._get_parsed_sub_schema(
                config_dict["issue"], IssueSchema
            )

        if config_dict.get("pr") is not None:
            config_dict["pr"] = cls._get_parsed_sub_schema(config_dict["pr"], PRSchema)

        return ConfigSchema.parse_obj(config_dict)

    def get_config(self) -> "ConfigSchema":
        with open(self._get_config_file_path(), "r") as config_file:
            return self._parse_config_file(safe_load(config_file))
