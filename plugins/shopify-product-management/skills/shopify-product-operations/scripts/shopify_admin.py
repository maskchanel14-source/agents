#!/usr/bin/env python3
"""Credential-safe Shopify Admin GraphQL transport for agent skills.

The helper deliberately accepts GraphQL documents and variables from files so
credentials and user-controlled values never need shell interpolation. It uses
only the Python standard library and never writes credentials or access tokens
to stdout, stderr, or repository files.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from collections.abc import Callable, Iterable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Literal, TextIO, cast
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

DEFAULT_API_VERSION = "2026-10"
DEFAULT_TIMEOUT_SECONDS = 30.0
REQUIRED_SCOPES = frozenset(
    {
        "write_products",
        "write_inventory",
        "read_locations",
        "write_publications",
        "write_files",
    }
)
OPERATION_MODES = frozenset({"read-only", "safe", "unrestricted"})
_QUARTERLY_API_VERSION = re.compile(r"^20\d{2}-(?:01|04|07|10)$")
_SHOP_SUBDOMAIN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")

OperationKind = Literal["query", "mutation"]
OperationMode = Literal["read-only", "safe", "unrestricted"]
AuthStrategy = Literal["admin_access_token", "client_credentials"]


class ShopifyHelperError(Exception):
    """Base class for errors that the CLI renders as structured JSON."""


class ConfigError(ShopifyHelperError):
    """Configuration or input is invalid before an API call is attempted."""


class PolicyError(ShopifyHelperError):
    """The configured operation mode does not authorize a request."""


class InputError(ShopifyHelperError):
    """A document, variables file, or streamed JSONL row is invalid."""


class TransportError(ShopifyHelperError):
    """A network/protocol failure, optionally with an unknown mutation outcome."""

    def __init__(self, message: str, *, outcome_unknown: bool = False) -> None:
        super().__init__(message)
        self.outcome_unknown = outcome_unknown


class ApiError(ShopifyHelperError):
    """Shopify returned a definite HTTP, GraphQL, or mutation-level error."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


def normalize_shop(value: str) -> str:
    """Return a canonical ``*.myshopify.com`` host or reject unsafe input."""

    if not isinstance(value, str) or value != value.strip() or not value:
        raise ConfigError(
            "SHOPIFY_SHOP must be a valid Shopify shop subdomain or *.myshopify.com domain."
        )
    suffix = ".myshopify.com"
    subdomain = value[: -len(suffix)] if value.endswith(suffix) else value
    if not _SHOP_SUBDOMAIN.fullmatch(subdomain):
        raise ConfigError(
            "SHOPIFY_SHOP must be a valid Shopify shop subdomain or *.myshopify.com domain."
        )
    return f"{subdomain}{suffix}"


def _environment_value(environ: Mapping[str, str], name: str) -> str | None:
    value = environ.get(name)
    return value if value else None


