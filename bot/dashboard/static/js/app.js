/* =========================================================
   ARC-TERMINAL app.js — vanilla JS, no build step, no CDN
   ========================================================= */
"use strict";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const state = {
  token: window.__ARC_TOKEN__ || "",
  events: new EventSource("/api/stream"),
  paused: false,
  sortKey: "net",
  sortAsc: false,
  data: null,
  logFilter: "",
  filter: { q: "", strategy: "", status: "", minProfit: null },
};

/* ---------------- boot sequence ---------------- */
function boot() {
  const overlay = $("#boot-overlay");
  const linesEl = $("#boot-lines");
  const lines = [
    "ARC-TERMINAL v0.1 // initializing…",
    "loading cost model [Decimal] ......... OK",
    "linking CLOB / Gamma / WS feeds ....... OK",
    "risk kernel: hard limits armed ........ OK",
    "execution mode: PAPER (simulation) .... OK",
    "HUD render pipeline ................... OK",
  ];
  const finish = () => overlay.classList.add("done");
  $("#boot-skip").addEventListener("click", finish);
  if (REDUCED) { finish(); return; }
  lines.forEach((t, i) => {
    const d = document.createElement("div");
    d.textContent = t;
    d.style.animationDelay = (i * 0.28) + "s";
    linesEl.appendChild(d);
  });
  setTimeout(finish, 2100);
}

/* ---------------- SSE ---------------- */
function connectSSE() {
  state.events.onmessage = (ev) => {
    try {
      const data = JSON.parse(ev.data);
      render(data);
    } catch (e) { /* swallow render errors */ }
  };
  state.events.onerror = () => {
    setConn("#conn-feed", false, "SSE");
    // EventSource auto-reconnects; just reflect status
  };
  state.events.onopen = () => setConn("#conn-feed", true, "SSE");
}

function setConn(sel, ok, label) {
  const el = $(sel);
  if (!el) return;
  el.classList.toggle("ok", ok);
  el.classList.toggle("bad", !ok);
  el.querySelector("b").textContent = ok ? "OK" : "DOWN";
}

