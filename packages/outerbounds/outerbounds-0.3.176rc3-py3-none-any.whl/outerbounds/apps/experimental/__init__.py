from functools import wraps
from outerbounds._vendor import click
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app_config import AppConfig

DEFAULT_BRANCH = "test"


def wrapping_cli_options(func):
    @click.option(
        "--project",
        type=str,
        help="The flow project the app/endpoint belongs to",
        default=None,
    )
    @click.option(
        "--branch",
        type=str,
        help="The branch the app/endpoint belongs to",
        default=None,
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def build_config_from_options(options):
    """Build an app configuration from CLI options."""
    keys = [
        "project",
        "branch",
    ]
    config = {}
    for key in keys:
        if options.get(key):
            config[key] = options.get(key)

    return config


# Account for project / branch and the capsule input.
def capsule_input_overrides(app_config: "AppConfig", capsule_input: dict):
    project = app_config.get_state("project", None)
    # Update the project/branch related configurations.
    if project is not None:
        branch = app_config.get_state("branch", DEFAULT_BRANCH)
        capsule_input["tags"].extend(
            [dict(key="project", value=project), dict(key="branch", value=branch)]
        )

    model_asset_conf = app_config.get_state("models", None)
    data_asset_conf = app_config.get_state("data", None)
    code_info = _code_info(app_config)
    # todo:fix me
    _objects_key = "associatedObjects"
    if model_asset_conf or data_asset_conf or code_info:
        capsule_input[_objects_key] = {}

        if model_asset_conf:
            capsule_input[_objects_key]["models"] = [
                {"assetId": x["asset_id"], "assetInstanceId": x["asset_instance_id"]}
                for x in model_asset_conf
            ]
        if data_asset_conf:
            capsule_input[_objects_key]["data"] = [
                {"assetId": x["asset_id"], "assetInstanceId": x["asset_instance_id"]}
                for x in data_asset_conf
            ]
        if code_info:
            capsule_input[_objects_key]["code"] = code_info

    return capsule_input


def _code_info(app_config: "AppConfig"):
    from metaflow.metaflow_git import get_repository_info, _call_git

    repo_info = get_repository_info(app_config.get_state("packaging_directory", None))
    if len(repo_info) == 0:
        return None

    git_log_info, returncode, failed = _call_git(
        ["log", "-1", "--pretty=%B"],
        path=app_config.get_state("packaging_directory", None),
    )
    _url = (
        repo_info["repo_url"]
        if not repo_info["repo_url"].endswith(".git")
        else repo_info["repo_url"].rstrip(".git")
    )
    _code_info = {
        "commitId": repo_info["commit_sha"],
        "commitLink": os.path.join(_url, "commit", repo_info["commit_sha"]),
    }
    if not failed and returncode == 0:
        _code_info["commitMessage"] = git_log_info.strip()

    return _code_info
