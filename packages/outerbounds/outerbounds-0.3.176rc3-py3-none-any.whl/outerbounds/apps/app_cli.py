import json
import os
import sys
from functools import wraps
from typing import Dict, List, Any, Optional, Union
from outerbounds._vendor import click, yaml
from outerbounds.utils import metaflowconfig
from .app_config import (
    AppConfig,
    AppConfigError,
    CODE_PACKAGE_PREFIX,
    CAPSULE_DEBUG,
    AuthType,
)
from .cli_to_config import build_config_from_options
from .utils import CommaSeparatedListType, KVPairType, KVDictType
from . import experimental
from .validations import deploy_validations
from .code_package import CodePackager
from .capsule import Capsule, list_and_filter_capsules
import shlex
import time
import uuid
from datetime import datetime

LOGGER_TIMESTAMP = "magenta"
LOGGER_COLOR = "green"
LOGGER_BAD_COLOR = "red"

NativeList = list


def _logger(
    body="", system_msg=False, head="", bad=False, timestamp=True, nl=True, color=None
):
    if timestamp:
        if timestamp is True:
            dt = datetime.now()
        else:
            dt = timestamp
        tstamp = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        click.secho(tstamp + " ", fg=LOGGER_TIMESTAMP, nl=False)
    if head:
        click.secho(head, fg=LOGGER_COLOR, nl=False)
    click.secho(
        body,
        bold=system_msg,
        fg=LOGGER_BAD_COLOR if bad else color if color is not None else None,
        nl=nl,
    )


class CliState(object):
    pass


def _pre_create_debug(app_config: AppConfig, capsule: Capsule, state_dir: str):
    if CAPSULE_DEBUG:
        os.makedirs(state_dir, exist_ok=True)
        debug_path = os.path.join(state_dir, f"debug_{time.time()}.yaml")
        with open(
            debug_path,
            "w",
        ) as f:
            f.write(
                yaml.dump(
                    {
                        "app_state": app_config.dump_state(),
                        "capsule_input": capsule.create_input(),
                    },
                    default_flow_style=False,
                    indent=2,
                )
            )


def print_table(data, headers):
    """Print data in a formatted table."""
    if not data:
        return

    # Calculate column widths
    col_widths = [len(h) for h in headers]

    # Calculate actual widths based on data
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Print header
    header_row = " | ".join(
        [headers[i].ljust(col_widths[i]) for i in range(len(headers))]
    )
    click.secho("-" * len(header_row), fg="yellow")
    click.secho(header_row, fg="yellow", bold=True)
    click.secho("-" * len(header_row), fg="yellow")

    # Print data rows
    for row in data:
        formatted_row = " | ".join(
            [str(row[i]).ljust(col_widths[i]) for i in range(len(row))]
        )
        click.secho(formatted_row, fg="green", bold=True)
    click.secho("-" * len(header_row), fg="yellow")


@click.group()
def cli():
    """Outerbounds CLI tool."""
    pass


@cli.group(
    help="Commands related to Deploying/Running/Managing Apps on Outerbounds Platform."
)
@click.pass_context
def app(ctx):
    """App-related commands."""
    ctx.obj = CliState()
    ctx.obj.trace_id = str(uuid.uuid4())
    ctx.obj.app_state_dir = os.path.join(os.curdir, ".ob_apps")
    profile = os.environ.get("METAFLOW_PROFILE", "")
    config_dir = os.path.expanduser(
        os.environ.get("METAFLOW_HOME", "~/.metaflowconfig")
    )
    api_url = metaflowconfig.get_sanitized_url_from_config(
        config_dir, profile, "OBP_API_SERVER"
    )

    ctx.obj.api_url = api_url
    ctx.obj.perimeter = os.environ.get("OB_CURRENT_PERIMETER")
    os.makedirs(ctx.obj.app_state_dir, exist_ok=True)


