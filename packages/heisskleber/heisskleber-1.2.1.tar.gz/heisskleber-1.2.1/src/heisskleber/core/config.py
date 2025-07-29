"""Configuration baseclass."""

import logging
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Literal, Self, TextIO, TypeVar, Union, get_args, get_origin

import yaml

logger = logging.getLogger("heisskleber")

ConfigType = TypeVar(
    "ConfigType",
    bound="BaseConf",
)  # https://stackoverflow.com/a/46227137 , https://docs.python.org/3/library/typing.html#typing.TypeVar


def _parse_yaml(file: TextIO) -> dict[str, Any]:
    try:
        return dict(yaml.safe_load(file))
    except yaml.YAMLError as e:
        msg = "Failed to parse config file!"
        logger.exception(msg)
        raise ValueError(msg) from e


def _parse_json(file: TextIO) -> dict[str, Any]:
    import json

    try:
        return dict(json.load(file))
    except json.JSONDecodeError as e:
        msg = "Failed to parse config file!"
        logger.exception(msg)
        raise ValueError(msg) from e


def _parser(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()

    with path.open() as f:
        if suffix in [".yaml", ".yml"]:
            return _parse_yaml(f)
        if suffix == ".json":
            return _parse_json(f)
        msg = f"Unsupported file format {suffix}."
        logger.exception(msg)
        raise ValueError


def _check_type(value: Any, expected_type: Any) -> bool:
    origin = get_origin(expected_type)
    if origin is Literal:  # Explicitly check literal
        if value not in get_args(expected_type):
            logger.exception("%s is not part of %s", value, get_args(expected_type))
            raise TypeError
        return True
    return isinstance(value, expected_type)


@dataclass
class BaseConf:
    """Default configuration class for generic configuration info."""

    def __post_init__(self) -> None:
        """Check if all attributes are the same type as the original defition of the dataclass."""
        for field in fields(self):
            value = getattr(self, field.name)
            if value is None:  # Allow optional fields
                continue
            if hasattr(field.type, "__origin__") and field.type.__origin__ is Union:
                if not any(_check_type(value, t) for t in field.type.__args__):
                    raise TypeError
                continue
            if not _check_type(value, field.type):  # Failed field comparison
                raise TypeError

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> Self:
        """Create a config instance from a dictionary, including only fields defined in the dataclass.

        Arguments:
            config_dict: Dictionary containing configuration values.
                        Keys should match dataclass field names.

        Returns:
            An instance of the configuration class with values from the dictionary.

        Raises:
            TypeError: If provided values don't match field types.

        Example:
            >>> from dataclasses import dataclass
            >>> @dataclass
            ... class ServerConfig(BaseConf):
            ...     host: str
            ...     port: int
            ...     debug: bool = False
            >>>
            >>> config = ServerConfig.from_dict({
            ...     "host": "localhost",
            ...     "port": 8080,
            ...     "debug": True,
            ...     "invalid_key": "ignored"  # Will be filtered out
            ... })
            >>> config.host
            'localhost'
            >>> config.port
            8080
            >>> config.debug
            True
            >>> hasattr(config, "invalid_key")  # Extra keys are ignored
            False
            >>>
            >>> # Type validation
            >>> try:
            ...     ServerConfig.from_dict({"host": "localhost", "port": "8080"})  # Wrong type
            ... except TypeError as e:
            ...     print("TypeError raised as expected")
            TypeError raised as expected

        """
        valid_fields = {f.name for f in fields(cls)}
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_fields}
        return cls(**filtered_dict)

    @classmethod
    def from_file(cls, file_path: str | Path) -> Self:
        """Create a config instance from a file - accepts yaml or json."""
        path = Path(file_path)
        if not path.exists():
            logger.exception("Config file not found: %(path)s", {"path": path})
            raise FileNotFoundError

        return cls.from_dict(_parser(path))
