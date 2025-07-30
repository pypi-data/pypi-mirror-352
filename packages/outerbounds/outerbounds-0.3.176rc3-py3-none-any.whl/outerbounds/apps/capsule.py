import json
import os
import pathlib
import requests
import time
import shlex
from typing import Optional
from .utils import TODOException, safe_requests_wrapper
from .app_config import AppConfig, CAPSULE_DEBUG, AuthType
from . import experimental


class CapsuleStateMachine:
    """
    Since capsules are a kinda newer concept, we will treat the state transitions based on the conditions and the
    availability of certain fields in the status dictionary.
    """

    CONDITIONS = ["Ready", "DeploymentReplicasAvailable", "IngressObjectReady"]

    def __init__(self, capsule_id: str):
        self._capsule_id = capsule_id
        self._status_trail = []

    def is_completely_new_capsule(self):
        # This is a heuristic. Not a fully tested.
        # If we create a completely new capsule then the status
        # field might be a completely empty dictionary.
        assert (
            len(self._status_trail) > 0
        ), "status_trail cannot be none to infer if its a new capsule"
        return self._empty_status(self._status_trail[0].get("status"))

    def get_status_trail(self):
        return self._status_trail

    @staticmethod
    def _empty_status(status):
        if json.dumps(status) == "{}":
            return True
        return False

    @staticmethod
    def _parse_conditions(conditions):
        curr_conditons = {}
        for condition in conditions:
            curr_conditons[condition["type"]] = condition["status"]
        return curr_conditons

    def add_status(self, status: dict):
        assert type(status) == dict, "TODO: Make this check somewhere else"
        self._status_trail.append({"timestamp": time.time(), "status": status})

    @staticmethod
    def _condition_change_emoji(previous_condition_status, current_condition_status):
        if previous_condition_status == current_condition_status:
            if previous_condition_status == "True":
                return "✅"
            else:
                return "❌"
        if previous_condition_status == "True" and current_condition_status == "False":
            return "🔴 --> 🟢"
        if previous_condition_status == "False" and current_condition_status == "True":
            return "🚀"
        return "🟡"

    @property
    def current_status(self):
        return self._status_trail[-1].get("status")

    @property
    def out_of_cluster_url(self):
        access_info = self.current_status.get("accessInfo", {}) or {}
        url = access_info.get("outOfClusterURL", None)
        if url is not None:
            return f"https://{url}"
        return None

    @property
    def in_cluster_url(self):
        access_info = self.current_status.get("accessInfo", {}) or {}
        url = access_info.get("inClusterURL", None)
        if url is not None:
            return f"https://{url}"
        return None

    @property
    def ready_to_serve_traffic(self):
        if self.current_status.get("readyToServeTraffic", False):
            return any(
                i is not None for i in [self.out_of_cluster_url, self.in_cluster_url]
            )
        return False

    @property
    def available_replicas(self):
        return self.current_status.get("availableReplicas", 0)

    def report_current_status(self, logger):
        if len(self._status_trail) < 2:
            return
        previous_status, current_status = self._status_trail[-2].get(
            "status"
        ), self._status_trail[-1].get("status")
        if self._empty_status(current_status):
            return

        if self._empty_status(previous_status):
            logger("💊 %s Deployment has started ... 🚀" % self._capsule_id)
            return

    def check_for_debug(self, state_dir: str):
        if CAPSULE_DEBUG:
            debug_path = os.path.join(
                state_dir, f"debug_capsule_{self._capsule_id}.json"
            )
            with open(debug_path, "w") as f:
                json.dump(self._status_trail, f, indent=4)