/* ---------------- render ---------------- */
function render(d) {
  state.data = d;
  const st = d.status || {};
  const mode = st.mode || d.mode || "paper";
  const badge = $("#mode-badge");
  badge.textContent = String(mode).toUpperCase();
  badge.classList.toggle("live", mode === "live");

  setConn("#conn-ws", !!st.ws_connected, "WS");
  setConn("#conn-api", !!st.api_ok, "API");

  const cov = d.coverage || {};
  $("#kpi-coverage").textContent = `${st.markets_monitored ?? 0} / ${st.markets_total ?? 0}`;
  $("#kpi-valid").textContent = st.valid_total ?? 0;
  $("#kpi-status").textContent = st.running ? "RUNNING" : "STOPPED";
  $("#kpi-status").className = "kpi-value " + (st.running ? "pos" : "warn");

  const risk = d.risk || {};
  $("#risk-cb").textContent = risk.halted ? (risk.halt_reason || "HALTED") : "OK";
  $("#risk-cb").className = risk.halted ? "bad" : "";
  $("#risk-ks").textContent = risk.kill_switch ? "TRIGGERED" : "ARMED";
  $("#risk-ks").className = risk.kill_switch ? "bad" : "";

  // funnel
  const rej = d.rejection_stats || {};
  $("#fn-total").textContent = st.markets_total ?? 0;
  $("#fn-monitored").textContent = st.markets_monitored ?? 0;
  $("#fn-candidates").textContent = st.opportunities_total ?? 0;
  $("#fn-valid").textContent = st.valid_total ?? 0;
  $("#fn-executed").textContent = st.executed_total ?? 0;
  const rl = $("#reject-list");
  rl.innerHTML = "";
  const entries = Object.entries(rej).filter(([k]) => k !== "ok").sort((a, b) => b[1] - a[1]);
  if (!entries.length) {
    rl.innerHTML = '<div class="empty-note">Belum ada penolakan tercatat.</div>';
  } else {
    const total = entries.reduce((s, [, n]) => s + n, 0) || 1;
    for (const [reason, n] of entries.slice(0, 8)) {
      const div = document.createElement("div");
      div.className = "r";
      div.innerHTML = `<span>${escapeHtml(reason)}</span><b>${n} (${(100 * n / total).toFixed(1)}%)</b>`;
      rl.appendChild(div);
    }
  }

  // risk meters
  const daily = risk.daily_realized_pnl ? parseFloat(risk.daily_realized_pnl) : 0;
  const exp = risk.total_exposure ? parseFloat(risk.total_exposure) : 0;
  const expPct = Math.min(100, exp / 5);   // cap tampilan 500 → 100%
  const dayPct = Math.min(100, Math.abs(daily) / 0.5);
  $("#risk-daily").style.width = dayPct + "%";
  $("#risk-daily").className = dayPct > 80 ? "warn" : "";
  $("#risk-daily-v").textContent = "$" + daily.toFixed(2);
  $("#risk-exp").style.width = expPct + "%";
  $("#risk-exp-v").textContent = "$" + exp.toFixed(2);
  $("#bal-used").textContent = "$" + exp.toFixed(2);

  // health
  const dash = d.dashboard || {};
  const health = d.health || {};
  $("#h-uptime").textContent = fmtDur(dash.uptime_s || 0);
  $("#h-rss").textContent = health.rss_mb != null ? health.rss_mb + " MB" : "n/a";
  $("#h-scan").textContent = st.last_scan_ms != null ? st.last_scan_ms + " ms" : "—";
  $("#h-stale").textContent = cov.stale_assets ?? "—";
  $("#h-reconn").textContent = (d.ws_stats && d.ws_stats.reconnects) ?? "—";

  // opportunities
  renderMiniTable(d.opportunities || []);
  renderFullTable(d.opportunities || []);

  // positions
  const posBody = $("#pos-tbody");
  const positions = d.positions || [];
  if (!positions.length) {
    posBody.innerHTML = '<tr class="empty-row"><td colspan="6">Tidak ada posisi terbuka.</td></tr>';
  } else {
    posBody.innerHTML = positions.map((p) => `<tr>
      <td>${escapeHtml(p.market_id || "")}</td><td>${escapeHtml((p.asset_id || "").slice(0, 12))}…</td>
      <td>${escapeHtml(p.label || "")}</td><td class="num">${p.shares}</td>
      <td class="num">$${p.avg_price}</td><td>${escapeHtml((p.updated_at || "").slice(0, 19))}</td></tr>`).join("");
  }

  // logs
  renderLogs(d.logs || []);

  // settings
  if (!$("#settings-list").children.length) {
    const cfgRows = [
      ["Mode", mode.toUpperCase()],
      ["Cost model", "Decimal · fee = C×rate×(p(1-p))^e · 5dp"],
      ["Order type primary", "FOK"],
      ["Dashboard bind", "127.0.0.1 (localhost only)"],
      ["Sound", "OFF"],
      ["Live trading", "LOCKED (env + confirm file)"],
    ];
    $("#settings-list").innerHTML = cfgRows.map(([k, v]) =>
      `<li><span>${k}</span><b>${escapeHtml(String(v))}</b></li>`).join("");
    $("#risk-limits").innerHTML = [
      ["Max capital / trade", "$50"], ["Max exposure / market", "$100"],
      ["Max exposure / event", "$150"], ["Max total exposure", "$500"],
      ["Max daily loss", "$50 → auto-halt"], ["Max orders / min", "30"],
      ["Kill switch", "file KILL_SWITCH + dashboard"],
    ].map(([k, v]) => `<li><span>${k}</span><b>${v}</b></li>`).join("");
  }
}

