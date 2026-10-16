"""Tests for the Shopify product-management skill runtime helper."""

from __future__ import annotations

import importlib.util
import inspect
import io
import json
import sys
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request
from urllib.parse import parse_qs

import pytest

WORKTREE = Path(__file__).resolve().parent.parent.parent
SCRIPT = (
    WORKTREE
    / "plugins"
    / "shopify-product-management"
    / "skills"
    / "shopify-product-operations"
    / "scripts"
    / "shopify_admin.py"
)

spec = importlib.util.spec_from_file_location("shopify_admin", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load Shopify helper at {SCRIPT}")
shopify_admin = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = shopify_admin
write_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    spec.loader.exec_module(shopify_admin)
finally:
    sys.dont_write_bytecode = write_bytecode


def test_helper_test_import_leaves_no_generated_runtime_artifacts():
    support_files = [
        path.relative_to(SCRIPT.parent)
        for path in SCRIPT.parent.rglob("*")
        if path.is_file() and path != SCRIPT
    ]
    assert support_files == []


def token_environment(**overrides: str) -> dict[str, str]:
    values = {
        "SHOPIFY_SHOP": "arena-test-store",
        "SHOPIFY_ADMIN_ACCESS_TOKEN": "test-admin-token",
    }
    values.update(overrides)
    return values


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("example-store", "example-store.myshopify.com"),
        ("example-store.myshopify.com", "example-store.myshopify.com"),
        ("a1", "a1.myshopify.com"),
    ],
)
def test_normalize_shop_accepts_only_canonical_shopify_hosts(raw: str, expected: str):
    assert shopify_admin.normalize_shop(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "https://example-store.myshopify.com",
        "http://example-store.myshopify.com",
        "example-store.myshopify.com/path",
        "example-store.myshopify.com:443",
        "user@example-store.myshopify.com",
        "example-store.myshopify.com.evil.test",
        "Example-Store",
        "-example-store",
        "example-store-",
        "example_store",
        "",
    ],
)
def test_normalize_shop_rejects_noncanonical_or_ambiguous_hosts(raw: str):
    with pytest.raises(shopify_admin.ConfigError, match="valid Shopify shop"):
        shopify_admin.normalize_shop(raw)


def test_redirect_handler_rejects_before_constructing_an_external_request():
    request = urllib_request.Request(
        "https://arena-test-store.myshopify.com/admin/api/2026-10/graphql.json"
    )

    with pytest.raises(urllib_error.HTTPError, match="redirects are not permitted"):
        shopify_admin._RejectRedirects().redirect_request(
            request,
            None,
            302,
            "Found",
            {},
            "https://credential-collector.invalid/graphql",
        )


def test_default_network_boundaries_use_the_redirect_rejecting_opener():
    client_default = inspect.signature(shopify_admin.ShopifyClient).parameters["opener"].default
    cli_default = inspect.signature(shopify_admin.main).parameters["opener"].default

    assert client_default is shopify_admin._shopify_urlopen
    assert cli_default is shopify_admin._shopify_urlopen


@pytest.mark.parametrize("version", ["2026-01", "2026-04", "2026-07", "2026-10"])
def test_config_accepts_quarterly_api_versions(version: str):
    config = shopify_admin.Config.from_environ(token_environment(SHOPIFY_API_VERSION=version))
    assert config.api_version == version


@pytest.mark.parametrize("version", ["latest", "unstable", "2026-02", "26-10", "2026-10/path"])
def test_config_rejects_unpinned_or_invalid_api_versions(version: str):
    with pytest.raises(shopify_admin.ConfigError, match="API version"):
        shopify_admin.Config.from_environ(token_environment(SHOPIFY_API_VERSION=version))


def test_config_defaults_to_2026_10_and_safe_mode():
    config = shopify_admin.Config.from_environ(token_environment())
    assert config.api_version == "2026-10"
    assert config.operation_mode == "safe"
    assert config.auth_strategy == "admin_access_token"