def parse_commands(app_config: AppConfig, cli_command_input):
    # There can be two modes:
    # 1. User passes command via `--` in the CLI
    # 2. User passes the `commands` key in the config.
    base_commands = []
    if len(cli_command_input) > 0:
        # TODO: we can be a little more fancy here by allowing the user to just call
        #       `outerbounds app deploy -- foo.py` and figure out if we need to stuff python
        #       in front of the command or not. But for sake of dumb simplicity, we can just
        #       assume what ever the user called on local needs to be called remotely, we can
        #       just ask them to add the outerbounds command in front of it.
        #       So the dev ex would be :
        #       `python foo.py` -> `outerbounds app deploy -- python foo.py`
        if type(cli_command_input) == str:
            base_commands.append(cli_command_input)
        else:
            base_commands.append(shlex.join(cli_command_input))
    elif app_config.get("commands", None) is not None:
        base_commands.extend(app_config.get("commands"))
    return base_commands


def common_deploy_options(func):
    @click.option(
        "--name",
        type=str,
        help="The name of the app to deploy.",
    )
    @click.option("--port", type=int, help="Port where the app is hosted.")
    @click.option(
        "--tag",
        "tags",
        multiple=True,
        type=KVPairType,
        help="The tags of the app to deploy. Format KEY=VALUE. Example --tag foo=bar --tag x=y",
        default=None,
    )
    @click.option(
        "--image",
        type=str,
        help="The Docker image to deploy with the App",
        default=None,
    )
    @click.option(
        "--cpu",
        type=str,
        help="CPU resource request and limit",
        default=None,
    )
    @click.option(
        "--memory",
        type=str,
        help="Memory resource request and limit",
        default=None,
    )
    @click.option(
        "--gpu",
        type=str,
        help="GPU resource request and limit",
        default=None,
    )
    @click.option(
        "--disk",
        type=str,
        help="Storage resource request and limit",
        default=None,
    )
    @click.option(
        "--health-check-enabled",
        type=bool,
        help="Enable health checks",
        default=None,
    )
    @click.option(
        "--health-check-path",
        type=str,
        help="Health check path",
        default=None,
    )
    @click.option(
        "--health-check-initial-delay",
        type=int,
        help="Initial delay seconds for health check",
        default=None,
    )
    @click.option(
        "--health-check-period",
        type=int,
        help="Period seconds for health check",
        default=None,
    )
    @click.option(
        "--compute-pools",
        type=CommaSeparatedListType,
        help="The compute pools to deploy the app to. Example: --compute-pools default,large",
        default=None,
    )
    @click.option(
        "--auth-type",
        type=click.Choice(AuthType.enums()),
        help="The type of authentication to use for the app.",
        default=None,
    )
    @click.option(
        "--public-access/--private-access",
        "auth_public",
        type=bool,
        help="Whether the app is public or not.",
        default=None,
    )
    @click.option(
        "--no-deps",
        is_flag=True,
        help="Do not any dependencies. Directly used the image provided",
        default=False,
    )
    @click.option(
        "--min-replicas",
        type=int,
        help="Minimum number of replicas to deploy",
        default=None,
    )
    @click.option(
        "--max-replicas",
        type=int,
        help="Maximum number of replicas to deploy",
        default=None,
    )
    @click.option(
        "--description",
        type=str,
        help="The description of the app to deploy.",
        default=None,
    )
    @click.option(
        "--app-type",
        type=str,
        help="The type of app to deploy.",
        default=None,
    )
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def common_run_options(func):
    """Common options for running and deploying apps."""

    @click.option(
        "--config-file",
        type=str,
        help="The config file to use for the App (YAML or JSON)",
        default=None,
    )
    @click.option(
        "--secret",
        "secrets",
        multiple=True,
        type=str,
        help="Secrets to deploy with the App",
        default=None,
    )
    @click.option(
        "--env",
        "envs",
        multiple=True,
        type=KVPairType,
        help="Environment variables to deploy with the App. Use format KEY=VALUE",
        default=None,
    )
    @click.option(
        "--package-src-path",
        type=str,
        help="The path to the source code to deploy with the App.",
        default=None,
    )
    @click.option(
        "--package-suffixes",
        type=CommaSeparatedListType,
        help="The suffixes of the source code to deploy with the App.",
        default=None,
    )
    @click.option(
        "--dep-from-requirements",
        type=str,
        help="Path to requirements.txt file for dependencies",
        default=None,
    )
    @click.option(
        "--dep-from-pyproject",
        type=str,
        help="Path to pyproject.toml file for dependencies",
        default=None,
    )
    # TODO: [FIX ME]: Get better CLI abstraction for pypi/conda dependencies
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def _package_necessary_things(app_config: AppConfig, logger):
    # Packaging has a few things to be thought through:
    #   1. if `entrypoint_path` exists then should we package the directory
    #      where the entrypoint lives. For example : if the user calls
    #      `outerbounds app deploy foo/bar.py`  should we package `foo` dir
    #      or should we package the cwd from which foo/bar.py is being called.
    #   2. if the src path is used with the config file then how should we view
    #      that path ?
    #   3. It becomes interesting when users call the deployment with config files
    #      where there is a `src_path` and then is the src_path relative to the config file
    #      or is it relative to where the caller command is sitting. Ideally it should work
    #      like Kustomizations where its relative to where the yaml file sits for simplicity
    #      of understanding relationships between config files. Ideally users can pass the src_path
    #      from the command line and that will aliviate any need to package any other directories for
    #

    package_dir = app_config.get_state("packaging_directory")
    if package_dir is None:
        app_config.set_state("code_package_url", None)
        app_config.set_state("code_package_key", None)
        return
    from metaflow.metaflow_config import DEFAULT_DATASTORE

    package = app_config.get_state("package") or {}
    suffixes = package.get("suffixes", None)

    packager = CodePackager(
        datastore_type=DEFAULT_DATASTORE, code_package_prefix=CODE_PACKAGE_PREFIX
    )
    package_url, package_key = packager.store(
        paths_to_include=[package_dir], file_suffixes=suffixes
    )
    app_config.set_state("code_package_url", package_url)
    app_config.set_state("code_package_key", package_key)
    logger("💾 Code Package Saved to : %s" % app_config.get_state("code_package_url"))


