# Shopify Access Setup

This guide reflects Shopify's Dev Dashboard flow and Admin GraphQL API `2026-10`
as of 2026-10-16. The plugin is not a native Arena connector. Live access occurs
only after installation in a compatible agent harness with Shopify network
access and credentials configured on that host.

## Required Access

Request these app scopes for complete product management:

```text
write_products,write_inventory,read_locations,write_publications,write_files
```

Shopify write scopes include the corresponding read access, but the person who
installs or operates the app also needs the relevant staff permissions for
products, variants, inventory, publications, and files. App scopes do not
bypass staff permissions.

Official references:

- [Create apps using the Dev Dashboard](https://shopify.dev/docs/apps/build/dev-dashboard/create-apps-using-dev-dashboard)
- [Admin API access scopes](https://shopify.dev/docs/api/usage/access-scopes)
- [Manage app access scopes](https://shopify.dev/docs/apps/build/authentication-authorization/app-installation/manage-access-scopes)

## Create and Install a Dev Dashboard App

New admin-created custom apps are no longer available. Existing admin-created
custom apps continue to work, but a new integration should use the
[Dev Dashboard](https://dev.shopify.com/dashboard/) (or Shopify CLI for a full
public app). See Shopify's [legacy custom-app notice](https://shopify.dev/docs/apps/build/authentication-authorization/legacy/admin-custom-apps).

1. Sign in to the Dev Dashboard with a user who has app-development permission.
2. Open **Apps**, select **Create app**, choose **Start from Dev Dashboard**,
   name the app, and select **Create**.
3. Open **Versions** and create a version. For a non-embedded integration, the
   documented default app URL `https://shopify.dev/apps/default-app-home` is
   sufficient.
4. Add the five scopes listed above. If a webhook API version is requested,
   choose the current appropriate version; the helper independently pins Admin
   GraphQL requests to `2026-10` in the endpoint path.
5. **Release** the version. An app needs a released version before installation.
6. From the app's **Installs** card, select **Install app**, choose the store, and
   approve installation.
7. If scopes change later, release another version and approve the changed
   scopes on every installation; releasing a version alone does not grant them.

## Preferred Authentication: Client Credentials

Use client credentials when the app acts only on stores in the same Shopify
organization as the app. This is the simplest server-to-server flow and does
not require an OAuth callback or redirect handler.

1. Open the app's **Settings** in the Dev Dashboard.
2. Copy its **Client ID** and **Client secret** into the runtime's secret store.
3. Export the values in the harness process, not in chat or a tracked file:

```bash
export SHOPIFY_SHOP="your-store"
export SHOPIFY_CLIENT_ID="your-client-id"
export SHOPIFY_CLIENT_SECRET="replace-with-secret-from-dev-dashboard"
export SHOPIFY_API_VERSION="2026-10"
export SHOPIFY_OPERATION_MODE="unrestricted"
```

`SHOPIFY_SHOP` can be the subdomain (`your-store`) or canonical host
(`your-store.myshopify.com`). Schemes, paths, ports, user information, uppercase
names, and non-Shopify suffixes are rejected before networking. HTTP redirects
are rejected rather than forwarding an authenticated request to another host.

The helper exchanges the client ID and secret in memory at Shopify's token
endpoint and uses the acquired 24-hour token for that invocation. It never
prints the token. Details and same-organization restrictions are in Shopify's
[client credentials guide](https://shopify.dev/docs/apps/build/authentication-authorization/client-credentials-grant).

## Alternate Authentication: Existing Admin Token

The helper also accepts an already-issued OAuth Admin API token or a token from
an existing legacy admin-created custom app:

```bash
export SHOPIFY_SHOP="your-store"
export SHOPIFY_ADMIN_ACCESS_TOKEN="replace-with-an-already-issued-token"
export SHOPIFY_API_VERSION="2026-10"
export SHOPIFY_OPERATION_MODE="unrestricted"
```

Do not set `SHOPIFY_ADMIN_ACCESS_TOKEN` together with either client-credentials
variable. The helper rejects mixed or incomplete authentication strategies.
It does not implement an interactive OAuth authorization flow.

For a store outside the app's Shopify organization, client credentials return
`shop_not_permitted`. Build and install an OAuth-capable app (normally with
Shopify CLI), or use the appropriate public/custom distribution flow, complete
merchant authorization outside this plugin, and provide the resulting offline
Admin API token through `SHOPIFY_ADMIN_ACCESS_TOKEN`. Review Shopify's
[authentication overview](https://shopify.dev/docs/apps/build/authentication-authorization)
and [distribution choices](https://shopify.dev/docs/apps/launch/distribution/select-distribution-method).

## Protect Credentials

- Use a platform secret manager or process environment.
- Never paste credentials into a conversation, GraphQL file, JSON variables,
  JSONL, issue, commit, shell history, or diagnostic output.
- Do not run `env`, `printenv`, `set`, `set -x`, or `echo` on secret variables.
- The shipped `assets/shopify.env.example` contains placeholders only. If you
  create a local env file from it, keep that file untracked and load it before
  starting the agent harness; the helper does not parse `.env` files itself.
- Rotate a secret immediately if it was exposed. For a legacy admin-created app,
  follow Shopify's legacy rotation guidance; do not delete an irreplaceable
  legacy app merely to troubleshoot access.

## Operation Mode

The variable is deliberately separate from authentication:

| Value | Behavior |
| --- | --- |
| `read-only` | Queries work; all mutations are rejected. |
| `safe` or unset | Mutations require the helper's `--confirm-write` flag. |
| `unrestricted` | A clear mutation runs without preview or second confirmation. |

Only the exact value `unrestricted` enables confirmation-free writes. An invalid
value is an error. Unrestricted mode still obeys ambiguity checks, Shopify
scopes and staff permissions, validation, API limits, and throttle signals.

## Validate with Doctor

Resolve the helper relative to the installed skill and run:

```bash
python3 "$SKILL_DIR/scripts/shopify_admin.py" doctor
```

`doctor` performs a read-only query and returns machine-readable JSON containing:

- authenticated shop ID, name, and `myshopify.com` domain;
- requested and resolved API versions, including a mismatch flag;
- granted scopes and any missing required scopes;
- GraphQL errors without credential values.

A healthy report has `"ok":true`, no missing scopes, and matching requested and
resolved versions. A nonzero exit is expected when setup is incomplete. Use
[troubleshooting.md](troubleshooting.md) rather than printing environment values.