def test_config_selects_complete_client_credentials_pair():
    config = shopify_admin.Config.from_environ(
        {
            "SHOPIFY_SHOP": "arena-test-store.myshopify.com",
            "SHOPIFY_CLIENT_ID": "test-client-id",
            "SHOPIFY_CLIENT_SECRET": "test-client-secret",
            "SHOPIFY_OPERATION_MODE": "unrestricted",
        }
    )
    assert config.auth_strategy == "client_credentials"
    assert config.operation_mode == "unrestricted"


@pytest.mark.parametrize(
    "environment",
    [
        {"SHOPIFY_SHOP": "arena-test-store"},
        {"SHOPIFY_SHOP": "arena-test-store", "SHOPIFY_CLIENT_ID": "only-id"},
        {"SHOPIFY_SHOP": "arena-test-store", "SHOPIFY_CLIENT_SECRET": "only-secret"},
        {
            "SHOPIFY_SHOP": "arena-test-store",
            "SHOPIFY_ADMIN_ACCESS_TOKEN": "test-admin-token",
            "SHOPIFY_CLIENT_ID": "test-client-id",
            "SHOPIFY_CLIENT_SECRET": "test-client-secret",
        },
    ],
)
def test_config_rejects_missing_partial_or_competing_auth(environment: dict[str, str]):
    with pytest.raises(shopify_admin.ConfigError, match="authentication") as error:
        shopify_admin.Config.from_environ(environment)
    assert not any(value in str(error.value) for value in environment.values())


def test_config_rejects_unknown_operation_mode_without_echoing_it():
    environment = token_environment(SHOPIFY_OPERATION_MODE="dangerously-misspelled")
    with pytest.raises(shopify_admin.ConfigError, match="operation mode") as error:
        shopify_admin.Config.from_environ(environment)
    assert "dangerously-misspelled" not in str(error.value)


@pytest.mark.parametrize(
    ("document", "expected"),
    [
        ("{ shop { id } }", "query"),
        ("query ShopIdentity { shop { id } }", "query"),
        ('query { product(query: "mutation is data") { id } }', "query"),
        ("# mutation Hidden { x }\nquery { shop { id } }", "query"),
        ("mutation UpdateProduct { productUpdate { userErrors { message } } }", "mutation"),
        (
            "fragment ProductId on Product { id }\n"
            "mutation UpdateProduct { productUpdate { product { ...ProductId } } }",
            "mutation",
        ),
        ('query { shop { metafield(key: """mutation text""") { id } } }', "query"),
    ],
)
def test_operation_kind_ignores_comments_and_string_literals(document: str, expected: str):
    assert shopify_admin.operation_kind(document) == expected


@pytest.mark.parametrize("document", ["", "fragment F on Product { id }"])
def test_operation_kind_rejects_documents_without_an_operation(document: str):
    with pytest.raises(shopify_admin.ConfigError, match="GraphQL operation"):
        shopify_admin.operation_kind(document)


def test_read_only_mode_rejects_mutations_even_when_confirmed():
    with pytest.raises(shopify_admin.PolicyError, match="read-only"):
        shopify_admin.authorize_operation("mutation", "read-only", confirmed=True)


def test_safe_mode_requires_confirmation_for_mutations():
    with pytest.raises(shopify_admin.PolicyError, match="confirmation"):
        shopify_admin.authorize_operation("mutation", "safe", confirmed=False)
    shopify_admin.authorize_operation("mutation", "safe", confirmed=True)


def test_unrestricted_mode_executes_mutations_without_confirmation():
    shopify_admin.authorize_operation("mutation", "unrestricted", confirmed=False)


@pytest.mark.parametrize("mode", ["read-only", "safe", "unrestricted"])
def test_queries_are_allowed_in_every_mode(mode: str):
    shopify_admin.authorize_operation("query", mode, confirmed=False)


