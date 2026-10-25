/**
 * shopify.ts — minimal, dependency-free Shopify Admin GraphQL client.
 *
 * Design rules (po-pilot):
 *  - NEVER throw at the tool layer: every failure comes back as
 *    { ok: false, error, hint } so the LLM can recover gracefully.
 *  - No secrets logged, no data stored. Token is used per-request only.
 */

export interface ShopifyEnv {
  /** e.g. "my-store.myshopify.com" */
  domain: string;
  /** Admin API access token from a custom app (starts with "shpat_") */
  token: string;
  /** Admin GraphQL API version */
  apiVersion: string;
  /** Default wholesale discount % off catalog price (0 = off) */
  discountPct: number;
  /** Tags applied to every draft order created by PO Pilot */
  defaultTags: string[];
}

const SETUP_STEPS = [
  "PO Pilot is not configured yet. One-time setup, ~60 seconds, no OAuth, no app review:",
  "1. Shopify Admin -> Settings -> Apps and sales channels -> Develop apps -> Create app (name it 'PO Pilot').",
  "2. In the app: Configuration -> Admin API integration -> grant these scopes ONLY:",
  "   read_products, read_customers, read_draft_orders, write_draft_orders -> Save.",
  "3. API credentials tab -> Install app -> Admin API access token -> Reveal token once -> copy it (starts with 'shpat_').",
  "4. Set these env vars wherever you run this server (Claude Desktop config / Claude Code / MCPize):",
  "   SHOPIFY_STORE_DOMAIN=your-store.myshopify.com",
  "   SHOPIFY_ADMIN_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxx",
  "Optional: PO_PILOT_DISCOUNT_PCT=40 (default wholesale discount), PO_PILOT_TAGS=wholesale,b2b, PO_PILOT_API_VERSION=2026-10.",
].join("\n");

/** Read + validate configuration from environment. Never throws. */
export function getEnv(): { env?: ShopifyEnv; setupError?: string } {
  const domain = (process.env.SHOPIFY_STORE_DOMAIN ?? "")
    .trim()
    .replace(/^https?:\/\//, "")
    .replace(/\/+$/, "");
  const token = (process.env.SHOPIFY_ADMIN_TOKEN ?? "").trim();

  if (!domain || !token) {
    return { setupError: SETUP_STEPS };
  }
  if (!/^[a-z0-9-]+\.myshopify\.com$/i.test(domain) && !domain.includes(".")) {
    return {
      setupError:
        `SHOPIFY_STORE_DOMAIN="${domain}" does not look like a store domain.\n` +
        "Use the full domain, e.g. your-store.myshopify.com (find it in Shopify Admin -> Settings -> Domains).\n\n" +
        SETUP_STEPS,
    };
  }
  if (!token.startsWith("shpat_")) {
    return {
      setupError:
        "SHOPIFY_ADMIN_TOKEN should start with 'shpat_' (Admin API access token from a custom app).\n" +
        "If you pasted an API key or password instead, regenerate it.\n\n" +
        SETUP_STEPS,
    };
  }

  const discountPct = Math.min(
    99,
    Math.max(0, Number.parseFloat(process.env.PO_PILOT_DISCOUNT_PCT ?? "0") || 0),
  );
  const defaultTags = (process.env.PO_PILOT_TAGS ?? "wholesale")
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);

  return {
    env: {
      domain,
      token,
      apiVersion: (process.env.PO_PILOT_API_VERSION ?? "2026-10").trim(),
      discountPct,
      defaultTags,
    },
  };
}

export type GqlResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string; hint?: string };

/**
 * Execute one Admin GraphQL request. Returns structured errors instead of
 * throwing so tools can always respond with actionable guidance.
 */
export async function gql<T>(
  env: ShopifyEnv,
  query: string,
  variables?: Record<string, unknown>,
): Promise<GqlResult<T>> {
  const url = `https://${env.domain}/admin/api/${env.apiVersion}/graphql.json`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": env.token,
      },
      body: JSON.stringify({ query, variables }),
      signal: AbortSignal.timeout(30_000),
    });

    if (res.status === 401 || res.status === 403) {
      return {
        ok: false,
        error: `Shopify rejected the access token (HTTP ${res.status}).`,
        hint: "Token may be revoked, or missing scopes: read_products, read_customers, read_draft_orders, write_draft_orders. Reinstall the custom app and copy a fresh token.",
      };
    }
    if (res.status === 404) {
      return {
        ok: false,
        error: `Store or API version not found (HTTP 404) for ${url}`,
        hint: "Check SHOPIFY_STORE_DOMAIN (must be the .myshopify.com domain) and PO_PILOT_API_VERSION (try 2026-10 or 2025-10).",
      };
    }
    if (res.status === 429) {
      return {
        ok: false,
        error: "Shopify rate limit hit (HTTP 429).",
        hint: "Wait a few seconds and retry. Batch items into a single match_catalog_items call instead of one call per line.",
      };
    }
    if (!res.ok) {
      const body = (await res.text()).slice(0, 300);
      return { ok: false, error: `HTTP ${res.status}: ${body}`, hint: "Unexpected Shopify response. Verify store domain and token." };
    }

    const json = (await res.json()) as {
      data?: T;
      errors?: Array<{ message: string; extensions?: { code?: string } }>;
    };

    if (json.errors && json.errors.length > 0) {
      const msg = json.errors.map((e) => e.message).join("; ").slice(0, 500);
      return {
        ok: false,
        error: `GraphQL error: ${msg}`,
        hint: msg.includes("access denied") || msg.includes("requires access")
          ? "The custom app token lacks a required scope. Add read_products, read_customers, read_draft_orders, write_draft_orders in the app's Admin API integration settings, then reinstall."
          : "Check the request shape against the Admin GraphQL 2026-10 reference.",
      };
    }
    if (!json.data) {
      return { ok: false, error: "Shopify returned an empty response body." };
    }
    return { ok: true, data: json.data };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return {
      ok: false,
      error: `Network error contacting Shopify: ${msg}`,
      hint: "Check internet access and that SHOPIFY_STORE_DOMAIN is spelled exactly like your .myshopify.com domain (no https://, no trailing slash).",
    };
  }
}

/** Normalize a PO number into a safe, searchable tag slug: "PO #A-102/x" -> "po-A-102-X" */
export function poTag(poNumber: string): string {
  const slug = poNumber
    .trim()
    .toUpperCase()
    .replace(/[^A-Z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40);
  return `po-${slug || "UNKNOWN"}`;
}

/** JSON tool-response helper: keeps every tool output machine-readable. */
export function asText(payload: unknown): { content: Array<{ type: "text"; text: string }> } {
  return { content: [{ type: "text", text: JSON.stringify(payload, null, 2) }] };
}