@dataclass(frozen=True)
class Config:
    """Validated runtime configuration with secret-safe representation."""

    shop: str
    api_version: str
    operation_mode: OperationMode
    auth_strategy: AuthStrategy
    admin_access_token: str | None = field(default=None, repr=False)
    client_id: str | None = field(default=None, repr=False)
    client_secret: str | None = field(default=None, repr=False)

    @classmethod
    def from_environ(cls, environ: Mapping[str, str]) -> Config:
        shop_value = _environment_value(environ, "SHOPIFY_SHOP")
        if shop_value is None:
            raise ConfigError(
                "SHOPIFY_SHOP must be a valid Shopify shop subdomain or *.myshopify.com domain."
            )
        shop = normalize_shop(shop_value)

        api_version = _environment_value(environ, "SHOPIFY_API_VERSION") or DEFAULT_API_VERSION
        if not _QUARTERLY_API_VERSION.fullmatch(api_version):
            raise ConfigError("SHOPIFY_API_VERSION must be a pinned quarterly API version.")

        raw_mode = _environment_value(environ, "SHOPIFY_OPERATION_MODE") or "safe"
        if raw_mode not in OPERATION_MODES:
            raise ConfigError("SHOPIFY_OPERATION_MODE contains an unsupported operation mode.")
        operation_mode = cast(OperationMode, raw_mode)

        access_token = _environment_value(environ, "SHOPIFY_ADMIN_ACCESS_TOKEN")
        client_id = _environment_value(environ, "SHOPIFY_CLIENT_ID")
        client_secret = _environment_value(environ, "SHOPIFY_CLIENT_SECRET")

        has_client_value = client_id is not None or client_secret is not None
        if access_token is not None and has_client_value:
            raise ConfigError("Configure exactly one complete Shopify authentication strategy.")
        if access_token is not None:
            return cls(
                shop=shop,
                api_version=api_version,
                operation_mode=operation_mode,
                auth_strategy="admin_access_token",
                admin_access_token=access_token,
            )
        if client_id is not None and client_secret is not None:
            return cls(
                shop=shop,
                api_version=api_version,
                operation_mode=operation_mode,
                auth_strategy="client_credentials",
                client_id=client_id,
                client_secret=client_secret,
            )
        raise ConfigError("Configure exactly one complete Shopify authentication strategy.")

    def secret_values(self) -> tuple[str, ...]:
        """Return non-empty credentials for defensive error-message redaction."""

        return tuple(
            value
            for value in (self.admin_access_token, self.client_id, self.client_secret)
            if value
        )


def _graphql_tokens(document: str) -> list[str]:
    """Tokenize operation keywords while ignoring comments and string literals."""

    tokens: list[str] = []
    index = 0
    length = len(document)
    while index < length:
        char = document[index]
        if char == "#":
            newline = document.find("\n", index + 1)
            index = length if newline == -1 else newline + 1
            continue
        if document.startswith('"""', index):
            end = document.find('"""', index + 3)
            if end == -1:
                raise ConfigError("The GraphQL operation document is malformed.")
            index = end + 3
            continue
        if char == '"':
            index += 1
            while index < length:
                if document[index] == "\\":
                    index += 2
                    continue
                if document[index] == '"':
                    index += 1
                    break
                index += 1
            else:
                raise ConfigError("The GraphQL operation document is malformed.")
            continue
        if char.isalpha() or char == "_":
            end = index + 1
            while end < length and (document[end].isalnum() or document[end] == "_"):
                end += 1
            tokens.append(document[index:end])
            index = end
            continue
        if char == "{":
            tokens.append(char)
        index += 1
    return tokens


def operation_kind(document: str) -> OperationKind:
    """Classify a GraphQL document conservatively for write-policy enforcement."""

    if not isinstance(document, str):
        raise ConfigError("The GraphQL operation document is invalid.")
    tokens = _graphql_tokens(document)
    if "mutation" in tokens:
        return "mutation"
    if "subscription" in tokens:
        raise ConfigError("GraphQL subscriptions are not supported by this helper.")
    if "query" in tokens or "{" in tokens and "fragment" not in tokens:
        return "query"
    raise ConfigError("The GraphQL operation document must contain a GraphQL operation.")


def authorize_operation(
    kind: OperationKind,
    mode: OperationMode,
    *,
    confirmed: bool,
) -> None:
    """Enforce read-only, safe, or explicitly unrestricted execution policy."""

    if mode not in OPERATION_MODES:
        raise ConfigError("SHOPIFY_OPERATION_MODE contains an unsupported operation mode.")
    if kind not in {"query", "mutation"}:
        raise ConfigError("The GraphQL operation type is unsupported.")
    if kind == "query":
        return
    if mode == "read-only":
        raise PolicyError("Mutations are disabled while Shopify operation mode is read-only.")
    if mode == "safe" and not confirmed:
        raise PolicyError("Safe mode requires explicit write confirmation for mutations.")


DOCTOR_QUERY = """\
query ShopifyProductAgentDoctor {
  shop {
    id
    name
    myshopifyDomain
  }
  currentAppInstallation {
    accessScopes {
      handle
    }
  }
}
"""