class CapsuleInput:
    @classmethod
    def construct_exec_command(cls, commands: list[str]):
        commands = ["set -eEuo pipefail"] + commands
        command_string = "\n".join(commands)
        # First constuct a base64 encoded string of the quoted command
        # One of the reasons we don't directly pass the command string to the backend with a `\n` join
        # is because the backend controller doesnt play nice when the command can be a multi-line string.
        # So we encode it to a base64 string and then decode it back to a command string at runtime to provide to
        # `bash -c`. The ideal thing to have done is to run "bash -c {shlex.quote(command_string)}" and call it a day
        # but the backend controller yields the following error:
        # `error parsing template: error converting YAML to JSON: yaml: line 111: mapping values are not allowed in this context`
        # So we go to great length to ensure the command is provided in base64 to avoid any issues with the backend controller.
        import base64

        encoded_command = base64.b64encode(command_string.encode()).decode()
        decode_cmd = f"echo {encoded_command} | base64 -d > ./_ob_app_run.sh"
        return (
            f"bash -c '{decode_cmd} && cat ./_ob_app_run.sh && bash ./_ob_app_run.sh'"
        )

    @classmethod
    def _marshal_environment_variables(cls, app_config: AppConfig):
        envs = app_config.get_state("environment", {}).copy()
        _return = []
        for k, v in envs.items():
            _v = v
            if isinstance(v, dict):
                _v = json.dumps(v)
            elif isinstance(v, list):
                _v = json.dumps(v)
            else:
                _v = str(v)
            _return.append(
                {
                    "name": k,
                    "value": _v,
                }
            )
        return _return

    @classmethod
    def from_app_config(self, app_config: AppConfig):
        gpu_resource = app_config.get_state("resources").get("gpu")
        resources = {}
        shared_memory = app_config.get_state("resources").get("shared_memory")
        if gpu_resource:
            resources["gpu"] = gpu_resource
        if shared_memory:
            resources["sharedMemory"] = shared_memory

        _scheduling_config = {}
        if app_config.get_state("compute_pools", None):
            _scheduling_config["computePools"] = [
                {"name": x} for x in app_config.get_state("compute_pools")
            ]
        _description = app_config.get_state("description")
        _app_type = app_config.get_state("app_type")
        _final_info = {}
        if _description:
            _final_info["description"] = _description
        if _app_type:
            _final_info["endpointType"] = _app_type
        return {
            "perimeter": app_config.get_state("perimeter"),
            **_final_info,
            "codePackagePath": app_config.get_state("code_package_url"),
            "image": app_config.get_state("image"),
            "resourceIntegrations": [
                {"name": x} for x in app_config.get_state("secrets", [])
            ],
            "resourceConfig": {
                "cpu": str(app_config.get_state("resources").get("cpu")),
                "memory": str(app_config.get_state("resources").get("memory")),
                "ephemeralStorage": str(app_config.get_state("resources").get("disk")),
                **resources,
            },
            "autoscalingConfig": {
                "minReplicas": app_config.get_state("replicas", {}).get("min", 1),
                "maxReplicas": app_config.get_state("replicas", {}).get("max", 1),
            },
            **_scheduling_config,
            "containerStartupConfig": {
                "entrypoint": self.construct_exec_command(
                    app_config.get_state("commands")
                )
            },
            "environmentVariables": self._marshal_environment_variables(app_config),
            # "assets": [{"name": "startup-script.sh"}],
            "authConfig": {
                "authType": app_config.get_state("auth").get("type"),
                "publicToDeployment": app_config.get_state("auth").get("public"),
            },
            "tags": [
                dict(key=k, value=v)
                for tag in app_config.get_state("tags", [])
                for k, v in tag.items()
            ],
            "port": app_config.get_state("port"),
            "displayName": app_config.get_state("name"),
        }


def create_capsule(capsule_input: dict, api_url: str, request_headers: dict):
    _data = json.dumps(capsule_input)
    response = safe_requests_wrapper(
        requests.post,
        api_url,
        data=_data,
        headers=request_headers,
        conn_error_retries=2,
        retryable_status_codes=[409],  # todo : verify me
    )

    if response.status_code >= 400:
        raise TODOException(
            f"Failed to create capsule: {response.status_code} {response.text}"
        )
    return response.json()


def list_capsules(api_url: str, request_headers: dict):
    response = safe_requests_wrapper(
        requests.get,
        api_url,
        headers=request_headers,
        retryable_status_codes=[409],  # todo : verify me
        conn_error_retries=3,
    )
    if response.status_code >= 400:
        raise TODOException(
            f"Failed to list capsules: {response.status_code} {response.text}"
        )
    return response.json()


def get_capsule(capsule_id: str, api_url: str, request_headers: dict):
    # params = {"instance_id": capsule_id}
    url = os.path.join(api_url, capsule_id)
    response = safe_requests_wrapper(
        requests.get,
        url,
        headers=request_headers,
        retryable_status_codes=[409, 404],  # todo : verify me
        conn_error_retries=3,
    )
    if response.status_code >= 400:
        raise TODOException(
            f"Failed to get capsule: {response.status_code} {response.text}"
        )
    return response.json()


def delete_capsule(capsule_id: str, api_url: str, request_headers: dict):
    _url = os.path.join(api_url, capsule_id)
    response = safe_requests_wrapper(
        requests.delete,
        _url,
        headers=request_headers,
        retryable_status_codes=[409],  # todo : verify me
    )
    if response.status_code >= 400:
        raise TODOException(
            f"Failed to delete capsule: {response.status_code} {response.text}"
        )

    if response.status_code == 200:
        return True
    return False


def list_capsules(api_url: str, request_headers: dict):
    response = safe_requests_wrapper(
        requests.get,
        api_url,
        headers=request_headers,
    )
    if response.status_code >= 400:
        raise TODOException(
            f"Failed to list capsules: {response.status_code} {response.text}"
        )
    return response.json()