@app.command(help="Deploy an app to the Outerbounds Platform.")
@common_deploy_options
@common_run_options
@experimental.wrapping_cli_options
@click.pass_context
@click.argument("command", nargs=-1, type=click.UNPROCESSED, required=False)
def deploy(ctx, command, **options):
    """Deploy an app to the Outerbounds Platform."""
    from functools import partial

    if not ctx.obj.perimeter:
        raise AppConfigError("OB_CURRENT_PERIMETER is not set")

    logger = partial(_logger, timestamp=True)
    try:
        # Create configuration
        if options["config_file"]:
            # Load from file
            app_config = AppConfig.from_file(options["config_file"])

            # Update with any CLI options using the unified method
            app_config.update_from_cli_options(options)
        else:
            # Create from CLI options
            config_dict = build_config_from_options(options)
            app_config = AppConfig(config_dict)

        # Validate the configuration
        app_config.validate()
        logger(
            f"🚀 Deploying {app_config.get('name')} to the Outerbounds platform...",
            color=LOGGER_COLOR,
            system_msg=True,
        )

        packaging_directory = None
        package_src_path = app_config.get("package", {}).get("src_path", None)
        if package_src_path:
            if os.path.isfile(package_src_path):
                raise AppConfigError("src_path must be a directory, not a file")
            elif os.path.isdir(package_src_path):
                packaging_directory = os.path.abspath(package_src_path)
            else:
                raise AppConfigError(f"src_path '{package_src_path}' does not exist")
        else:
            # If src_path is None then we assume then we can assume for the moment
            # that we can package the current working directory.
            packaging_directory = os.getcwd()

        app_config.set_state("packaging_directory", packaging_directory)
        logger(
            "📦 Packaging Directory : %s" % app_config.get_state("packaging_directory"),
        )
        # TODO: Construct the command needed to run the app
        #       If we are constructing the directory with the src_path
        #       then we need to add the command from the option otherwise
        #       we use the command from the entrypoint path and whatever follows `--`
        #       is the command to run.

        # Set some defaults for the deploy command
        app_config.set_deploy_defaults(packaging_directory)

        if options.get("no_deps") == True:
            # Setting this in the state will make it skip the fast-bakery step
            # of building an image.
            app_config.set_state("skip_dependencies", True)
        else:
            # Check if the user has set the dependencies in the app config
            dependencies = app_config.get("dependencies", {})
            if len(dependencies) == 0:
                # The user has not set any dependencies, so we can sniff the packaging directory
                # for a dependencies file.
                requirements_file = os.path.join(
                    packaging_directory, "requirements.txt"
                )
                pyproject_toml = os.path.join(packaging_directory, "pyproject.toml")
                if os.path.exists(pyproject_toml):
                    app_config.set_state(
                        "dependencies", {"from_pyproject_toml": pyproject_toml}
                    )
                    logger(
                        "📦 Using dependencies from pyproject.toml: %s" % pyproject_toml
                    )
                elif os.path.exists(requirements_file):
                    app_config.set_state(
                        "dependencies", {"from_requirements_file": requirements_file}
                    )
                    logger(
                        "📦 Using dependencies from requirements.txt: %s"
                        % requirements_file
                    )

        # Print the configuration
        # 1. validate that the secrets for the app exist
        # 2. TODO: validate that the compute pool specified in the app exists.
        # 3. Building Docker image if necessary (based on parameters)
        #   - We will bake images with fastbakery and pass it to the deploy command
        # TODO: validation logic can be wrapped in try catch so that we can provide
        #       better error messages.
        cache_dir = os.path.join(
            ctx.obj.app_state_dir, app_config.get("name", "default")
        )
        deploy_validations(
            app_config,
            cache_dir=cache_dir,
            logger=logger,
        )

        base_commands = parse_commands(app_config, command)

        app_config.set_state("commands", base_commands)

        # TODO: Handle the case where packaging_directory is None
        # This would involve:
        # 1. Packaging the code:
        #   - We need to package the code and throw the tarball to some object store
        _package_necessary_things(app_config, logger)

        app_config.set_state("perimeter", ctx.obj.perimeter)

        # 2. Convert to the IR that the backend accepts
        capsule = Capsule(app_config, ctx.obj.api_url, debug_dir=cache_dir)

        _pre_create_debug(app_config, capsule, cache_dir)
        # 3. Throw the job into the platform and report deployment status
        logger(
            f"🚀 Deploying {capsule.capsule_type.lower()} to the platform...",
            color=LOGGER_COLOR,
            system_msg=True,
        )
        capsule.create()
        capsule.wait_for_terminal_state(logger=logger)
        logger(
            f"💊 {capsule.capsule_type} {app_config.config['name']} ({capsule.identifier}) deployed successfully! You can access it at {capsule.status.out_of_cluster_url}",
            color=LOGGER_COLOR,
            system_msg=True,
        )

    except AppConfigError as e:
        click.echo(f"Error in app configuration: {e}", err=True)
        raise e
    except Exception as e:
        click.echo(f"Error deploying app: {e}", err=True)
        raise e


