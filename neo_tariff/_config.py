"""Client configuration helpers for NeoTariff clients.

Centralizes environment-variable and optional ``.env`` file resolution so
sync and async clients stay behaviorally consistent.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Mapping

from neo_tariff.exceptions import NeoTariffError

DEFAULT_BASE_URL = "https://tariff-data.enterprise-neo.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2


@dataclass(frozen=True)
class ClientConfig:
    """Resolved client configuration values."""

    api_key: str
    base_url: str
    timeout: float
    max_retries: int


def _normalize_env_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _parse_env_file(env_file: str | PathLike[str]) -> dict[str, str]:
    path = Path(env_file).expanduser()
    if not path.exists():
        raise NeoTariffError(f"Env file not found: {path}")

    values: dict[str, str] = {}
    for line_no, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            raise NeoTariffError(
                f"Invalid env line {line_no} in {path}: expected KEY=VALUE"
            )
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            raise NeoTariffError(
                f"Invalid env line {line_no} in {path}: empty key name"
            )
        values[key] = _normalize_env_value(value)
    return values


def _read_env(name: str, file_values: Mapping[str, str]) -> str | None:
    if name in file_values:
        value = file_values[name].strip()
        return value or None
    env_value = os.environ.get(name)
    if env_value is None:
        return None
    env_value = env_value.strip()
    return env_value or None


def _resolve_timeout(
    timeout: float | None,
    file_values: Mapping[str, str],
) -> float:
    if timeout is not None:
        if timeout <= 0:
            raise NeoTariffError("timeout must be > 0")
        return timeout

    raw = _read_env("NEO_TARIFF_TIMEOUT", file_values)
    if raw is None:
        return DEFAULT_TIMEOUT
    try:
        value = float(raw)
    except ValueError as exc:
        raise NeoTariffError(
            "Invalid NEO_TARIFF_TIMEOUT value; expected a number."
        ) from exc
    if value <= 0:
        raise NeoTariffError("NEO_TARIFF_TIMEOUT must be > 0")
    return value


def _resolve_max_retries(
    max_retries: int | None,
    file_values: Mapping[str, str],
) -> int:
    if max_retries is not None:
        if max_retries < 0:
            raise NeoTariffError("max_retries must be >= 0")
        return max_retries

    raw = _read_env("NEO_TARIFF_MAX_RETRIES", file_values)
    if raw is None:
        return DEFAULT_MAX_RETRIES
    try:
        value = int(raw)
    except ValueError as exc:
        raise NeoTariffError(
            "Invalid NEO_TARIFF_MAX_RETRIES value; expected an integer."
        ) from exc
    if value < 0:
        raise NeoTariffError("NEO_TARIFF_MAX_RETRIES must be >= 0")
    return value


def resolve_client_config(
    *,
    api_key: str | None,
    base_url: str | None,
    timeout: float | None,
    max_retries: int | None,
    env_file: str | PathLike[str] | None,
) -> ClientConfig:
    """Resolve client settings from explicit args + env + optional env file.

    Precedence is:
    1. Explicit constructor argument
    2. Optional ``env_file`` values
    3. Process environment variables
    4. SDK defaults
    """

    file_values: dict[str, str] = {}
    if env_file is not None:
        file_values = _parse_env_file(env_file)

    resolved_api_key = api_key or _read_env("NEO_TARIFF_API_KEY", file_values)
    if not resolved_api_key:
        raise NeoTariffError(
            "No API key provided. Either pass api_key= to the client "
            "or set the NEO_TARIFF_API_KEY environment variable."
        )

    resolved_base_url = (
        base_url or _read_env("NEO_TARIFF_BASE_URL", file_values) or DEFAULT_BASE_URL
    )

    return ClientConfig(
        api_key=resolved_api_key,
        base_url=resolved_base_url,
        timeout=_resolve_timeout(timeout, file_values),
        max_retries=_resolve_max_retries(max_retries, file_values),
    )