def _collect_user_errors(value: Any) -> list[dict[str, Any]]:
    """Collect mutation ``userErrors`` arrays anywhere below GraphQL data."""

    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "userErrors" and isinstance(child, list):
                found.extend(item for item in child if isinstance(item, dict))
            else:
                found.extend(_collect_user_errors(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_collect_user_errors(child))
    return found


def _header_value(headers: Any, name: str) -> str | None:
    if headers is None:
        return None
    direct = headers.get(name) if hasattr(headers, "get") else None
    if direct:
        return str(direct)
    if hasattr(headers, "items"):
        lowered = name.lower()
        for key, value in headers.items():
            if str(key).lower() == lowered:
                return str(value)
    return None


def _retry_after_seconds(headers: Any) -> float | None:
    raw_value = _header_value(headers, "Retry-After")
    if raw_value is None:
        return None
    try:
        value = float(raw_value)
    except ValueError:
        return None
    return value if math.isfinite(value) and value >= 0 else None


@dataclass(frozen=True)
class ExecutionResult:
    """Structured GraphQL outcome without request credentials or documents."""

    data: Any
    top_level_errors: list[Any]
    user_errors: list[dict[str, Any]]
    requested_api_version: str
    resolved_api_version: str
    extensions: dict[str, Any]

    @property
    def ok(self) -> bool:
        return not self.top_level_errors and not self.user_errors

    @property
    def api_version_mismatch(self) -> bool:
        return self.requested_api_version != self.resolved_api_version

    @property
    def throttle_status(self) -> dict[str, Any]:
        cost = self.extensions.get("cost")
        if not isinstance(cost, dict):
            return {}
        status = cost.get("throttleStatus")
        return status if isinstance(status, dict) else {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "success" if self.ok else "api_error",
            "data": self.data,
            "errors": {
                "graphql": self.top_level_errors,
                "user": self.user_errors,
            },
            "apiVersion": {
                "requested": self.requested_api_version,
                "resolved": self.resolved_api_version,
                "mismatch": self.api_version_mismatch,
            },
            "extensions": self.extensions,
        }


class ShopifyClient:
    """Minimal Admin GraphQL client with injectable network and sleep boundaries."""

    def __init__(
        self,
        config: Config,
        *,
        opener: Callable[..., Any] = urllib_request.urlopen,
        sleep: Callable[[float], None] = time.sleep,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.config = config
        self._opener = opener
        self._sleep = sleep
        self._timeout = timeout
        self._access_token: str | None = config.admin_access_token
        subdomain = config.shop[: -len(".myshopify.com")]
        self._redaction_values = {
            config.shop,
            subdomain,
            config.api_version,
            *config.secret_values(),
        }

    def _redact(self, value: object) -> str:
        rendered = str(value)
        for secret in sorted(
            (item for item in self._redaction_values if item),
            key=len,
            reverse=True,
        ):
            rendered = rendered.replace(secret, "[REDACTED]")
        return rendered

    def _request_json(
        self,
        request: urllib_request.Request,
        *,
        purpose: str,
        ambiguous_on_failure: bool,
    ) -> tuple[dict[str, Any], Any]:
        try:
            response_context = self._opener(request, timeout=self._timeout)
            with response_context as response:
                body = response.read()
                headers = response.headers
        except urllib_error.HTTPError as exc:
            try:
                error_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                error_body = ""
            detail = self._redact(error_body or exc.reason or exc)
            if 400 <= exc.code < 500:
                raise ApiError(
                    f"Shopify {purpose} request was rejected: {detail}",
                    status_code=exc.code,
                    retry_after=_retry_after_seconds(exc.headers),
                ) from None
            raise TransportError(
                f"Shopify {purpose} request failed: {detail}",
                outcome_unknown=ambiguous_on_failure,
            ) from None
        except (urllib_error.URLError, TimeoutError, OSError) as exc:
            detail = self._redact(exc)
            raise TransportError(
                f"Shopify {purpose} request failed: {detail}",
                outcome_unknown=ambiguous_on_failure,
            ) from None

        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            detail = self._redact(exc)
            raise TransportError(
                f"Shopify {purpose} returned invalid JSON: {detail}",
                outcome_unknown=ambiguous_on_failure,
            ) from None
        if not isinstance(payload, dict):
            raise TransportError(
                f"Shopify {purpose} returned an invalid response object.",
                outcome_unknown=ambiguous_on_failure,
            )
        return payload, headers

    def _get_access_token(self) -> str:
        if self._access_token:
            return self._access_token
        if not self.config.client_id or not self.config.client_secret:
            raise ConfigError("The configured Shopify authentication strategy is incomplete.")

        form = urllib_parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            }
        ).encode("utf-8")
        request = urllib_request.Request(
            f"https://{self.config.shop}/admin/oauth/access_token",
            data=form,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "shopify-product-management-agent/1.0",
            },
            method="POST",
        )
        payload, _ = self._request_json(
            request,
            purpose="authentication",
            ambiguous_on_failure=False,
        )
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise ApiError("Shopify authentication did not return an access token.")
        self._access_token = token
        self._redaction_values.add(token)
        return token

    def execute(
        self,
        document: str,
        variables: Mapping[str, Any],
        operation_name: str | None = None,
        *,
        confirmed: bool = False,
    ) -> ExecutionResult:
        """Execute one GraphQL operation after enforcing the configured write mode."""

        kind = operation_kind(document)
        authorize_operation(kind, self.config.operation_mode, confirmed=confirmed)
        if not isinstance(variables, Mapping):
            raise ConfigError("GraphQL variables must be a JSON object.")

        body: dict[str, Any] = {
            "query": document,
            "variables": dict(variables),
        }
        if operation_name:
            body["operationName"] = operation_name
        request = urllib_request.Request(
            f"https://{self.config.shop}/admin/api/{self.config.api_version}/graphql.json",
            data=json.dumps(body, separators=(",", ":")).encode("utf-8"),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "shopify-product-management-agent/1.0",
                "X-Shopify-Access-Token": self._get_access_token(),
            },
            method="POST",
        )
        payload, headers = self._request_json(
            request,
            purpose="GraphQL",
            ambiguous_on_failure=kind == "mutation",
        )
        top_level_errors = payload.get("errors")
        if not isinstance(top_level_errors, list):
            top_level_errors = []
        extensions = payload.get("extensions")
        if not isinstance(extensions, dict):
            extensions = {}
        resolved_version = (
            _header_value(headers, "X-Shopify-API-Version") or self.config.api_version
        )
        data = payload.get("data")
        return ExecutionResult(
            data=data,
            top_level_errors=top_level_errors,
            user_errors=_collect_user_errors(data),
            requested_api_version=self.config.api_version,
            resolved_api_version=resolved_version,
            extensions=extensions,
        )

    def doctor(self) -> dict[str, Any]:
        """Check shop identity, API resolution, and required product-management scopes."""

        result = self.execute(DOCTOR_QUERY, {})
        data = result.data if isinstance(result.data, dict) else {}
        installation = data.get("currentAppInstallation")
        scopes_value = installation.get("accessScopes") if isinstance(installation, dict) else []
        granted = sorted(
            {
                item["handle"]
                for item in scopes_value
                if isinstance(item, dict) and isinstance(item.get("handle"), str)
            }
        )
        missing = sorted(REQUIRED_SCOPES.difference(granted))
        return {
            "ok": result.ok and not missing,
            "shop": data.get("shop"),
            "requestedApiVersion": result.requested_api_version,
            "resolvedApiVersion": result.resolved_api_version,
            "apiVersionMismatch": result.api_version_mismatch,
            "grantedScopes": granted,
            "missingScopes": missing,
            "errors": {
                "graphql": result.top_level_errors,
                "user": result.user_errors,
            },
        }

    def pace(self, result: ExecutionResult) -> None:
        """Delay only as much as Shopify cost metadata requires for the next item."""

        delay = throttle_delay(result)
        if delay > 0:
            self._sleep(delay)

    def pace_retry_after(self, error: ApiError) -> None:
        """Honor a numeric Shopify Retry-After response before the next item."""

        if error.retry_after is not None and error.retry_after > 0:
            self._sleep(error.retry_after)


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def throttle_delay(result: ExecutionResult) -> float:
    """Calculate pacing for another operation of approximately the same cost."""

    cost = result.extensions.get("cost")
    if not isinstance(cost, dict):
        return 0.0
    status = cost.get("throttleStatus")
    if not isinstance(status, dict):
        return 0.0
    currently_available = _finite_number(status.get("currentlyAvailable"))
    restore_rate = _finite_number(status.get("restoreRate"))
    actual_cost = _finite_number(cost.get("actualQueryCost"))
    requested_cost = _finite_number(cost.get("requestedQueryCost"))
    next_cost = actual_cost if actual_cost is not None else requested_cost
    if (
        currently_available is None
        or restore_rate is None
        or restore_rate <= 0
        or next_cost is None
        or next_cost <= currently_available
    ):
        return 0.0
    return max(0.0, (next_cost - currently_available) / restore_rate)