class FakeResponse:
    def __init__(self, payload: dict, *, api_version: str | None = "2026-10"):
        self._body = json.dumps(payload).encode("utf-8")
        self.headers = {}
        if api_version is not None:
            self.headers["X-Shopify-API-Version"] = api_version

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return self._body


class RecordingOpener:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, request, *, timeout):
        self.requests.append((request, timeout))
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


def request_headers(request) -> dict[str, str]:
    return {key.lower(): value for key, value in request.header_items()}


def test_execute_with_direct_token_uses_pinned_graphql_endpoint_and_header():
    opener = RecordingOpener(
        FakeResponse(
            {
                "data": {"shop": {"id": "gid://shopify/Shop/1"}},
                "extensions": {
                    "cost": {
                        "requestedQueryCost": 1,
                        "actualQueryCost": 1,
                        "throttleStatus": {
                            "maximumAvailable": 2000,
                            "currentlyAvailable": 1999,
                            "restoreRate": 100,
                        },
                    }
                },
            }
        )
    )
    config = shopify_admin.Config.from_environ(token_environment())
    client = shopify_admin.ShopifyClient(config, opener=opener, sleep=lambda _: None)

    result = client.execute("query Identity { shop { id } }", {"unused": False})

    assert result.ok is True
    assert result.requested_api_version == "2026-10"
    assert result.resolved_api_version == "2026-10"
    assert result.throttle_status["currentlyAvailable"] == 1999
    assert len(opener.requests) == 1
    request, timeout = opener.requests[0]
    assert request.full_url == (
        "https://arena-test-store.myshopify.com/admin/api/2026-10/graphql.json"
    )
    assert timeout == shopify_admin.DEFAULT_TIMEOUT_SECONDS
    assert request_headers(request)["x-shopify-access-token"] == "test-admin-token"
    body = json.loads(request.data)
    assert body == {
        "query": "query Identity { shop { id } }",
        "variables": {"unused": False},
    }
    assert "test-admin-token" not in json.dumps(result.to_dict())


def test_client_credentials_are_exchanged_once_per_process_and_never_returned():
    opener = RecordingOpener(
        FakeResponse(
            {
                "access_token": "acquired-access-token",
                "scope": "write_products,write_inventory",
                "expires_in": 86399,
            },
            api_version=None,
        ),
        FakeResponse({"data": {"shop": {"id": "gid://shopify/Shop/1"}}}),
        FakeResponse({"data": {"shop": {"id": "gid://shopify/Shop/1"}}}),
    )
    config = shopify_admin.Config.from_environ(
        {
            "SHOPIFY_SHOP": "arena-test-store",
            "SHOPIFY_CLIENT_ID": "test-client-id",
            "SHOPIFY_CLIENT_SECRET": "test-client-secret",
        }
    )
    client = shopify_admin.ShopifyClient(config, opener=opener, sleep=lambda _: None)

    first = client.execute("query { shop { id } }", {})
    second = client.execute("query { shop { id } }", {})

    assert first.ok and second.ok
    assert len(opener.requests) == 3
    token_request, _ = opener.requests[0]
    assert token_request.full_url == (
        "https://arena-test-store.myshopify.com/admin/oauth/access_token"
    )
    token_form = parse_qs(token_request.data.decode("utf-8"))
    assert token_form == {
        "grant_type": ["client_credentials"],
        "client_id": ["test-client-id"],
        "client_secret": ["test-client-secret"],
    }
    for graph_request, _ in opener.requests[1:]:
        assert request_headers(graph_request)["x-shopify-access-token"] == ("acquired-access-token")
        assert b"acquired-access-token" not in graph_request.data
    rendered = json.dumps([first.to_dict(), second.to_dict()])
    for secret in ("test-client-id", "test-client-secret", "acquired-access-token"):
        assert secret not in rendered


