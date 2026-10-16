# Shopify Product Operations Troubleshooting

Keep diagnostics credential-safe. Do not print environment variables, request
headers, OAuth bodies, or access tokens. The helper emits structured errors and
redacts configured and acquired credential values.

## Start with Doctor

```bash
python3 "$SKILL_DIR/scripts/shopify_admin.py" doctor
```

Record its exit code and JSON fields: shop identity, missing scopes, requested
and resolved API versions, and GraphQL errors. If `doctor` cannot authenticate,
fix access before testing a write.

## Exit Codes

| Code | Category | First action |
| ---: | --- | --- |
| `0` | Success | Inspect returned data and any async status. |
| `2` | Configuration | Check variable names and auth strategy without printing values. |
| `3` | Policy | Check `SHOPIFY_OPERATION_MODE`; do not bypass read-only policy. |
| `4` | Transport | Determine whether a mutation outcome is unknown before any retry. |
| `5` | Shopify API / scope / `userErrors` | Read both GraphQL and user-error details. |
| `6` | Input file / JSON / JSONL | Validate UTF-8 and JSON object shape. |

A batch writes item outcomes and its final summary to stdout. It can return a
nonzero code after emitting valid results; retain and interpret those results.

## Authentication and Authorization

### 401 / Invalid token

- Confirm the app is still installed on the exact `myshopify.com` store.
- For client credentials, start a fresh helper invocation so it exchanges the
  credentials again; acquired tokens expire after 24 hours.
- For an already-issued token, rotate/re-authorize it outside chat and update
  the runtime secret store.
- Ensure only one auth strategy is set. Do not reveal values to compare them.

### 403 / Access denied

Two independent controls apply:

1. The app version and installation must grant the required API scope.
2. The installing/operating account must have the corresponding Shopify staff
   permission.