def _batch_item(
    index: int,
    status: Literal["succeeded", "failed", "unknown"],
    *,
    item_id: Any = None,
    result: dict[str, Any] | None = None,
    error_type: str | None = None,
    message: str | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "type": "item",
        "index": index,
        "line": index + 1,
        "status": status,
    }
    if item_id is not None:
        event["itemId"] = item_id
    if result is not None:
        event["result"] = result
    if error_type is not None:
        event["error"] = {"type": error_type, "message": message or ""}
    return event


def stream_batch(
    client: ShopifyClient,
    document: str,
    lines: Iterable[str],
    operation_name: str | None = None,
    *,
    confirmed: bool = False,
) -> Iterator[dict[str, Any]]:
    """Execute an uncapped JSONL stream and yield each outcome plus one summary."""

    kind = operation_kind(document)
    authorize_operation(kind, client.config.operation_mode, confirmed=confirmed)
    succeeded = 0
    failed = 0
    unknown = 0
    stopped = False

    for index, line in enumerate(lines):
        item_id: Any = None
        try:
            decoded = json.loads(line)
            if not isinstance(decoded, dict):
                raise InputError("Each batch row must be a JSON object.")
            if "variables" in decoded:
                variables = decoded.get("variables")
                item_id = decoded.get("id", decoded.get("itemId"))
            else:
                variables = decoded
            if not isinstance(variables, dict):
                raise InputError("Each batch row's variables must be a JSON object.")
        except (json.JSONDecodeError, UnicodeError, InputError):
            failed += 1
            yield _batch_item(
                index,
                "failed",
                item_id=item_id,
                error_type="input",
                message="The JSONL row is not a valid variables object.",
            )
            continue

        try:
            result = client.execute(
                document,
                variables,
                operation_name,
                confirmed=confirmed,
            )
        except ApiError as exc:
            failed += 1
            yield _batch_item(
                index,
                "failed",
                item_id=item_id,
                error_type="api",
                message=str(exc),
            )
            client.pace_retry_after(exc)
            continue
        except TransportError as exc:
            if exc.outcome_unknown:
                unknown += 1
                stopped = True
                yield _batch_item(
                    index,
                    "unknown",
                    item_id=item_id,
                    error_type="transport",
                    message=str(exc),
                )
                break
            failed += 1
            yield _batch_item(
                index,
                "failed",
                item_id=item_id,
                error_type="transport",
                message=str(exc),
            )
            continue

        if result.ok:
            succeeded += 1
            status: Literal["succeeded", "failed", "unknown"] = "succeeded"
        else:
            failed += 1
            status = "failed"
        yield _batch_item(
            index,
            status,
            item_id=item_id,
            result=result.to_dict(),
        )
        client.pace(result)

    yield {
        "type": "summary",
        "status": "stopped_unknown" if stopped else "completed",
        "processed": succeeded + failed + unknown,
        "succeeded": succeeded,
        "failed": failed,
        "unknown": unknown,
    }