def test_execute_surfaces_shopify_api_version_fall_forward():
    opener = RecordingOpener(
        FakeResponse(
            {"data": {"shop": {"id": "gid://shopify/Shop/1"}}},
            api_version="2027-01",
        )
    )
    client = shopify_admin.ShopifyClient(
        shopify_admin.Config.from_environ(token_environment()),
        opener=opener,
        sleep=lambda _: None,
    )

    result = client.execute("query { shop { id } }", {})

    assert result.requested_api_version == "2026-10"
    assert result.resolved_api_version == "2027-01"
    assert result.api_version_mismatch is True


def test_execute_classifies_top_level_and_nested_user_errors():
    opener = RecordingOpener(
        FakeResponse(
            {
                "data": {
                    "productUpdate": {
                        "product": None,
                        "userErrors": [
                            {"field": ["product", "title"], "message": "Title is invalid"}
                        ],
                    }
                },
                "errors": [
                    {
                        "message": "A resolver warning",
                        "extensions": {"code": "BAD_USER_INPUT"},
                    }
                ],
            }
        )
    )
    config = shopify_admin.Config.from_environ(
        token_environment(SHOPIFY_OPERATION_MODE="unrestricted")
    )
    client = shopify_admin.ShopifyClient(config, opener=opener, sleep=lambda _: None)

    result = client.execute(
        'mutation Update { productUpdate(product: {title: "x"}) { userErrors { field message } } }',
        {},
    )

    assert result.ok is False
    assert result.top_level_errors[0]["extensions"]["code"] == "BAD_USER_INPUT"
    assert result.user_errors == [{"field": ["product", "title"], "message": "Title is invalid"}]
    rendered = result.to_dict()
    assert rendered["status"] == "api_error"
    assert rendered["errors"]["graphql"][0]["message"] == "A resolver warning"
    assert rendered["errors"]["user"][0]["message"] == "Title is invalid"


def test_execute_redacts_config_and_acquired_secrets_from_transport_errors():
    opener = RecordingOpener(
        FakeResponse(
            {
                "access_token": "acquired-access-token",
                "scope": "write_products",
                "expires_in": 86399,
            },
            api_version=None,
        ),
        OSError(
            "failed for arena-test-store.myshopify.com with acquired-access-token "
            "test-client-id test-client-secret"
        ),
    )
    config = shopify_admin.Config.from_environ(
        {
            "SHOPIFY_SHOP": "arena-test-store",
            "SHOPIFY_CLIENT_ID": "test-client-id",
            "SHOPIFY_CLIENT_SECRET": "test-client-secret",
        }
    )
    client = shopify_admin.ShopifyClient(config, opener=opener, sleep=lambda _: None)

    with pytest.raises(shopify_admin.TransportError) as error:
        client.execute("query { shop { id } }", {})

    message = str(error.value)
    assert "[REDACTED]" in message
    for secret in (
        "arena-test-store",
        "arena-test-store.myshopify.com",
        "test-client-id",
        "test-client-secret",
        "acquired-access-token",
    ):
        assert secret not in message


def test_execute_redacts_credentials_echoed_by_graphql_error_payloads():
    opener = RecordingOpener(
        FakeResponse(
            {
                "data": {
                    "productUpdate": {
                        "userErrors": [
                            {
                                "field": ["product"],
                                "message": "Shopify rejected test-admin-token",
                            }
                        ]
                    }
                },
                "errors": [{"message": "Header contained test-admin-token"}],
                "extensions": {"debug": "test-admin-token"},
            }
        )
    )
    config = shopify_admin.Config.from_environ(
        token_environment(SHOPIFY_OPERATION_MODE="unrestricted")
    )
    client = shopify_admin.ShopifyClient(config, opener=opener, sleep=lambda _: None)

    result = client.execute(
        'mutation Update { productUpdate(product: {title: "x"}) { userErrors { field message } } }',
        {},
    )

    rendered = json.dumps(result.to_dict())
    assert "test-admin-token" not in rendered
    assert rendered.count("[REDACTED]") >= 3