def _parse_capsule_table(filtered_capsules):
    headers = ["Name", "ID", "Ready", "App Type", "Port", "Tags", "URL"]
    table_data = []

    for capsule in filtered_capsules:
        spec = capsule.get("spec", {})
        status = capsule.get("status", {}) or {}
        cap_id = capsule.get("id")
        display_name = spec.get("displayName", "")
        ready = str(status.get("readyToServeTraffic", False))
        auth_type = spec.get("authConfig", {}).get("authType", "")
        port = str(spec.get("port", ""))
        tags_str = ", ".join(
            [f"{tag['key']}={tag['value']}" for tag in spec.get("tags", [])]
        )
        access_info = status.get("accessInfo", {}) or {}
        url = access_info.get("outOfClusterURL", None)

        table_data.append(
            [
                display_name,
                cap_id,
                ready,
                auth_type,
                port,
                tags_str,
                f"https://{url}" if url else "URL not available",
            ]
        )
    return headers, table_data


@app.command(help="List apps in the Outerbounds Platform.")
@click.option("--project", type=str, help="Filter apps by project")
@click.option("--branch", type=str, help="Filter apps by branch")
@click.option("--name", type=str, help="Filter apps by name")
@click.option(
    "--tag",
    "tags",
    type=KVDictType,
    help="Filter apps by tag. Format KEY=VALUE. Example --tag foo=bar --tag x=y. If multiple tags are provided, the app must match all of them.",
    multiple=True,
)
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    help="Format the output",
    default="text",
)
@click.option(
    "--auth-type", type=click.Choice(AuthType.enums()), help="Filter apps by Auth type"
)
@click.pass_context
def list(ctx, project, branch, name, tags, format, auth_type):
    """List apps in the Outerbounds Platform."""

    filtered_capsules = list_and_filter_capsules(
        ctx.obj.api_url, ctx.obj.perimeter, project, branch, name, tags, auth_type, None
    )
    if format == "json":
        click.echo(json.dumps(filtered_capsules, indent=4))
    else:
        headers, table_data = _parse_capsule_table(filtered_capsules)
        print_table(table_data, headers)


