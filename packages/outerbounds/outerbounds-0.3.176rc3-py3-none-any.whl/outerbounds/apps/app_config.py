import json
import os
from outerbounds._vendor import yaml
from typing import Dict, Any
from .cli_to_config import build_config_from_options

CODE_PACKAGE_PREFIX = "mf.obp-apps"

CAPSULE_DEBUG = os.environ.get("OUTERBOUNDS_CAPSULE_DEBUG", False)


class classproperty(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class AppConfigError(Exception):
    """Exception raised when app configuration is invalid."""

    pass


class AuthType:
    BROWSER = "Browser"
    API = "API"

    @classmethod
    def enums(cls):
        return [cls.BROWSER, cls.API]

    @classproperty
    def default(cls):
        return cls.BROWSER


class AppConfig:
    """Class representing an Outerbounds App configuration."""

    def __init__(self, config_dict: Dict[str, Any]):
        """Initialize configuration from a dictionary."""
        self.config = config_dict or {}
        self.schema = self._load_schema()
        self._final_state = {}

    def set_state(self, key, value):
        self._final_state[key] = value
        return self

    def get_state(self, key, default=None):
        return self._final_state.get(key, self.config.get(key, default))

    def dump_state(self):
        x = {k: v for k, v in self.config.items()}
        for k, v in self._final_state.items():
            x[k] = v
        return x

    @staticmethod
    def _load_schema():
        """Load the configuration schema from the YAML file."""
        schema_path = os.path.join(os.path.dirname(__file__), "config_schema.yaml")
        with open(schema_path, "r") as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self.config.get(key, default)

    def validate(self) -> None:
        """Validate the configuration against the schema."""
        self._validate_required_fields()
        self._validate_field_types()
        self._validate_field_constraints()

    def set_deploy_defaults(self, packaging_directory: str) -> None:
        """Set default values for fields that are not provided."""
        if not self.config.get("auth"):
            self.config["auth"] = {}
        if not self.config["auth"].get("public"):
            self.config["auth"]["public"] = True
        if not self.config["auth"].get("type"):
            self.config["auth"]["type"] = AuthType.BROWSER

        if not self.config.get("health_check"):
            self.config["health_check"] = {}
        if not self.config["health_check"].get("enabled"):
            self.config["health_check"]["enabled"] = False

        if not self.config.get("resources"):
            self.config["resources"] = {}
        if not self.config["resources"].get("cpu"):
            self.config["resources"]["cpu"] = 1
        if not self.config["resources"].get("memory"):
            self.config["resources"]["memory"] = "4096Mi"
        if not self.config["resources"].get("disk"):
            self.config["resources"]["disk"] = "20Gi"

        if not self.config.get("replicas", None):
            self.config["replicas"] = {
                "min": 1,
                "max": 1,
            }
        else:
            max_is_set = self.config["replicas"].get("max", None) is not None
            min_is_set = self.config["replicas"].get("min", None) is not None
            if max_is_set and not min_is_set:
                # If users want to set 0 replicas for min,
                # then they need explicitly specify min to 0
                self.config["replicas"]["min"] = 1  # Atleast set 1 replica
            if min_is_set and not max_is_set:
                # In the situations where we dont have min/max replicas, we can
                # set max to min.
                self.config["replicas"]["max"] = self.config["replicas"].get("min")

    def _validate_required_fields(self) -> None:
        """Validate that all required fields are present."""
        required_fields = self.schema.get("required", [])
        for field in required_fields:
            if field not in self.config:
                raise AppConfigError(
                    f"Required field '{field}' is missing from the configuration."
                )

    def _validate_field_types(self) -> None:
        """Validate that fields have correct types."""
        properties = self.schema.get("properties", {})

        for field, value in self.config.items():
            if field not in properties:
                raise AppConfigError(f"Unknown field '{field}' in configuration.")

            field_schema = properties[field]
            field_type = field_schema.get("type")

            if field_type == "string" and not isinstance(value, str):
                raise AppConfigError(f"Field '{field}' must be a string.")

            elif field_type == "integer" and not isinstance(value, int):
                raise AppConfigError(f"Field '{field}' must be an integer.")

            elif field_type == "boolean" and not isinstance(value, bool):
                raise AppConfigError(f"Field '{field}' must be a boolean.")

            elif field_type == "array" and not isinstance(value, list):
                raise AppConfigError(f"Field '{field}' must be an array.")

            elif field_type == "object" and not isinstance(value, dict):
                raise AppConfigError(f"Field '{field}' must be an object.")

    def _validate_field_constraints(self) -> None:
        """Validate field-specific constraints."""
        properties = self.schema.get("properties", {})

        # Validate name
        if "name" in self.config:
            name = self.config["name"]
            max_length = properties["name"].get("maxLength", 20)
            if len(name) > max_length:
                raise AppConfigError(
                    f"App name '{name}' exceeds maximum length of {max_length} characters."
                )

        # Validate port
        if "port" in self.config:
            port = self.config["port"]
            min_port = properties["port"].get("minimum", 1)
            max_port = properties["port"].get("maximum", 65535)
            if port < min_port or port > max_port:
                raise AppConfigError(
                    f"Port number {port} is outside valid range ({min_port}-{max_port})."
                )

        # Validate dependencies (only one type allowed)
        if "dependencies" in self.config:
            deps = self.config["dependencies"]
            if not isinstance(deps, dict):
                raise AppConfigError("Dependencies must be an object.")

            valid_dep_types = [
                "from_requirements_file",
                "from_pyproject_toml",
            ]

            found_types = [dep_type for dep_type in valid_dep_types if dep_type in deps]

            if len(found_types) > 1:
                raise AppConfigError(
                    f"You can only specify one mode of specifying dependencies. You have specified : {found_types} . Please only set one."
                )

        # Validate that each tag has exactly one key
        if "tags" in self.config:
            tags = self.config["tags"]
            for tag in tags:
                if not isinstance(tag, dict):
                    raise AppConfigError(
                        "Each tag must be a dictionary. %s is of type %s"
                        % (str(tag), type(tag))
                    )
                if len(tag.keys()) != 1:
                    raise AppConfigError(
                        "Each tag must have exactly one key-value pair. Tag %s has %d key-value pairs."
                        % (str(tag), len(tag.keys()))
                    )
        if "replicas" in self.config:
            replicas = self.config["replicas"]
            if not isinstance(replicas, dict):
                raise AppConfigError("Replicas must be an object.")
            max_is_set = self.config["replicas"].get("max", None) is not None
            if max_is_set:
                if replicas.get("max") == 0:
                    raise AppConfigError("Max replicas must be greater than 0.")

                if replicas.get("min", 1) > replicas.get("max"):
                    raise AppConfigError(
                        "Min replicas must be less than max replicas. %s > %s"
                        % (replicas.get("min", 1), replicas.get("max", 1))
                    )

    def to_dict(self) -> Dict[str, Any]:
        """Return the configuration as a dictionary."""
        return self.config

    def to_yaml(self) -> str:
        """Return the configuration as a YAML string."""
        return yaml.dump(self.config, default_flow_style=False)

    def to_json(self) -> str:
        """Return the configuration as a JSON string."""
        return json.dumps(self.config, indent=2)

    @classmethod
    def from_file(cls, file_path: str) -> "AppConfig":
        """Create a configuration from a file."""
        if not os.path.exists(file_path):
            raise AppConfigError(f"Configuration file '{file_path}' does not exist.")

        with open(file_path, "r") as f:
            try:
                config_dict = yaml.safe_load(f)
            except Exception as e:
                raise AppConfigError(f"Failed to parse configuration file: {e}")

        return cls(config_dict)

    def update_from_cli_options(self, options):
        """
        Update configuration from CLI options using the same logic as build_config_from_options.
        This ensures consistent handling of CLI options whether they come from a config file
        or direct CLI input.
        """
        cli_config = build_config_from_options(options)

        # Process each field using allow_union property
        for key, value in cli_config.items():
            if key in self.schema.get("properties", {}):
                self._update_field(key, value)

        return self

    def _update_field(self, field_name, new_value):
        """Update a field based on its allow_union property."""
        properties = self.schema.get("properties", {})

        # Skip if field doesn't exist in schema
        if field_name not in properties:
            return

        field_schema = properties[field_name]
        allow_union = field_schema.get("allow_union", False)

        # If field doesn't exist in config, just set it
        if field_name not in self.config:
            self.config[field_name] = new_value
            return

        # If allow_union is True, merge values based on type
        if allow_union:
            current_value = self.config[field_name]

            if isinstance(current_value, list) and isinstance(new_value, list):
                # For lists, append new items
                self.config[field_name].extend(new_value)
            elif isinstance(current_value, dict) and isinstance(new_value, dict):
                # For dicts, update with new values
                self.config[field_name].update(new_value)
            else:
                # For other types, replace with new value
                self.config[field_name] = new_value
        else:
            raise AppConfigError(
                f"Field '{field_name}' does not allow union. Current value: {self.config[field_name]}, new value: {new_value}"
            )