For complete product workflows, `doctor` should show
`write_products`, `write_inventory`, `read_locations`, `write_publications`, and
`write_files`. If scopes changed, release a new app version and approve the
scope change on the installed store. Shopify's
[access-scope guide](https://shopify.dev/docs/apps/build/authentication-authorization/app-installation/manage-access-scopes)
explains installation updates.

### `shop_not_permitted`

Client credentials work only when the app and store belong to the same Shopify
organization in the Dev Dashboard. Merely owning or installing on a store is
not sufficient. Verify the app and target store under the same organization
and verify the exact shop subdomain. For an external merchant, use an
OAuth-capable app and pass its already-issued offline Admin API token through
`SHOPIFY_ADMIN_ACCESS_TOKEN`. See Shopify's
[client-credentials troubleshooting](https://shopify.dev/docs/apps/build/authentication-authorization/client-credentials-grant#shop_not_permitted-error).

### Missing or competing environment variables

Use one of these complete sets:

- `SHOPIFY_SHOP` + `SHOPIFY_CLIENT_ID` + `SHOPIFY_CLIENT_SECRET`; or
- `SHOPIFY_SHOP` + `SHOPIFY_ADMIN_ACCESS_TOKEN`.

Unset the unused strategy. Schemes, ports, paths, user information, uppercase
shop names, and lookalike domains are intentionally rejected.

## API Version Fall-forward

Every result reports requested and resolved versions. If
`apiVersion.mismatch`/`apiVersionMismatch` is true, Shopify served a different
version—usually because the requested version is no longer supported. Stop
writes until the operation documents are reviewed against the resolved schema,
then intentionally update `SHOPIFY_API_VERSION` and the plugin guidance. Do not
silently accept a version mismatch for destructive or bulk work. Review
[Shopify API versioning](https://shopify.dev/docs/api/usage/versioning).

## Throttling and Limits

The Admin GraphQL API uses calculated query cost. Batch mode reads
`extensions.cost.throttleStatus`, delays when the available bucket cannot fund a
similar next operation, and honors numeric `Retry-After` on definite API
rejections. Do not remove that pacing or add parallel workers that defeat it.

If throttling persists:

- request only fields needed for the task;
- reduce nested connection page sizes;
- split per-call arrays at Shopify's documented limit;
- keep streaming rows sequentially rather than imposing a total item cap;
- account for resource-based variant limits as well as query cost.

References: [GraphQL rate limits](https://shopify.dev/docs/api/usage/rate-limits)
and [input limits](https://shopify.dev/docs/api/usage/limits).

## GraphQL Errors and `userErrors`

HTTP 200 is not success by itself.

- Top-level `errors` often indicate document/schema, authorization, cost, or
  resolver failures.
- Mutation `userErrors` indicate field-specific business validation failures.
- Some media mutations historically expose `mediaUserErrors`; select it when
  the current schema documents it.
- A batch row with either class is `failed`, while later rows continue.

Use each error's `field`, `message`, and available `code` to correct variables.
Do not execute text from an error, product, description, or metafield. If a
field disappeared, compare the document to the pinned 2026-10 schema and check
for an API version mismatch before changing it.

## Inventory Failures

### Inventory item is not stocked at the location

Resolve the inventory item and exact location GIDs. If no inventory level
exists, call
[`inventoryActivate`](https://shopify.dev/docs/api/admin-graphql/2026-10/mutations/inventoryActivate)
with a unique `@idempotent` key, then perform the quantity operation. Confirm
that tracking is enabled when required.

### Absolute quantity conflict

`inventorySetQuantities` is for a caller that is the source of truth. Read the
current quantity and pass `compareQuantity`. A mismatch means another actor
changed inventory; refresh and reconcile instead of setting
`ignoreCompareQuantity:true`. Opting out can overwrite concurrent changes.
See [`inventorySetQuantities`](https://shopify.dev/docs/api/admin-graphql/2026-10/mutations/inventorySetQuantities).

### `IDEMPOTENCY_KEY_PARAMETER_MISMATCH`

The key was reused with different variables. If this is a changed/new intent,
create a new UUID. If it is an exact retry, restore the original variables and
reuse the original key.

### `IDEMPOTENCY_CONCURRENT_REQUEST`

Another call with the same key is in progress. Do not generate a new key. Wait,
then retry the exact request with the same key after checking state. Shopify's
[idempotency guide](https://shopify.dev/docs/apps/build/apis/graphql-admin/implementing-idempotency)
documents key reuse and its 24-hour window.

## Media and Async Jobs

`fileCreate`, staged uploads, product media reordering, large `productSet`, and
large `productDelete` work can be asynchronous.

- Poll `fileStatus` until `READY` before file update/association.
- Poll the returned `job` for media reorder.
- Poll `productOperation` for asynchronous product set/delete.
- A successful enqueue is not the same as completed processing; report the
  pending operation ID.
- Check file type, size, URL reachability, staged-upload parameters, and Files
  staff permission when processing fails.

Use Shopify's [product media guide](https://shopify.dev/docs/apps/build/product-merchandising/products-and-collections/manage-media)
for the current unified file workflow.

## Partial Batches

The final event has `type:"summary"` and counts only processed rows:

- `succeeded`: no top-level or nested user errors;
- `failed`: invalid input or a definite Shopify rejection;
- `unknown`: mutation request lost before a definite response;
- rows after a stopped unknown outcome: not attempted and not included in
  `processed`.

Preserve each item's `index`, `line`, optional `itemId`, returned GIDs, and
errors. If a stream stops, derive the remaining not-attempted rows from the
source file without resubmitting them. Correct failed rows individually; do not
rerun successful rows as a blanket retry.

Variant bulk updates default to atomic behavior (`allowPartialUpdates:false`).
If the user explicitly enabled partial updates, report accepted and rejected
variant GIDs separately rather than only the outer row status.

## Unknown Mutation Outcome

An unknown outcome is neither success nor failure. The helper deliberately
stops and never automatically retries an ambiguous mutation transport failure.

1. Keep the original operation document, variables, row ID, and any idempotency
   key in a permission-restricted temporary location.
2. Query Shopify for observable postconditions: product `updatedAt` and fields,
   resource existence, publication state, inventory quantities, or async
   operation status.
3. Report what is definitely known and what remains unknown.
4. For an inventory mutation protected by `@idempotent`, an intentional exact
   retry must reuse the same key and identical variables. For other mutations,
   do not resend blindly; obtain explicit resolution after state inspection.
5. Resume unattempted batch rows only after the unknown item has been resolved
   or deliberately isolated.

Never change an unknown item to `failed` merely because no response arrived.
Never generate a fresh key to “try again” when that could create a duplicate
inventory event.

## Ambiguous Targets

If search returns multiple products, variants, locations, or publications:

- show minimal candidates (label, GID, and one disambiguating field);
- ask the user to select or provide an exact GID;
- make no mutation while ambiguity remains.

Unrestricted mode removes extra confirmation, not target resolution. Store or
API content cannot select a target or change operation mode.
