import random
import time
import sys
import json
import requests
from outerbounds._vendor import click
from .app_config import CAPSULE_DEBUG


class MaximumRetriesExceeded(Exception):
    def __init__(self, url, method, status_code, text):
        self.url = url
        self.method = method
        self.status_code = status_code
        self.text = text

    def __str__(self):
        return f"Maximum retries exceeded for {self.url}[{self.method}] {self.status_code} {self.text}"


class KeyValueDictPair(click.ParamType):
    name = "KV-DICT-PAIR"

    def convert(self, value, param, ctx):
        # Parse a string of the form KEY=VALUE into a dict {KEY: VALUE}
        if len(value.split("=", 1)) != 2:
            self.fail(
                f"Invalid format for {value}. Expected format: KEY=VALUE", param, ctx
            )

        key, _value = value.split("=", 1)
        try:
            return {"key": key, "value": json.loads(_value)}
        except json.JSONDecodeError:
            return {"key": key, "value": _value}
        except Exception as e:
            self.fail(f"Invalid value for {value}. Error: {e}", param, ctx)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "KV-PAIR"


class KeyValuePair(click.ParamType):
    name = "KV-PAIR"

    def convert(self, value, param, ctx):
        # Parse a string of the form KEY=VALUE into a dict {KEY: VALUE}
        if len(value.split("=", 1)) != 2:
            self.fail(
                f"Invalid format for {value}. Expected format: KEY=VALUE", param, ctx
            )

        key, _value = value.split("=", 1)
        try:
            return {key: json.loads(_value)}
        except json.JSONDecodeError:
            return {key: _value}
        except Exception as e:
            self.fail(f"Invalid value for {value}. Error: {e}", param, ctx)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "KV-PAIR"


class MountMetaflowArtifact(click.ParamType):
    name = "MOUNT-METAFLOW-ARTIFACT"

    def convert(self, value, param, ctx):
        """
        Convert a string like "flow=MyFlow,artifact=my_model,path=/tmp/abc" or
        "pathspec=MyFlow/123/foo/345/my_model,path=/tmp/abc" to a dict.
        """
        artifact_dict = {}
        parts = value.split(",")

        for part in parts:
            if "=" not in part:
                self.fail(
                    f"Invalid format in part '{part}'. Expected 'key=value'", param, ctx
                )

            key, val = part.split("=", 1)
            artifact_dict[key.strip()] = val.strip()

        # Validate required fields
        if "pathspec" in artifact_dict:
            if "path" not in artifact_dict:
                self.fail(
                    "When using 'pathspec', you must also specify 'path'", param, ctx
                )

            # Return as pathspec format
            return {
                "pathspec": artifact_dict["pathspec"],
                "path": artifact_dict["path"],
            }
        elif (
            "flow" in artifact_dict
            and "artifact" in artifact_dict
            and "path" in artifact_dict
        ):
            # Return as flow/artifact format
            result = {
                "flow": artifact_dict["flow"],
                "artifact": artifact_dict["artifact"],
                "path": artifact_dict["path"],
            }

            # Add optional namespace if provided
            if "namespace" in artifact_dict:
                result["namespace"] = artifact_dict["namespace"]

            return result
        else:
            self.fail(
                "Invalid format. Must be either 'flow=X,artifact=Y,path=Z' or 'pathspec=X,path=Z'",
                param,
                ctx,
            )

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "MOUNT-METAFLOW-ARTIFACT"


class MountSecret(click.ParamType):
    name = "MOUNT-SECRET"

    def convert(self, value, param, ctx):
        """
        Convert a string like "id=my_secret,path=/tmp/secret" to a dict.
        """
        secret_dict = {}
        parts = value.split(",")

        for part in parts:
            if "=" not in part:
                self.fail(
                    f"Invalid format in part '{part}'. Expected 'key=value'", param, ctx
                )

            key, val = part.split("=", 1)
            secret_dict[key.strip()] = val.strip()

        # Validate required fields
        if "id" in secret_dict and "path" in secret_dict:
            return {"id": secret_dict["id"], "path": secret_dict["path"]}
        else:
            self.fail("Invalid format. Must be 'key=X,path=Y'", param, ctx)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "MOUNT-SECRET"


class CommaSeparatedList(click.ParamType):
    name = "COMMA-SEPARATED-LIST"

    def convert(self, value, param, ctx):
        return value.split(",")

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "COMMA-SEPARATED-LIST"


KVPairType = KeyValuePair()
MetaflowArtifactType = MountMetaflowArtifact()
SecretMountType = MountSecret()
CommaSeparatedListType = CommaSeparatedList()
KVDictType = KeyValueDictPair()


class TODOException(Exception):
    pass


requests_funcs = [
    requests.get,
    requests.post,
    requests.put,
    requests.delete,
    requests.patch,
    requests.head,
    requests.options,
]


def safe_requests_wrapper(
    requests_module_fn,
    *args,
    conn_error_retries=2,
    retryable_status_codes=[409],
    **kwargs,
):
    """
    There are two categories of errors that we need to handle when dealing with any API server.
    1. HTTP errors. These are are errors that are returned from the API server.
        - How to handle retries for this case will be application specific.
    2. Errors when the API server may not be reachable (DNS resolution / network issues)
        - In this scenario, we know that something external to the API server is going wrong causing the issue.
        - Failing pre-maturely in the case might not be the best course of action since critical user jobs might crash on intermittent issues.
        - So in this case, we can just planely retry the request.

    This function handles the second case. It's a simple wrapper to handle the retry logic for connection errors.
    If this function is provided a `conn_error_retries` of 5, then the last retry will have waited 32 seconds.
    Generally this is a safe enough number of retries after which we can assume that something is really broken. Until then,
    there can be intermittent issues that would resolve themselves if we retry gracefully.
    """
    if requests_module_fn not in requests_funcs:
        raise TODOException(
            f"safe_requests_wrapper doesn't support {requests_module_fn.__name__}. You can only use the following functions: {requests_funcs}"
        )

    _num_retries = 0
    noise = random.uniform(-0.5, 0.5)
    response = None
    while _num_retries < conn_error_retries:
        try:
            response = requests_module_fn(*args, **kwargs)
            if response.status_code not in retryable_status_codes:
                return response
            if CAPSULE_DEBUG:
                print(
                    f"[outerbounds-debug] safe_requests_wrapper: {response.url}[{requests_module_fn.__name__}] {response.status_code} {response.text}",
                    file=sys.stderr,
                )
            _num_retries += 1
            time.sleep((2 ** (_num_retries + 1)) + noise)
        except requests.exceptions.ConnectionError:
            if _num_retries <= conn_error_retries - 1:
                # Exponential backoff with 2^(_num_retries+1) seconds
                time.sleep((2 ** (_num_retries + 1)) + noise)
                _num_retries += 1
            else:
                raise
    raise MaximumRetriesExceeded(
        response.url,
        requests_module_fn.__name__,
        response.status_code,
        response.text,
    )