def test_safe_policy_blocks_before_authentication_or_networking():
    opener = RecordingOpener()
    client = shopify_admin.ShopifyClient(
        shopify_admin.Config.from_environ(token_environment()),
        opener=opener,
        sleep=lambda _: None,
    )

    with pytest.raises(shopify_admin.PolicyError):
        client.execute('mutation { productDelete(input: {id: "gid"}) { deletedProductId } }', {})

    assert opener.requests == []


def test_doctor_reports_identity_resolved_version_and_missing_scopes():
    opener = RecordingOpener(
        FakeResponse(
            {
                "data": {
                    "shop": {
                        "id": "gid://shopify/Shop/1",
                        "name": "Arena Test Store",
                        "myshopifyDomain": "arena-test-store.myshopify.com",
                    },
                    "currentAppInstallation": {
                        "accessScopes": [
                            {"handle": "write_products"},
                            {"handle": "write_inventory"},
                            {"handle": "read_locations"},
                            {"handle": "write_publications"},
                        ]
                    },
                }
            },
            api_version="2026-10",
        )
    )
    client = shopify_admin.ShopifyClient(
        shopify_admin.Config.from_environ(token_environment()),
        opener=opener,
        sleep=lambda _: None,
    )

    report = client.doctor()

    assert report["ok"] is False
    assert report["shop"] == {
        "id": "gid://shopify/Shop/1",
        "name": "Arena Test Store",
        "myshopifyDomain": "arena-test-store.myshopify.com",
    }
    assert report["requestedApiVersion"] == "2026-10"
    assert report["resolvedApiVersion"] == "2026-10"
    assert report["grantedScopes"] == [
        "read_locations",
        "write_inventory",
        "write_products",
        "write_publications",
    ]
    assert report["missingScopes"] == ["write_files"]
    request, _ = opener.requests[0]
    body = json.loads(request.data)
    assert "currentAppInstallation" in body["query"]
    assert "accessScopes" in body["query"]


def execution_result(
    *,
    data=None,
    top_level_errors=None,
    user_errors=None,
    extensions=None,
):
    return shopify_admin.ExecutionResult(
        data={} if data is None else data,
        top_level_errors=[] if top_level_errors is None else top_level_errors,
        user_errors=[] if user_errors is None else user_errors,
        requested_api_version="2026-10",
        resolved_api_version="2026-10",
        extensions={} if extensions is None else extensions,
    )


class StubBatchClient:
    def __init__(self, responses):
        self.config = shopify_admin.Config.from_environ(
            token_environment(SHOPIFY_OPERATION_MODE="unrestricted")
        )
        self.responses = iter(responses)
        self.calls = []
        self.paced = []
        self.retry_paced = []

    def execute(self, document, variables, operation_name=None, *, confirmed=False):
        self.calls.append((document, variables, operation_name, confirmed))
        response = next(self.responses)
        if isinstance(response, BaseException):
            raise response
        return response

    def pace(self, result):
        self.paced.append(result)

    def pace_retry_after(self, error):
        self.retry_paced.append(error.retry_after)


