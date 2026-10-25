#!/usr/bin/env node
/**
 * PO Pilot — MCP server for wholesale purchase-order intake on Shopify.
 *
 * The workflow this server exists for (non-Plus Shopify brands, US wholesalers):
 *   messy emailed PO (PDF/Excel/text)  ->  [LLM reads & extracts]  ->
 *   match_catalog_items (validate SKUs, live prices, inventory, case packs)  ->
 *   find_customer (reuse or create the B2B account)  ->
 *   create_draft_order (PO dedupe, net terms, tags, optional invoice send)  ->
 *   list_draft_orders (net-30 aging: who still hasn't paid)
 *
 * Division of labor is deliberate: the CLIENT LLM does fuzzy extraction from
 * unstructured documents; THIS server does authoritative validation against
 * the live Shopify catalog and the write. That split is the product.
 *
 * Guarantees:
 *  - No tool ever throws or crashes the server; every failure is a structured
 *    { ok:false, error, hint } payload the model can act on.
 *  - Nothing is stored: the Admin token is used per-request, no logs of PO data.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { asText, getEnv, gql, poTag, type ShopifyEnv } from "./shopify.js";

const SERVER = { name: "po-pilot-mcp", version: "0.1.0" };

const INSTRUCTIONS = `PO Pilot turns wholesale purchase orders into validated Shopify draft orders.
Standard workflow: (1) read the customer's PO (email text, pasted CSV, PDF content) yourself and extract line items; (2) call match_catalog_items to validate SKUs/prices/inventory against the live catalog; (3) call find_customer to resolve the buyer; (4) call create_draft_order with the MATCHED variant ids only — resolve 'ambiguous' items with the user first; (5) later, use list_draft_orders to chase unpaid net-terms invoices. Never create a draft order with unmatched or price-mismatched lines without telling the user.`;

// ---------------------------------------------------------------------------
// GraphQL documents (Admin API 2026-10)
// ---------------------------------------------------------------------------

const Q_PRODUCTS = `query PoPilotProducts($q: String!) {
  products(query: $q, first: 5) {
    nodes {
      id
      title
      vendor
      productType
      variants(first: 20) {
        nodes {
          id
          sku
          title
          price
          inventoryQuantity
          selectedOptions { name value }
        }
      }
    }
  }
}`;

const Q_CUSTOMERS = `query PoPilotCustomers($q: String!) {
  customers(query: $q, first: 5) {
    nodes {
      id
      displayName
      email
      phone
      tags
      addresses(first: 2) { nodes { address1 city province zip country } }
    }
  }
}`;

const M_CUSTOMER_CREATE = `mutation PoPilotCustomerCreate($input: CustomerCreateInput!) {
  customerCreate(input: $input) {
    customer { id displayName email }
    userErrors { field message }
  }
}`;

const Q_DRAFTS = `query PoPilotDrafts {
  draftOrders(first: 50, sortKey: CREATED_AT, reverse: true) {
    nodes {
      id
      name
      status
      invoiceUrl
      createdAt
      totalPrice
      email
      tags
      note
      customer { displayName }
    }
  }
}`;

const M_DRAFT_CREATE = `mutation PoPilotDraftCreate($input: DraftOrderInput!) {
  draftOrderCreate(input: $input) {
    draftOrder { id name status invoiceUrl totalPrice createdAt }
    userErrors { field message }
  }
}`;

const M_INVOICE_SEND = `mutation PoPilotInvoiceSend($id: ID!, $email: DraftOrderInvoiceSendInput!) {
  draftOrderInvoiceSend(id: $id, email: $email) {
    draftOrder { invoiceUrl }
    userErrors { field message }
  }
}`;

// ---------------------------------------------------------------------------
// Shared Zod shapes
// ---------------------------------------------------------------------------

const PoLineItem = z.object({
  sku: z.string().optional().describe("SKU printed on the PO, if any. Exact match is attempted first (case-insensitive)."),
  title: z.string().optional().describe("Product name/description as written on the PO. Used for catalog search when SKU is missing or unmatched."),
  variant_title: z.string().optional().describe("Variant hint from the PO, e.g. 'Large / Navy' or '12oz'. Used to disambiguate multi-variant products."),
  quantity: z.number().int().positive().describe("Units ordered. If the PO says '4 cases of 12', convert to 48 before calling."),
  unit_price: z.number().positive().optional().describe("Unit price stated on the PO (if any). Compared against catalog price and the configured wholesale price; mismatches are flagged, never silently accepted."),
  case_pack: z.number().int().positive().optional().describe("Known case-pack size for this product, e.g. 6 or 12. Quantity not divisible by it triggers a warning (a classic wholesale keying error)."),
});

const VariantInfo = z.object({
  variant_id: z.string(),
  product_id: z.string(),
  product_title: z.string(),
  variant_title: z.string(),
  sku: z.string(),
  catalog_price: z.number(),
  suggested_wholesale_price: z.number(),
  inventory_available: z.number(),
  options: z.record(z.string()).optional(),
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function needEnv(): { env?: ShopifyEnv; response?: ReturnType<typeof asText> } {
  const { env, setupError } = getEnv();
  if (!env) return { response: asText({ ok: false, error: "not_configured", setup_instructions: setupError }) };
  return { env };
}

function wholesalePrice(catalogPrice: number, discountPct: number): number {
  return Math.round(catalogPrice * (1 - discountPct / 100) * 100) / 100;
}

interface RawVariant {
  id: string;
  sku: string | null;
  title: string | null;
  price: string;
  inventoryQuantity: number | null;
  selectedOptions: Array<{ name: string; value: string }>;
}
interface RawProduct {
  id: string;
  title: string;
  vendor: string | null;
  productType: string | null;
  variants: { nodes: RawVariant[] };
}

function toVariantInfo(v: RawVariant, p: RawProduct, discountPct: number) {
  const catalogPrice = Number.parseFloat(v.price) || 0;
  return {
    variant_id: v.id,
    product_id: p.id,
    product_title: p.title,
    variant_title: v.title ?? "",
    sku: v.sku ?? "",
    catalog_price: catalogPrice,
    suggested_wholesale_price: wholesalePrice(catalogPrice, discountPct),
    inventory_available: v.inventoryQuantity ?? 0,
    options: Object.fromEntries(v.selectedOptions.map((o) => [o.name, o.value])),
  };
}

// ---------------------------------------------------------------------------
// Server + tools
// ---------------------------------------------------------------------------

const server = new McpServer(SERVER, { instructions: INSTRUCTIONS });

// -- Tool 1: match_catalog_items -------------------------------------------

server.registerTool(
  "match_catalog_items",
  {
    title: "Match PO line items against the live Shopify catalog",
    description:
      "Validates extracted purchase-order lines against the merchant's LIVE Shopify catalog. For each line: finds the exact variant by SKU (or searches by product title), returns its variant_id, catalog price, suggested wholesale price (catalog price minus the configured discount), and on-hand inventory. Flags: price mismatches between the PO and the catalog, quantity above available inventory, quantities not divisible by the case pack, and ambiguous matches (multiple candidate variants — ask the user which one before ordering). ALWAYS call this before create_draft_order; never invent variant ids. Input lines should come from YOU reading the PO document (email text, pasted CSV/Excel content, PDF text) — this tool validates, it does not parse documents.",
    inputSchema: {
      items: z.array(PoLineItem).min(1).max(100).describe("Line items extracted from the purchase order, in PO order."),
    },
  },
  async ({ items }) => {
    const { env, response } = needEnv();
    if (!env) return response!;

    const results: unknown[] = [];
    let matched = 0;
    let needsReview = 0;

    for (let i = 0; i < items.length; i++) {
      const item = items[i]!;
      try {
        const q = item.sku?.trim()
          ? `sku:${item.sku.trim().replace(/["\\]/g, "")}`
          : (item.title ?? "").trim().split(/\s+/).slice(0, 6).join(" ");
        if (!q) {
          results.push({ line: i + 1, status: "error", error: "Provide at least one of: sku, title.", hint: "Re-read the PO line; if it is unreadable, ask the user." });
          needsReview++;
          continue;
        }

        const res = await gql<{ products: { nodes: RawProduct[] } }>(env, Q_PRODUCTS, { q });
        if (!res.ok) {
          results.push({ line: i + 1, status: "error", error: res.error, hint: res.hint });
          needsReview++;
          continue;
        }

        // Collect candidate variants across matched products.
        let candidates: ReturnType<typeof toVariantInfo>[] = [];
        for (const p of res.data.products.nodes) {
          for (const v of p.variants.nodes) candidates.push(toVariantInfo(v, p, env.discountPct));
        }

        // Exact SKU filter when a SKU was given.
        if (item.sku?.trim()) {
          const sku = item.sku.trim().toLowerCase();
          const exact = candidates.filter((c) => c.sku.toLowerCase() === sku);
          if (exact.length > 0) candidates = exact;
        }
        // Variant-title narrowing when a hint was given.
        const hint = item.variant_title?.trim().toLowerCase();
        if (hint && candidates.length > 1) {
          const narrowed = candidates.filter(
            (c) =>
              c.variant_title.toLowerCase().includes(hint) ||
              Object.values(c.options ?? {}).some((ov) => ov.toLowerCase().includes(hint)),
          );
          if (narrowed.length > 0) candidates = narrowed;
        }

        if (candidates.length === 0) {
          results.push({
            line: i + 1,
            status: "not_found",
            searched: q,
            error: `No catalog product matches ${item.sku ? `SKU "${item.sku}"` : `title "${item.title}"`}.`,
            hint: "Ask the user: discontinued item, typo in the PO, or a product not in this store? Do NOT create the draft order line blindly.",
          });
          needsReview++;
          continue;
        }
        if (candidates.length > 1) {
          results.push({
            line: i + 1,
            status: "ambiguous",
            searched: q,
            candidates: candidates.slice(0, 5),
            hint: "Multiple variants match. Present these options to the user (or use a more specific variant_title) and pick exactly one before ordering.",
          });
          needsReview++;
          continue;
        }

        // Exactly one candidate -> matched, now run the trust checks.
        const c = candidates[0]!;
        const warnings: string[] = [];
        if (item.unit_price !== undefined) {
          const expected = env.discountPct > 0 ? c.suggested_wholesale_price : c.catalog_price;
          if (Math.abs(item.unit_price - expected) > 0.01) {
            warnings.push(
              `PRICE MISMATCH: PO says ${item.unit_price.toFixed(2)}, catalog price is ${c.catalog_price.toFixed(2)} (suggested wholesale: ${c.suggested_wholesale_price.toFixed(2)}). Confirm the price with the user before creating the draft order; you can override via line_items[].unit_price in create_draft_order.`,
            );
          }
        }
        if (item.quantity > c.inventory_available) {
          warnings.push(`INVENTORY: PO requests ${item.quantity} units but only ${c.inventory_available} on hand. Draft orders can oversell — confirm with the user.`);
        }
        if (item.case_pack && item.quantity % item.case_pack !== 0) {
          warnings.push(`CASE PACK: quantity ${item.quantity} is not a multiple of case pack ${item.case_pack} — classic case-vs-unit keying error. Double-check the PO.`);
        }
        if (warnings.length > 0) needsReview++;
        else matched++;

        results.push({ line: i + 1, status: "matched", variant: c, warnings });
      } catch (e) {
        results.push({ line: i + 1, status: "error", error: e instanceof Error ? e.message : String(e) });
        needsReview++;
      }
    }

    return asText({
      ok: true,
      summary: { total_lines: items.length, clean_matches: matched, needs_review: needsReview },
      results,
      next_step:
        needsReview === 0
          ? "All lines validated. Next: find_customer, then create_draft_order with these variant_ids."
          : "Resolve every 'ambiguous'/'not_found' line and every warning WITH THE USER first, then proceed.",
    });
  },
);

// -- Tool 2: find_customer ---------------------------------------------------

server.registerTool(
  "find_customer",
  {
    title: "Find (or create) the B2B customer for a purchase order",
    description:
      "Resolves the buyer named on a purchase order to a Shopify customer. Searches by email (exact) or by name/company (partial). Returns customer_id, contact details, tags and recent addresses so create_draft_order can reuse them. With create_if_missing=true and an email provided, creates a minimal customer record when none exists (new wholesale accounts). Privacy: never create customers without the user's OK — default is search-only.",
    inputSchema: {
      query: z.string().min(2).describe("Email address, company name, or contact name exactly as written on the PO."),
      create_if_missing: z.boolean().optional().describe("Create a new Shopify customer when no match is found. Requires 'email'. Default false."),
      email: z.string().email().optional().describe("Email for the new customer (used with create_if_missing, or to refine search)."),
      first_name: z.string().optional().describe("Contact first name (for creation)."),
      last_name: z.string().optional().describe("Contact last name (for creation)."),
      phone: z.string().optional().describe("Phone (for creation)."),
      note: z.string().optional().describe("Internal note, e.g. 'Met at MAGIC trade show, net-30 approved' (for creation)."),
    },
  },
  async (args) => {
    const { env, response } = needEnv();
    if (!env) return response!;
    try {
      const q = (args.email ?? args.query).trim().replace(/["\\]/g, "");
      const res = await gql<{ customers: { nodes: Array<{
        id: string; displayName: string | null; email: string | null; phone: string | null; tags: string[];
        addresses: { nodes: Array<{ address1: string | null; city: string | null; province: string | null; zip: string | null; country: string | null }> };
      }> } }>(env, Q_CUSTOMERS, { q });
      if (!res.ok) return asText({ ok: false, error: res.error, hint: res.hint });

      if (res.data.customers.nodes.length > 0) {
        return asText({
          ok: true,
          found: res.data.customers.nodes.length,
          customers: res.data.customers.nodes.map((c) => ({
            customer_id: c.id,
            display_name: c.displayName,
            email: c.email,
            phone: c.phone,
            tags: c.tags,
            addresses: c.addresses.nodes,
          })),
          next_step: "Pass customer_id to create_draft_order (preferred) or just use the customer's email.",
        });
      }

      if (args.create_if_missing && args.email) {
        const created = await gql<{ customerCreate: { customer: { id: string; displayName: string | null; email: string | null } | null; userErrors: Array<{ field: string[] | null; message: string }> } }>(
          env, M_CUSTOMER_CREATE,
          { input: { email: args.email, firstName: args.first_name, lastName: args.last_name, phone: args.phone, note: args.note, tags: env.defaultTags } },
        );
        if (!created.ok) return asText({ ok: false, error: created.error, hint: created.hint });
        if (created.data.customerCreate.userErrors.length > 0) {
          return asText({ ok: false, error: "customerCreate failed", user_errors: created.data.customerCreate.userErrors });
        }
        return asText({ ok: true, created: true, customer: created.data.customerCreate.customer, next_step: "Now call create_draft_order with this customer_id." });
      }

      return asText({
        ok: true,
        found: 0,
        hint: "No customer matches. Ask the user whether to (a) create the account (call again with create_if_missing=true and email), or (b) create the draft order with just customer_email — Shopify allows email-only drafts.",
      });
    } catch (e) {
      return asText({ ok: false, error: e instanceof Error ? e.message : String(e) });
    }
  },
);

// -- Tool 3: create_draft_order ----------------------------------------------

const TERMS = ["net-15", "net-30", "net-60", "due-on-receipt"] as const;

server.registerTool(
  "create_draft_order",
  {
    title: "Create a Shopify draft order from validated PO lines",
    description:
      "Creates a Shopify draft order (the wholesale standard: review -> invoice -> payment link) from line items ALREADY validated by match_catalog_items. Workflow guardrails built in: (1) PO dedupe — if a draft order with the same po_number tag already exists, creation is refused and the existing draft returned unless allow_duplicate_po=true; (2) net terms — payment_terms is recorded in the note and as a note attribute; (3) tagging — every draft gets the configured tags plus 'po-<NUMBER>' for later tracking; (4) optional invoice send — send_invoice=true emails the invoice/payment link to the buyer and returns the invoice URL. Variant ids MUST come from match_catalog_items. Pass unit_price per line to lock an agreed wholesale price that differs from catalog.",
    inputSchema: {
      line_items: z.array(z.object({
        variant_id: z.string().describe("Shopify variant GID from match_catalog_items, e.g. gid://shopify/ProductVariant/123456789."),
        quantity: z.number().int().positive(),
        unit_price: z.number().positive().optional().describe("Override price per unit (agreed wholesale price). Omit to use catalog price."),
      })).min(1).max(100),
      po_number: z.string().optional().describe("The buyer's PO number, e.g. 'PO-2291'. Used for dedupe + tracking tag. Strongly recommended."),
      customer_id: z.string().optional().describe("Shopify customer GID from find_customer. Preferred over email."),
      customer_email: z.string().email().optional().describe("Buyer email (used when customer_id is absent; required to send an invoice)."),
      payment_terms: z.enum(TERMS).optional().describe("Wholesale payment terms to record on the draft order note. Default: net-30."),
      send_invoice: z.boolean().optional().describe("Immediately email the invoice + payment link to the buyer. Default false (draft stays in admin for review)."),
      tags: z.array(z.string()).optional().describe("Extra tags, e.g. ['trade-show', 'vip']. Merged with defaults."),
      note: z.string().optional().describe("Extra internal note appended to the draft order."),
      allow_duplicate_po: z.boolean().optional().describe("Create anyway even if po_number already exists. Default false."),
      use_customer_default_address: z.boolean().optional().describe("Use the customer's default address for shipping. Default true when customer_id is given."),
    },
  },
  async (args) => {
    const { env, response } = needEnv();
    if (!env) return response!;
    try {
      // Guard: variant ids must be real Shopify GIDs (i.e. came from match_catalog_items).
      const badIds = args.line_items.filter((l) => !/^gid:\/\/shopify\/ProductVariant\/\d+$/.test(l.variant_id));
      if (badIds.length > 0) {
        return asText({
          ok: false,
          error: `Invalid variant_id(s): ${badIds.map((b) => b.variant_id).join(", ")}`,
          hint: "Variant ids must be Shopify GIDs returned by match_catalog_items (gid://shopify/ProductVariant/...). Run match_catalog_items first — never fabricate ids.",
        });
      }

      // Guard: PO dedupe against the last 50 drafts (client-side tag match — reliable, no search-syntax quirks).
      if (args.po_number?.trim() && !args.allow_duplicate_po) {
        const existing = await gql<{ draftOrders: { nodes: Array<{ id: string; name: string; status: string; tags: string[]; createdAt: string; invoiceUrl: string | null }> } }>(env, Q_DRAFTS);
        if (existing.ok) {
          const tag = poTag(args.po_number);
          const dupes = existing.data.draftOrders.nodes.filter((d) => d.tags?.includes(tag));
          if (dupes.length > 0) {
            return asText({
              ok: false,
              error: "duplicate_po",
              message: `PO "${args.po_number}" already has draft order(s) in this store. Refusing to double-key the same order.`,
              existing_drafts: dupes.map((d) => ({ id: d.id, name: d.name, status: d.status, created_at: d.createdAt, invoice_url: d.invoiceUrl })),
              hint: "If this is genuinely a second order with the same PO number, call again with allow_duplicate_po=true.",
            });
          }
        }
        // If the dedupe query itself failed we continue (creation still works); note it for transparency.
      }

      const terms = args.payment_terms ?? "net-30";
      const tags = Array.from(new Set([...env.defaultTags, ...(args.po_number?.trim() ? [poTag(args.po_number)] : []), ...(args.tags ?? [])]));
      const noteLines = [
        `Payment terms: ${terms.toUpperCase()}`,
        args.po_number?.trim() ? `PO number: ${args.po_number.trim()}` : null,
        "Created via PO Pilot MCP (validated against live catalog).",
        args.note?.trim() ? `---\n${args.note.trim()}` : null,
      ].filter(Boolean);

      const input: Record<string, unknown> = {
        lineItems: args.line_items.map((l) => ({
          variantId: l.variant_id,
          quantity: l.quantity,
          ...(l.unit_price !== undefined ? { originalUnitPrice: String(l.unit_price) } : {}),
        })),
        note: noteLines.join("\n"),
        noteAttributes: [
          ...(args.po_number?.trim() ? [{ key: "PO Number", value: args.po_number.trim() }] : []),
          { key: "Payment Terms", value: terms },
        ],
        tags,
      };
      if (args.customer_id) {
        input.customerId = args.customer_id;
        input.useCustomerDefaultAddress = args.use_customer_default_address !== false;
      } else if (args.customer_email) {
        input.email = args.customer_email;
      }

      const res = await gql<{ draftOrderCreate: {
        draftOrder: { id: string; name: string; status: string; invoiceUrl: string | null; totalPrice: string | null; createdAt: string } | null;
        userErrors: Array<{ field: string[] | null; message: string }>;
      } }>(env, M_DRAFT_CREATE, { input });
      if (!res.ok) return asText({ ok: false, error: res.error, hint: res.hint });
      const { draftOrder, userErrors } = res.data.draftOrderCreate;
      if (userErrors.length > 0 || !draftOrder) {
        return asText({
          ok: false,
          error: "Shopify rejected the draft order.",
          user_errors: userErrors,
          hint: "Common causes: variant no longer exists, quantity invalid, or customer_id/email mismatch. Re-run match_catalog_items for stale lines.",
        });
      }

      let invoiceUrl = draftOrder.invoiceUrl;
      let invoice: { sent?: boolean; error?: string } = { sent: false };
      if (args.send_invoice) {
        const to = args.customer_email;
        if (!to) {
          invoice = { sent: false, error: "send_invoice=true but no customer_email provided and the customer record has no email — invoice not sent. Draft order was still created." };
        } else {
          const sent = await gql<{ draftOrderInvoiceSend: { draftOrder: { invoiceUrl: string | null } | null; userErrors: Array<{ field: string[] | null; message: string }> } }>(
            env, M_INVOICE_SEND,
            { id: draftOrder.id, email: { to, subject: `Invoice ${draftOrder.name}${args.po_number ? ` — PO ${args.po_number}` : ""}`, customMessage: `Payment terms: ${terms.toUpperCase()}. Thank you for your order!` } },
          );
          if (sent.ok && sent.data.draftOrderInvoiceSend.draftOrder) {
            invoice = { sent: true };
            invoiceUrl = sent.data.draftOrderInvoiceSend.draftOrder.invoiceUrl ?? invoiceUrl;
          } else {
            invoice = { sent: false, error: sent.ok ? sent.data.draftOrderInvoiceSend.userErrors.map((u) => u.message).join("; ") : sent.error };
          }
        }
      }

      return asText({
        ok: true,
        draft_order: {
          id: draftOrder.id,
          name: draftOrder.name,
          status: draftOrder.status,
          total_price: draftOrder.totalPrice,
          created_at: draftOrder.createdAt,
          payment_terms: terms,
          po_number: args.po_number ?? null,
          tags,
          invoice_url: invoiceUrl,
        },
        invoice,
        next_step: args.send_invoice
          ? "Invoice emailed to the buyer with the payment link. Track payment later with list_draft_orders."
          : `Draft ${draftOrder.name} is waiting in Shopify Admin -> Orders -> Drafts for review. Send the invoice from there, or re-call with send_invoice=true.`,
      });
    } catch (e) {
      return asText({ ok: false, error: e instanceof Error ? e.message : String(e) });
    }
  },
);

// -- Tool 4: list_draft_orders ------------------------------------------------

server.registerTool(
  "list_draft_orders",
  {
    title: "List draft orders + net-terms aging (who hasn't paid)",
    description:
      "Lists the store's 50 most recent draft orders with status, totals, PO tags and invoice URLs, and computes net-terms aging: days_open and an OVERDUE flag for OPEN/INVOICE_SENT drafts whose recorded terms (e.g. NET 30) have elapsed. This replaces the 'who owes me' spreadsheet for net-30/60 wholesale. Filter by status, tag, or PO number. Typical follow-up: for each overdue draft, draft a polite reminder email to the buyer referencing name, total, PO number and days overdue.",
    inputSchema: {
      status: z.enum(["OPEN", "INVOICE_SENT", "COMPLETED"]).optional().describe("Filter by draft order status. Omit for all."),
      tag: z.string().optional().describe("Filter by tag, e.g. 'wholesale' or 'po-2291'."),
      po_number: z.string().optional().describe("Filter by buyer PO number (converted to its tracking tag automatically)."),
      overdue_only: z.boolean().optional().describe("Return only drafts whose recorded net terms have elapsed without completion."),
      days: z.number().int().positive().max(365).optional().describe("Only drafts created within the last N days."),
    },
  },
  async (args) => {
    const { env, response } = needEnv();
    if (!env) return response!;
    try {
      const res = await gql<{ draftOrders: { nodes: Array<{
        id: string; name: string; status: string; invoiceUrl: string | null; createdAt: string;
        totalPrice: string | null; email: string | null; tags: string[] | null; note: string | null;
        customer: { displayName: string | null } | null;
      }> } }>(env, Q_DRAFTS);
      if (!res.ok) return asText({ ok: false, error: res.error, hint: res.hint });

      const wantTag = args.po_number?.trim() ? poTag(args.po_number) : args.tag?.trim();
      const cutoff = args.days ? Date.now() - args.days * 86_400_000 : null;

      const drafts = res.data.draftOrders.nodes
        .filter((d) => !args.status || d.status === args.status)
        .filter((d) => !wantTag || (d.tags ?? []).some((t) => t.toLowerCase() === wantTag.toLowerCase()))
        .filter((d) => !cutoff || Date.parse(d.createdAt) >= cutoff)
        .map((d) => {
          const daysOpen = Math.floor((Date.now() - Date.parse(d.createdAt)) / 86_400_000);
          const termsMatch = /payment terms:\s*net-(\d+)/i.exec(d.note ?? "");
          const netDays = termsMatch ? Number.parseInt(termsMatch[1]!, 10) : null;
          const overdue = netDays !== null && d.status !== "COMPLETED" && daysOpen > netDays;
          return {
            id: d.id,
            name: d.name,
            status: d.status,
            customer: d.customer?.displayName ?? null,
            email: d.email,
            total_price: d.totalPrice,
            created_at: d.createdAt,
            days_open: daysOpen,
            payment_terms: netDays ? `net-${netDays}` : null,
            overdue,
            po_tag: (d.tags ?? []).find((t) => t.startsWith("po-")) ?? null,
            invoice_url: d.invoiceUrl,
          };
        })
        .filter((d) => !args.overdue_only || d.overdue);

      return asText({
        ok: true,
        count: drafts.length,
        draft_orders: drafts,
        ...(args.overdue_only
          ? { next_step: drafts.length > 0 ? "For each overdue draft, write a short polite reminder email: reference name, PO tag, total, days overdue, and attach/mention the invoice_url." : "Nothing overdue. 🎉" }
          : {}),
        note: "Covers the 50 most recent drafts. Drafts stay OPEN/INVOICE_SENT until the buyer pays the invoice; COMPLETED means paid.",
      });
    } catch (e) {
      return asText({ ok: false, error: e instanceof Error ? e.message : String(e) });
    }
  },
);

// ---------------------------------------------------------------------------
// Start (stdio). Top-level guard: configuration problems are reported per
// tool-call (see needEnv), so the server always starts — never crashes.
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`[po-pilot-mcp ${SERVER.version}] ready on stdio (Shopify Admin GraphQL ${getEnv().env?.apiVersion ?? "unconfigured"})`);
}

main().catch((e) => {
  console.error("[po-pilot-mcp] fatal startup error:", e);
  process.exit(1);
});