@app.command(help="Delete an app/apps from the Outerbounds Platform.")
@click.option("--name", type=str, help="Filter app to delete by name")
@click.option("--id", "cap_id", type=str, help="Filter app to delete by id")
@click.option("--project", type=str, help="Filter apps to delete by project")
@click.option("--branch", type=str, help="Filter apps to delete by branch")
@click.option(
    "--tag",
    "tags",
    multiple=True,
    type=KVPairType,
    help="Filter apps to delete by tag. Format KEY=VALUE. Example --tag foo=bar --tag x=y. If multiple tags are provided, the app must match all of them.",
)
@click.pass_context
def delete(ctx, name, cap_id, project, branch, tags):

    """Delete an app/apps from the Outerbounds Platform."""
    # Atleast one of the args need to be provided
    if not any(
        [
            name is not None,
            cap_id is not None,
            project is not None,
            branch is not None,
            len(tags) != 0,
        ]
    ):
        raise AppConfigError(
            "Atleast one of the options need to be provided. You can use --name, --id, --project, --branch, --tag"
        )

    filtered_capsules = list_and_filter_capsules(
        ctx.obj.api_url, ctx.obj.perimeter, project, branch, name, tags, None, cap_id
    )

    headers, table_data = _parse_capsule_table(filtered_capsules)
    click.secho("The following apps will be deleted:", fg="red", bold=True)
    print_table(table_data, headers)

    # Confirm the deletion
    confirm = click.prompt(
        click.style(
            "💊 Are you sure you want to delete these apps?", fg="red", bold=True
        ),
        default="no",
        type=click.Choice(["yes", "no"]),
    )
    if confirm == "no":
        exit(1)

    def item_show_func(x):
        if not x:
            return None
        name = x.get("spec", {}).get("displayName", "")
        id = x.get("id", "")
        return click.style("💊 deleting %s [%s]" % (name, id), fg="red", bold=True)

    with click.progressbar(
        filtered_capsules,
        label=click.style("💊 Deleting apps...", fg="red", bold=True),
        fill_char=click.style("█", fg="red", bold=True),
        empty_char=click.style("░", fg="red", bold=True),
        item_show_func=item_show_func,
    ) as bar:
        for capsule in bar:
            Capsule.delete(capsule.get("id"), ctx.obj.api_url, ctx.obj.perimeter)


@app.command(help="Run an app locally (for testing).")
@common_run_options
@click.pass_context
def run(ctx, **options):
    """Run an app locally for testing."""
    try:
        # Create configuration
        if options["config_file"]:
            # Load from file
            app_config = AppConfig.from_file(options["config_file"])

            # Update with any CLI options using the unified method
            app_config.update_from_cli_options(options)
        else:
            # Create from CLI options
            config_dict = build_config_from_options(options)
            app_config = AppConfig(config_dict)

        # Validate the configuration
        app_config.validate()

        # Print the configuration
        click.echo("Running App with configuration:")
        click.echo(app_config.to_yaml())

        # TODO: Implement local run logic
        # This would involve:
        # 1. Setting up the environment
        # 2. Running the app locally
        # 3. Reporting status

        click.echo(f"App '{app_config.config['name']}' running locally!")

    except AppConfigError as e:
        click.echo(f"Error in app configuration: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        click.echo(f"Error running app: {e}", err=True)
        ctx.exit(1)


# if __name__ == "__main__":
#     cli()