EXIT_OK = 0
EXIT_CONFIG = 2
EXIT_POLICY = 3
EXIT_TRANSPORT = 4
EXIT_API = 5
EXIT_INPUT = 6


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Credential-safe Shopify Admin GraphQL 2026-10 helper."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="Check authentication, identity, and scopes.")

    graphql_parser = subparsers.add_parser("graphql", help="Execute one GraphQL document.")
    graphql_parser.add_argument("--document-file", required=True)
    graphql_parser.add_argument("--variables-file")
    graphql_parser.add_argument("--operation-name")
    graphql_parser.add_argument("--confirm-write", action="store_true")

    batch_parser = subparsers.add_parser("batch", help="Stream one variables object per JSONL row.")
    batch_parser.add_argument("--document-file", required=True)
    batch_parser.add_argument("--variables-jsonl", required=True)
    batch_parser.add_argument("--operation-name")
    batch_parser.add_argument("--confirm-write", action="store_true")
    return parser


def _read_utf8(path: str, description: str) -> str:
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeError):
        raise InputError(f"Unable to read the requested UTF-8 {description} file.") from None


def _read_variables(path: str | None) -> dict[str, Any]:
    if path is None:
        return {}
    raw_value = _read_utf8(path, "variables")
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError:
        raise InputError("The variables file does not contain valid JSON.") from None
    if not isinstance(value, dict):
        raise InputError("The variables file must contain a JSON object.")
    return value