def test_stream_batch_preserves_indexes_and_continues_after_row_and_api_errors():
    client = StubBatchClient(
        [
            execution_result(data={"productUpdate": {"product": {"id": "gid://1"}}}),
            execution_result(
                data={"productUpdate": {"product": None}},
                user_errors=[{"field": ["product"], "message": "Invalid product"}],
            ),
            execution_result(
                top_level_errors=[{"message": "GraphQL failed"}],
            ),
        ]
    )
    rows = [
        '{"id":"first","variables":{"input":{"id":"gid://1"}}}\n',
        "not-json\n",
        '{"id":"third","variables":{"input":{"id":"gid://3"}}}\n',
        '{"id":"fourth","variables":{"input":{"id":"gid://4"}}}\n',
    ]

    events = list(
        shopify_admin.stream_batch(
            client,
            "mutation Update($input: ProductInput!) { productUpdate(product: $input) { product { id } userErrors { field message } } }",
            rows,
        )
    )

    items = [event for event in events if event["type"] == "item"]
    assert [item["index"] for item in items] == [0, 1, 2, 3]
    assert [item["line"] for item in items] == [1, 2, 3, 4]
    assert [item["status"] for item in items] == [
        "succeeded",
        "failed",
        "failed",
        "failed",
    ]
    assert items[0]["itemId"] == "first"
    assert items[1]["error"]["type"] == "input"
    assert items[2]["result"]["errors"]["user"][0]["message"] == "Invalid product"
    assert items[3]["result"]["errors"]["graphql"][0]["message"] == "GraphQL failed"
    assert events[-1] == {
        "type": "summary",
        "status": "completed",
        "processed": 4,
        "succeeded": 1,
        "failed": 3,
        "unknown": 0,
    }
    assert len(client.calls) == 3


def test_stream_batch_has_no_plugin_imposed_item_cap():
    successful = execution_result(data={"productUpdate": {"product": {"id": "gid://1"}}})

    class UncappedClient(StubBatchClient):
        def __init__(self):
            super().__init__([])

        def execute(self, document, variables, operation_name=None, *, confirmed=False):
            self.calls.append(variables)
            return successful

    client = UncappedClient()
    count = 10_005
    rows = ('{"input":{"id":"gid://1"}}\n' for _ in range(count))
    item_count = 0
    summary = None

    for event in shopify_admin.stream_batch(
        client,
        "mutation Update($input: ProductInput!) { productUpdate(product: $input) { product { id } userErrors { message } } }",
        rows,
    ):
        if event["type"] == "item":
            item_count += 1
        else:
            summary = event

    assert item_count == count
    assert len(client.calls) == count
    assert summary is not None
    assert summary["processed"] == count
    assert summary["succeeded"] == count


def test_stream_batch_stops_after_ambiguous_mutation_transport_failure():
    successful = execution_result(data={"productUpdate": {"product": {"id": "gid://1"}}})
    ambiguous = shopify_admin.TransportError(
        "connection closed before a response",
        outcome_unknown=True,
    )
    client = StubBatchClient([successful, ambiguous, successful])
    produced = 0

    def rows():
        nonlocal produced
        for number in range(5):
            produced += 1
            yield json.dumps({"id": number, "variables": {"input": {"id": number}}}) + "\n"

    events = list(
        shopify_admin.stream_batch(
            client,
            "mutation Update($input: ProductInput!) { productUpdate(product: $input) { product { id } userErrors { message } } }",
            rows(),
        )
    )

    assert produced == 2
    assert len(client.calls) == 2
    assert [event["status"] for event in events if event["type"] == "item"] == [
        "succeeded",
        "unknown",
    ]
    assert events[-1] == {
        "type": "summary",
        "status": "stopped_unknown",
        "processed": 2,
        "succeeded": 1,
        "failed": 0,
        "unknown": 1,
    }


def test_stream_batch_paces_from_graphql_cost_metadata():
    sleeps = []
    opener = RecordingOpener(
        FakeResponse(
            {
                "data": {"shop": {"id": "gid://shopify/Shop/1"}},
                "extensions": {
                    "cost": {
                        "requestedQueryCost": 10,
                        "actualQueryCost": 10,
                        "throttleStatus": {
                            "maximumAvailable": 100,
                            "currentlyAvailable": 0,
                            "restoreRate": 2,
                        },
                    }
                },
            }
        ),
        FakeResponse({"data": {"shop": {"id": "gid://shopify/Shop/1"}}}),
    )
    client = shopify_admin.ShopifyClient(
        shopify_admin.Config.from_environ(token_environment()),
        opener=opener,
        sleep=sleeps.append,
    )

    events = list(
        shopify_admin.stream_batch(
            client,
            "query Identity { shop { id } }",
            ["{}\n", "{}\n"],
        )
    )

    assert events[-1]["succeeded"] == 2
    assert sleeps == [5.0]