def list_and_filter_capsules(
    api_url, perimeter, project, branch, name, tags, auth_type, capsule_id
):
    capsules = Capsule.list(api_url, perimeter)

    def _tags_match(tags, key, value):
        for t in tags:
            if t["key"] == key and t["value"] == value:
                return True
        return False

    def _all_tags_match(tags, tags_to_match):
        for t in tags_to_match:
            if _tags_match(tags, t["key"], t["value"]):
                return True
        return False

    def _filter_capsules(capsules, project, branch, name, tags, auth_type, capsule_id):
        _filtered_capsules = []
        for capsule in capsules:
            set_tags = capsule.get("spec", {}).get("tags", [])
            display_name = capsule.get("spec", {}).get("displayName", None)
            set_id = capsule.get("id", None)
            set_auth_type = (
                capsule.get("spec", {}).get("authConfig", {}).get("authType", None)
            )

            if auth_type and set_auth_type != auth_type:
                continue
            if project and not _tags_match(set_tags, "project", project):
                continue
            if branch and not _tags_match(set_tags, "branch", branch):
                continue
            if name and display_name != name:
                continue
            if tags and not _all_tags_match(set_tags, tags):
                continue
            if capsule_id and set_id != capsule_id:
                continue

            _filtered_capsules.append(capsule)
        return _filtered_capsules

    return _filter_capsules(
        capsules, project, branch, name, tags, auth_type, capsule_id
    )


class Capsule:

    status: CapsuleStateMachine

    identifier = None

    @classmethod
    def list(cls, base_url: str, perimeter: str):
        base_url = cls._create_base_url(base_url, perimeter)
        from metaflow.metaflow_config import SERVICE_HEADERS

        request_headers = {
            **{"Content-Type": "application/json", "Connection": "keep-alive"},
            **(SERVICE_HEADERS or {}),
        }
        _capsules = list_capsules(base_url, request_headers)
        if "capsules" not in _capsules:
            raise TODOException(f"Failed to list capsules")
        return _capsules.get("capsules", []) or []

    @classmethod
    def delete(cls, identifier: str, base_url: str, perimeter: str):
        base_url = cls._create_base_url(base_url, perimeter)
        from metaflow.metaflow_config import SERVICE_HEADERS

        request_headers = {
            **{"Content-Type": "application/json", "Connection": "keep-alive"},
            **(SERVICE_HEADERS or {}),
        }
        return delete_capsule(identifier, base_url, request_headers)

    @classmethod
    def _create_base_url(
        cls,
        base_url: str,
        perimeter: str,
    ):
        return os.path.join(
            base_url,
            "v1",
            "perimeters",
            perimeter,
            "capsules",
        )

    # TODO: Current default timeout is very large of 5 minutes. Ideally we should have finished the deployed in less than 1 minutes.
    def __init__(
        self,
        app_config: AppConfig,
        base_url: str,
        create_timeout: int = 60 * 5,
        debug_dir: Optional[str] = None,
    ):
        self._app_config = app_config
        self._base_url = self._create_base_url(
            base_url,
            app_config.get_state("perimeter"),
        )
        self._create_timeout = create_timeout
        self._debug_dir = debug_dir
        from metaflow.metaflow_config import SERVICE_HEADERS

        self._request_headers = {
            **{"Content-Type": "application/json", "Connection": "keep-alive"},
            **(SERVICE_HEADERS or {}),
        }

    @property
    def capsule_type(self):
        auth_type = self._app_config.get_state("auth", {}).get("type", AuthType.default)
        if auth_type == AuthType.BROWSER:
            return "App"
        elif auth_type == AuthType.API:
            return "Endpoint"
        else:
            raise TODOException(f"Unknown auth type: {auth_type}")

    @property
    def name(self):
        return self._app_config.get_state("name")

    def create_input(self):
        return experimental.capsule_input_overrides(
            self._app_config, CapsuleInput.from_app_config(self._app_config)
        )

    def create(self):
        capsule_response = create_capsule(
            self.create_input(), self._base_url, self._request_headers
        )
        self.identifier = capsule_response.get("id")
        return self.identifier

    def get(self):
        # TODO: [FIX ME]: This need to work in the reverse lookup way too.
        return get_capsule(self.identifier, self._base_url, self._request_headers)

    def wait_for_terminal_state(self, logger=print):
        state_machine = CapsuleStateMachine(self.identifier)
        logger(
            "💊 Waiting for %s %s to be ready to serve traffic"
            % (self.capsule_type.lower(), self.identifier)
        )
        self.status = state_machine
        for i in range(self._create_timeout):
            capsule_response = self.get()
            state_machine.add_status(capsule_response.get("status", {}))
            time.sleep(1)
            state_machine.report_current_status(logger)
            if state_machine.ready_to_serve_traffic:
                logger(
                    "💊 %s %s is ready to serve traffic on the URL: %s"
                    % (
                        self.capsule_type,
                        self.identifier,
                        state_machine.out_of_cluster_url,
                    ),
                )
                break
            if self._debug_dir:
                state_machine.check_for_debug(self._debug_dir)

        if not self.status.ready_to_serve_traffic:
            raise TODOException(
                f"Capsule {self.identifier} failed to be ready to serve traffic"
            )
        return capsule_response
