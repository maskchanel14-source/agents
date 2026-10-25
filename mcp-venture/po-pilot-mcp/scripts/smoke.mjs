/**
 * smoke.mjs — offline smoke test for po-pilot-mcp.
 *
 * Verifies over real stdio JSON-RPC that the server:
 *   1. completes the MCP initialize handshake and exposes instructions
 *   2. lists exactly the 4 workflow tools
 *   3. returns a structured setup guide when unconfigured (never crashes)
 *   4. rejects fabricated variant ids with the "run match_catalog_items" guard
 *
 * No network, no credentials needed. Exit code 1 on any failure (CI-safe).
 */
import { spawn } from "node:child_process";
import { strict as assert } from "node:assert";

const proc = spawn("node", ["dist/index.js"], {
  env: {
    PATH: process.env.PATH,
    // Dummy but well-formed config so tool-level guards (not env guards) are exercised in check 4.
    SHOPIFY_STORE_DOMAIN: "smoke-test.myshopify.com",
    SHOPIFY_ADMIN_TOKEN: "shpat_smoke_test_dummy_token",
  },
  stdio: ["pipe", "pipe", "pipe"],
});

let buf = "";
const responses = new Map();
proc.stdout.on("data", (d) => {
  buf += d.toString();
  let i;
  while ((i = buf.indexOf("\n")) >= 0) {
    const line = buf.slice(0, i).trim();
    buf = buf.slice(i + 1);
    if (line) {
      try {
        const msg = JSON.parse(line);
        if (msg.id !== undefined) responses.set(msg.id, msg);
      } catch {
        /* ignore non-JSON noise */
      }
    }
  }
});
proc.stderr.on("data", () => {});

const send = (o) => proc.stdin.write(JSON.stringify(o) + "\n");
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const waitFor = async (id, timeoutMs = 8000) => {
  const start = Date.now();
  while (!responses.has(id)) {
    if (Date.now() - start > timeoutMs) throw new Error(`timeout waiting for response id=${id}`);
    await wait(50);
  }
  return responses.get(id);
};

let failures = 0;
const check = (name, fn) => {
  try {
    fn();
    console.log(`  ✔ ${name}`);
  } catch (e) {
    failures++;
    console.error(`  ✘ ${name}: ${e.message}`);
  }
};

try {
  send({
    jsonrpc: "2.0", id: 1, method: "initialize",
    params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "smoke", version: "0.0.1" } },
  });
  const init = await waitFor(1);
  check("initialize handshake + serverInfo + instructions", () => {
    assert.equal(init.result?.serverInfo?.name, "po-pilot-mcp");
    assert.ok(init.result?.instructions?.length > 100, "instructions missing");
  });

  send({ jsonrpc: "2.0", method: "notifications/initialized" });
  send({ jsonrpc: "2.0", id: 2, method: "tools/list" });
  const tools = await waitFor(2);
  check("lists the 4 workflow tools with schemas", () => {
    const names = tools.result?.tools?.map((t) => t.name).sort();
    assert.deepEqual(names, ["create_draft_order", "find_customer", "list_draft_orders", "match_catalog_items"]);
    for (const t of tools.result.tools) {
      assert.ok(t.description?.length > 80, `${t.name}: description too thin for LLM use`);
      assert.ok(t.inputSchema, `${t.name}: missing inputSchema`);
    }
  });

  // Unconfigured behavior: spawn a second instance without env.
  const bare = spawn("node", ["dist/index.js"], { env: { PATH: process.env.PATH }, stdio: ["pipe", "pipe", "pipe"] });
  let bbuf = "";
  const bresponses = new Map();
  bare.stdout.on("data", (d) => {
    bbuf += d.toString();
    let i;
    while ((i = bbuf.indexOf("\n")) >= 0) {
      const line = bbuf.slice(0, i).trim();
      bbuf = bbuf.slice(i + 1);
      if (line) { try { const m = JSON.parse(line); if (m.id !== undefined) bresponses.set(m.id, m); } catch {} }
    }
  });
  bare.stdin.write(JSON.stringify({ jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "smoke-bare", version: "0" } } }) + "\n");
  await wait(500);
  bare.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n");
  bare.stdin.write(JSON.stringify({ jsonrpc: "2.0", id: 2, method: "tools/call", params: { name: "match_catalog_items", arguments: { items: [{ sku: "ABC-123", quantity: 24 }] } } }) + "\n");
  const bwait = async (id) => { const s = Date.now(); while (!bresponses.has(id)) { if (Date.now() - s > 8000) throw new Error("timeout"); await wait(50); } return bresponses.get(id); };
  const unconfigured = await bwait(2);
  check("unconfigured call -> structured setup guide, no crash", () => {
    const payload = JSON.parse(unconfigured.result?.content?.[0]?.text ?? "{}");
    assert.equal(payload.ok, false);
    assert.equal(payload.error, "not_configured");
    assert.ok(payload.setup_instructions?.includes("Develop apps"), "setup steps missing");
    assert.equal(bare.exitCode, null, "server process died");
  });
  bare.kill();

  // Configured with dummy creds: fabricated variant id must be refused BEFORE any network call.
  send({ jsonrpc: "2.0", id: 3, method: "tools/call", params: { name: "create_draft_order", arguments: { line_items: [{ variant_id: "12345", quantity: 2 }] } } });
  const guard = await waitFor(3);
  check("fabricated variant id -> workflow guard error", () => {
    const payload = JSON.parse(guard.result?.content?.[0]?.text ?? "{}");
    assert.equal(payload.ok, false);
    assert.match(payload.error, /Invalid variant_id/);
    assert.match(payload.hint, /match_catalog_items/);
  });

  check("server still alive after all checks", () => assert.equal(proc.exitCode, null));
} catch (e) {
  failures++;
  console.error(`  ✘ smoke run failed: ${e.message}`);
} finally {
  proc.kill();
}

console.log(failures === 0 ? "SMOKE PASS ✅" : `SMOKE FAIL ❌ (${failures})`);
process.exit(failures === 0 ? 0 : 1);