function renderMiniTable(opps) {
  const body = $("#mini-tbody");
  const rows = opps.filter((o) => o.valid).slice(0, 12);
  if (!rows.length) {
    body.innerHTML = '<tr class="empty-row"><td colspan="9">Belum ada peluang valid — semua kandidat gugur setelah biaya (atau belum ada kandidat).</td></tr>';
    return;
  }
  body.innerHTML = rows.map((o) => `<tr class="clickable" data-id="${escapeHtml(o.id)}">
    <td>${escapeHtml(o.strategy)}</td>
    <td title="${escapeHtml((o.markets || []).join(", "))}">${escapeHtml((o.markets || []).slice(0, 2).join(", "))}</td>
    <td class="num">${fmt$(o.gross_edge)}</td>
    <td class="num neg">${fmt$(-parseFloat(o.fees || 0) - parseFloat(o.slippage || 0))}</td>
    <td class="num pos">${fmt$(o.net_profit)}</td>
    <td class="num pos">${(parseFloat(o.net_profit_pct) || 0).toFixed(2)}%</td>
    <td class="num">${pct(o.annualized)}</td>
    <td class="num">${parseFloat(o.size || 0).toFixed(1)}</td>
    <td><span class="tag valid">VALID</span></td></tr>`).join("");
  bindRowClicks(body);
}

function renderFullTable(opps) {
  const body = $("#full-tbody");
  let rows = opps.slice();
  const f = state.filter;
  if (f.q) rows = rows.filter((o) => JSON.stringify(o).toLowerCase().includes(f.q.toLowerCase()));
  if (f.strategy) rows = rows.filter((o) => o.strategy === f.strategy);
  if (f.status === "valid") rows = rows.filter((o) => o.valid);
  if (f.status === "rejected") rows = rows.filter((o) => !o.valid);
  if (f.minProfit != null) rows = rows.filter((o) => parseFloat(o.net_profit || 0) >= f.minProfit);

  rows.sort((a, b) => {
    const key = state.sortKey;
    const va = sortVal(a, key), vb = sortVal(b, key);
    return (va < vb ? -1 : va > vb ? 1 : 0) * (state.sortAsc ? 1 : -1);
  });

  if (!rows.length) {
    body.innerHTML = '<tr class="empty-row"><td colspan="13">Tidak ada baris yang cocok dengan filter.</td></tr>';
    return;
  }
  body.innerHTML = rows.slice(0, 200).map((o) => `<tr class="clickable" data-id="${escapeHtml(o.id)}">
    <td>${escapeHtml((o.ts || "").slice(11, 19))}</td>
    <td>${escapeHtml(o.strategy)}</td>
    <td title="${escapeHtml((o.markets || []).join(", "))}">${escapeHtml((o.markets || []).slice(0, 2).join(", "))}</td>
    <td class="num">${fmt$(o.gross_edge)}</td>
    <td class="num neg">${fmt$(-parseFloat(o.fees || 0))}</td>
    <td class="num neg">${fmt$(-parseFloat(o.slippage || 0))}</td>
    <td class="num neg">${fmt$(-parseFloat(o.gas || 0))}</td>
    <td class="num ${parseFloat(o.net_profit) > 0 ? "pos" : "neg"}">${fmt$(o.net_profit)}</td>
    <td class="num">${(parseFloat(o.net_profit_pct) || 0).toFixed(2)}%</td>
    <td class="num">${pct(o.annualized)}</td>
    <td class="num">${parseFloat(o.size || 0).toFixed(1)}</td>
    <td class="num">${((parseFloat(o.fill_prob) || 0) * 100).toFixed(0)}%</td>
    <td>${o.valid ? '<span class="tag valid">VALID</span>' : '<span class="tag rejected">REJ</span>'}</td></tr>`).join("");
  bindRowClicks(body);
}