def test_stream_batch_honors_retry_after_and_continues_definite_api_error():
    retry_error = shopify_admin.ApiError(
        "Shopify requested throttling",
        status_code=429,
        retry_after=2.5,
    )
    client = StubBatchClient([retry_error, execution_result()])

    events = list(
        shopify_admin.stream_batch(
            client,
            "query Identity { shop { id } }",
            ["{}\n", "{}\n"],
        )
    )

    assert client.retry_paced == [2.5]
    assert [event["status"] for event in events if event["type"] == "item"] == [
        "failed",
        "succeeded",
    ]
    assert events[-1]["failed"] == 1


def test_cli_graphql_reads_files_and_emits_only_structured_json(tmp_path):
    document_path = tmp_path / "query.graphql"
    variables_path = tmp_path / "variables.json"
    document_path.write_text("query Identity { shop { id } }", encoding="utf-8")
    variables_path.write_text('{"includeName":false}', encoding="utf-8")
    opener = RecordingOpener(FakeResponse({"data": {"shop": {"id": "gid://shopify/Shop/1"}}}))
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = shopify_admin.main(
        [
            "graphql",
            "--document-file",
            str(document_path),
            "--variables-file",
            str(variables_path),
        ],
        environ=token_environment(SHOPIFY_OPERATION_MODE="unrestricted"),
        stdout=stdout,
        stderr=stderr,
        opener=opener,
        sleep=lambda _: None,
    )

    assert exit_code == shopify_admin.EXIT_OK
    assert stderr.getvalue() == ""
    payload = json.loads(stdout.getvalue())
    assert payload["status"] == "success"
    assert payload["data"]["shop"]["id"] == "gid://shopify/Shop/1"
    assert "test-admin-token" not in stdout.getvalue()


def test_cli_batch_emits_jsonl_items_then_final_summary(tmp_path):
    document_path = tmp_path / "query.graphql"
    jsonl_path = tmp_path / "variables.jsonl"
    document_path.write_text("query Identity { shop { id } }", encoding="utf-8")
    jsonl_path.write_text("{}\ninvalid\n{}\n", encoding="utf-8")
    opener = RecordingOpener(
        FakeResponse({"data": {"shop": {"id": "gid://shopify/Shop/1"}}}),
        FakeResponse({"data": {"shop": {"id": "gid://shopify/Shop/1"}}}),
    )
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = shopify_admin.main(
        [
            "batch",
            "--document-file",
            str(document_path),
            "--variables-jsonl",
            str(jsonl_path),
        ],
        environ=token_environment(),
        stdout=stdout,
        stderr=stderr,
        opener=opener,
        sleep=lambda _: None,
    )

    output = [json.loads(line) for line in stdout.getvalue().splitlines()]
    assert exit_code == shopify_admin.EXIT_INPUT
    assert stderr.getvalue() == ""
    assert [item["type"] for item in output] == ["item", "item", "item", "summary"]
    assert output[-1] == {
        "type": "summary",
        "status": "completed",
        "processed": 3,
        "succeeded": 2,
        "failed": 1,
        "unknown": 0,
    }


def test_cli_safe_mode_rejects_mutation_before_network(tmp_path):
    document_path = tmp_path / "mutation.graphql"
    document_path.write_text(
        'mutation Delete { productDelete(input: {id: "gid://1"}) { deletedProductId } }',
        encoding="utf-8",
    )
    opener = RecordingOpener()
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = shopify_admin.main(
        ["graphql", "--document-file", str(document_path)],
        environ=token_environment(),
        stdout=stdout,
        stderr=stderr,
        opener=opener,
        sleep=lambda _: None,
    )

    assert exit_code == shopify_admin.EXIT_POLICY
    assert stdout.getvalue() == ""
    assert json.loads(stderr.getvalue())["error"]["type"] == "policy"
    assert opener.requests == []