def _emit_json(stream: TextIO, value: Mapping[str, Any]) -> None:
    stream.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
    stream.flush()


def _error_payload(category: str, error: ShopifyHelperError) -> dict[str, Any]:
    return {
        "status": f"{category}_error",
        "error": {"type": category, "message": str(error)},
    }


@contextmanager
def _variables_jsonl_stream(path: str, stdin: TextIO) -> Iterator[TextIO]:
    try:
        if path == "-":
            yield stdin
        else:
            with open(path, encoding="utf-8") as stream:
                yield stream
    except (OSError, UnicodeError):
        raise InputError("Unable to read the requested UTF-8 variables JSONL file.") from None


def main(
    argv: list[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    stdin: TextIO = sys.stdin,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
    opener: Callable[..., Any] = urllib_request.urlopen,
    sleep: Callable[[float], None] = time.sleep,
) -> int:
    """CLI entry point; all normal output and failures are machine-readable JSON."""

    args = _argument_parser().parse_args(argv)
    try:
        config = Config.from_environ(os.environ if environ is None else environ)
        client = ShopifyClient(config, opener=opener, sleep=sleep)

        if args.command == "doctor":
            report = client.doctor()
            _emit_json(stdout, report)
            return EXIT_OK if report["ok"] else EXIT_API

        document = _read_utf8(args.document_file, "GraphQL document")
        if args.command == "graphql":
            variables = _read_variables(args.variables_file)
            result = client.execute(
                document,
                variables,
                args.operation_name,
                confirmed=args.confirm_write,
            )
            _emit_json(stdout, result.to_dict())
            return EXIT_OK if result.ok else EXIT_API

        batch_exit = EXIT_OK
        with _variables_jsonl_stream(args.variables_jsonl, stdin) as variables_stream:
            for event in stream_batch(
                client,
                document,
                variables_stream,
                args.operation_name,
                confirmed=args.confirm_write,
            ):
                _emit_json(stdout, event)
                if event.get("type") != "item" or event.get("status") == "succeeded":
                    continue
                error = event.get("error")
                error_type = error.get("type") if isinstance(error, dict) else "api"
                if event.get("status") == "unknown":
                    batch_exit = EXIT_TRANSPORT
                elif error_type == "input" and batch_exit not in {EXIT_TRANSPORT}:
                    batch_exit = EXIT_INPUT
                elif batch_exit == EXIT_OK:
                    batch_exit = EXIT_API
        return batch_exit
    except ConfigError as exc:
        _emit_json(stderr, _error_payload("configuration", exc))
        return EXIT_CONFIG
    except PolicyError as exc:
        _emit_json(stderr, _error_payload("policy", exc))
        return EXIT_POLICY
    except InputError as exc:
        _emit_json(stderr, _error_payload("input", exc))
        return EXIT_INPUT
    except TransportError as exc:
        _emit_json(stderr, _error_payload("transport", exc))
        return EXIT_TRANSPORT
    except ApiError as exc:
        _emit_json(stderr, _error_payload("api", exc))
        return EXIT_API


if __name__ == "__main__":
    raise SystemExit(main())