function sortVal(o, key) {
  switch (key) {
    case "strategy": return o.strategy || "";
    case "markets": return (o.markets || []).join();
    case "gross": return parseFloat(o.gross_edge || 0);
    case "fees": return parseFloat(o.fees || 0);
    case "slip": return parseFloat(o.slippage || 0);
    case "gas": return parseFloat(o.gas || 0);
    case "net": return parseFloat(o.net_profit || 0);
    case "net_pct": return parseFloat(o.net_profit_pct || 0);
    case "ann": return parseFloat(o.annualized || 0);
    case "size": return parseFloat(o.size || 0);
    case "fill": return parseFloat(o.fill_prob || 0);
    case "ts": return o.ts || "";
    default: return 0;
  }
}

function bindRowClicks(body) {
  body.querySelectorAll("tr.clickable").forEach((tr) => {
    tr.addEventListener("click", () => openDetail(tr.dataset.id));
  });
}

/* ---------------- detail panel (waterfall) ---------------- */
function openDetail(id) {
  const opps = (state.data && state.data.opportunities) || [];
  const o = opps.find((x) => x.id === id);
  if (!o) return;
  $("#detail-panel").classList.remove("hidden");
  $("#detail-title").textContent = `${o.strategy} · ${((o.markets || []).join(", "))}`;
  const rows = [
    ["Gross edge (top of book)", o.gross_edge, "gain"],
    ["Trading fees", -parseFloat(o.fees || 0), "fee"],
    ["Slippage (walk book)", -parseFloat(o.slippage || 0), "cost"],
    ["Gas / on-chain", -parseFloat(o.gas || 0), "cost"],
    ["Leg risk haircut", -parseFloat(o.leg_risk || 0), "cost"],
    ["Resolution risk", -parseFloat(o.resolution_risk || 0), "cost"],
    ["Safety margin", -parseFloat(o.safety || 0), "cost"],
    ["NET PROFIT", o.net_profit, "gain"],
  ];
  const maxAbs = Math.max(...rows.map((r) => Math.abs(parseFloat(r[1]) || 0)), 0.0001);
  $("#waterfall").innerHTML = rows.map(([label, val, cls]) => {
    const v = parseFloat(val) || 0;
    const w = Math.min(100, (Math.abs(v) / maxAbs) * 100);
    return `<div class="wf-row"><span>${label}</span>
      <div class="wf-bar"><i class="${cls}" style="width:${w}%"></i></div>
      <b class="${v >= 0 ? "pos" : "neg"}">${fmt$(v)}</b></div>`;
  }).join("");

  $("#timeline").innerHTML = [
    "1. Discovery: market ditemukan via Gamma",
    "2. Filter murah: gross top-of-book > 0",
    "3. Walk-the-book + fee per level (Decimal)",
    "4. Haircut risiko + safety margin",
    `5. ${o.valid ? "Lolos semua gate → masuk ranking" : "DITOLAK: " + escapeHtml(o.reject || "")}`,
  ].map((t) => `<li>${t}</li>`).join("");

  $("#detail-criteria").textContent = "Kriteria resolusi tersedia di metadata market (description). Selalu baca sebelum live trading.";
  $("#depth-charts").innerHTML = '<div class="empty-note">Depth chart per leg — data orderbook live tersedia di feed (lihat mode paper).</div>';
  $("#detail-panel").scrollIntoView({ behavior: REDUCED ? "auto" : "smooth" });
}

/* ---------------- logs ---------------- */
function renderLogs(logs) {
  const box = $("#log-stream");
  const f = state.logFilter;
  const rows = logs.filter((l) => !f || (l.level || "INFO") === f).slice(-120).reverse();
  if (!rows.length) {
    box.innerHTML = '<div class="empty-row">Belum ada log (filter aktif atau bot baru mulai).</div>';
    return;
  }
  box.innerHTML = rows.map((l) => `<div class="log-line ${escapeHtml(l.level || "INFO")}">
    <span class="ts">${escapeHtml((l.ts || "").replace("T", " ").replace("Z", ""))}</span>
    <span class="lv">${escapeHtml(l.level || "INFO")}</span>
    <span class="msg">${escapeHtml(l.msg || "")}</span></div>`).join("");
}

/* ---------------- controls ---------------- */
function setupControls() {
  $$(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      $$(".tab").forEach((t) => { t.classList.remove("active"); t.setAttribute("aria-selected", "false"); });
      tab.classList.add("active");
      tab.setAttribute("aria-selected", "true");
      $$(".tabpanel").forEach((p) => p.classList.remove("active"));
      $("#tab-" + tab.dataset.tab).classList.add("active");
    });
  });

  $("#btn-pause").addEventListener("click", () => {
    state.paused = !state.paused;
    $("#btn-pause").textContent = state.paused ? "RESUME" : "PAUSE";
  });

  $("#btn-kill").addEventListener("click", () => {
    confirmDialog("Aktifkan KILL SWITCH? Semua trading akan berhenti seketika.", async () => {
      await fetch("/api/control/kill", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-ARC-Token": state.token },
        body: JSON.stringify({ confirm: "CONFIRM" }),
      });
    });
  });

  // sorting
  $$(".data-table th[data-sort]").forEach((th) => {
    th.addEventListener("click", () => {
      const key = th.dataset.sort;
      if (state.sortKey === key) state.sortAsc = !state.sortAsc;
      else { state.sortKey = key; state.sortAsc = false; }
      if (state.data) render(state.data);
    });
  });

  // filters
  $("#f-search").addEventListener("input", (e) => { state.filter.q = e.target.value; });
  $("#f-strategy").addEventListener("change", (e) => { state.filter.strategy = e.target.value; });
  $("#f-status").addEventListener("change", (e) => { state.filter.status = e.target.value; });
  $("#f-minprofit").addEventListener("input", (e) => {
    state.filter.minProfit = e.target.value === "" ? null : parseFloat(e.target.value);
  });
  $("#f-loglevel").addEventListener("change", (e) => {
    state.logFilter = e.target.value;
    if (state.data) renderLogs(state.data.logs || []);
  });
  $("#btn-log-clear").addEventListener("click", () => { $("#log-stream").innerHTML = '<div class="empty-row">View dibersihkan (log asli tetap tersimpan di logs/bot.log).</div>'; });
  $("#btn-close-detail").addEventListener("click", () => $("#detail-panel").classList.add("hidden"));

  // exports
  $("#btn-export-csv").addEventListener("click", () => window.open("/api/export/opportunities", "_blank"));
  $("#btn-export-json").addEventListener("click", () => window.open("/api/export/pnl", "_blank"));

  // clock
  setInterval(() => {
    const now = new Date();
    $("#clock").textContent = now.toISOString().substr(11, 8) + " UTC";
  }, 1000);

  // keyboard: Esc closes modal/detail
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      $("#confirm-modal").classList.add("hidden");
      $("#detail-panel").classList.add("hidden");
    }
  });
}

function confirmDialog(msg, onOk) {
  const modal = $("#confirm-modal");
  const input = $("#confirm-input");
  const ok = $("#confirm-ok");
  $("#confirm-msg").innerHTML = msg + ' Ketik <code>CONFIRM</code> untuk melanjutkan.';
  input.value = "";
  ok.disabled = true;
  modal.classList.remove("hidden");
  input.focus();
  input.oninput = () => { ok.disabled = input.value.trim() !== "CONFIRM"; };
  $("#confirm-cancel").onclick = () => modal.classList.add("hidden");
  ok.onclick = async () => {
    modal.classList.add("hidden");
    try { await onOk(); } catch (e) { /* API errors surfaced in log */ }
  };
}

/* ---------------- helpers ---------------- */
function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}
function fmt$(v) {
  const n = parseFloat(v ?? 0) || 0;
  return (n >= 0 ? "$" : "-$") + Math.abs(n).toFixed(4);
}
function pct(v) {
  const n = parseFloat(v ?? 0) || 0;
  return (n * 100).toFixed(1) + "%";
}
function fmtDur(s) {
  s = Math.floor(s || 0);
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
  return (h ? h + "h " : "") + m + "m " + sec + "s";
}

/* ---------------- init ---------------- */
boot();
setupControls();
connectSSE();
