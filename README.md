# Plugins, agents, and skills for AI coding tools

<a id="agentic-plugin-marketplace"></a>
<a id="claude-code-plugins-agents-and-skills"></a>

Use one collection of plugins, agents, skills, and commands across Claude Code, OpenAI Codex CLI, Cursor, OpenCode, Antigravity CLI, GitHub Copilot, and Pi. A harness is the coding tool that loads and runs the components. Plugins cover Python and JavaScript development, code review, testing, infrastructure, security, and other work.

The catalog contains 95 plugins, including 93 local plugins and 2 external entries. The local source contains 202 agents, 187 skills, and 107 commands. The components share a Markdown source, with installation and capabilities adapted to each harness.

## Polymarket Arbitrage Bot ("ARC-TERMINAL")

Repo ini juga memuat **bot arbitrase Polymarket** (package `bot/`): scanner seluruh
market aktif, model biaya presisi (`bot/costs.py`, Decimal, fee resmi
`C × rate × p × (1-p)`), strategi A (intra-market binary), B (multi-outcome /
neg-risk), C/D (gated), risk manager hard-limit, paper executor + dashboard HUD
lokal. Dokumentasi: [`docs/POLYMARKET_NOTES.md`](docs/POLYMARKET_NOTES.md) ·
[`docs/COST_MODEL.md`](docs/COST_MODEL.md) · [`docs/FEASIBILITY.md`](docs/FEASIBILITY.md) ·
[`REPORT.md`](REPORT.md) · [`DECISIONS.md`](DECISIONS.md).

> **Default mode = PAPER (simulasi, TANPA order asli).** Mode live terkunci
> ganda (`LIVE_TRADING=true` + file `live_trading.confirmed`) dan TIDAK boleh
> diaktifkan tanpa review manual. Bot TIDAK berisi mekanisme penghindar geoblock.

### Quick start Windows (CMD)

1. **Instal** [Python 3.11+](https://www.python.org/downloads/) (centang *Add
   python.exe to PATH*) dan [Git](https://git-scm.com/download/win).
2. **Clone** repo ini, lalu buka folder hasil clone di Explorer.
3. **Klik dua kali `start_bot.bat`** — launcher otomatis: cek Python, buat
   `venv\`, install dependency (sekali, pakai marker), dan membuat `.env` dari
   `.env.example` (dibuka di Notepad untuk diisi).
4. Pilih menu **`1` PAPER** — bot mulai, **dashboard "ARC-TERMINAL" terbuka
   otomatis** di `http://127.0.0.1:8788/` (localhost only).
5. Berhenti: `Ctrl+C` di jendela CMD (shutdown bersih) atau `stop_bot.bat`.

Menu `start_bot.bat`: `1` PAPER · `2` BACKTEST · `3` LIVE (butuh ketik `LIVE`) ·
`4` Edit `.env` · `5` Test suite · `6` Rekam data orderbook · `0` Keluar.

Alternatif CLI langsung:

```bat
venv\Scripts\python.exe -m bot --mode paper
venv\Scripts\python.exe -m bot --mode paper --no-dashboard --port 8788
venv\Scripts\python.exe -m bot.backtest.run --sweep
venv\Scripts\python.exe -m pytest tests/ -q
```

### Checklist tes manual Windows (5 menit)

- [ ] `start_bot.bat` dari folder mana pun (klik dua kali) tetap berjalan
- [ ] `venv\` dibuat otomatis; `.env` muncul dari `.env.example`
- [ ] Menu `5` (test) — semua test hijau
- [ ] Menu `1` PAPER — dashboard terbuka di browser, badge **PAPER** hijau
- [ ] Dashboard menampilkan KPI, Scanner, Funnel, Risk (empty state wajar saat bot baru mulai)
- [ ] `Ctrl+C` → bot berhenti tanpa error stack, jendela CMD tidak tertutup sendiri
- [ ] Menu `3` LIVE tanpa ketik `LIVE` → kembali ke menu (tidak jalan)
- [ ] `stop_bot.bat` membuat file `KILL_SWITCH` dan bot berhenti

### Setup wallet untuk LIVE (jangan lakukan sebelum go-live)

1. Buat **hot wallet khusus** (bukan wallet utama), saldo kecil USDC/pUSD di Polygon.
2. Export private key ke `.env` (`POLYMARKET_PRIVATE_KEY`) — **jangan pernah commit**.
3. Buat API key CLOB (L1 EIP-712 via Polymarket) → isi `POLYMARKET_API_KEY/SECRET/PASSPHRASE`.
4. Set `LIVE_TRADING=true` di `.env` **dan** buat file `live_trading.confirmed`
   (isian manual) di root repo. Pahami signature type: `0`=EOA, `1`=Proxy,
   `2`=Safe, `3`=Deposit Wallet (lihat docs/trading/place-orders).
5. Review `config/default.yaml` (risk limits, safety margin, caps) sebelum start.

### Compliance & pembatasan wilayah

Polymarket membatasi beberapa yurisdiksi (market punya flag `restricted` /
geoblock; lihat ToS di polymarket.com). Bot ini **menghormati** pembatasan:
market `restricted` di-skip, dan TIDAK ADA fitur untuk menghindari geoblock
atau pembatasan akun. Pastikan penggunaan sesuai hukum setempat dan ToS
Polymarket. Ringkasan: market geopolitics fee-free; fee taker per kategori
(dokumentasi di `docs/COST_MODEL.md`); resolusi UMA (challenge 2 jam; dispute
4–6 hari) — lihat `docs/POLYMARKET_NOTES.md` §9.

## Multi-harness support

Choose the harness you use and follow its setup route. Available components depend on the installation route and the harness's capabilities.

| Tool | Installation | Components and limits |
|---|---|---|
| [Claude Code](#claude-code) | Plugin marketplace | Source agents, skills, and commands; plugin-specific hooks and MCP configuration |
| [OpenAI Codex CLI](#codex-cli) | Native marketplace or generated artifacts | Native source skills; generated TOML agents and commands as skills use a separate route |
| [Cursor](#cursor) | Plugin marketplace | Source agents, skills, and commands, with curated project rules |
| [OpenCode](#install-from-a-clone) | `make install-opencode` | Generated agents, skills, and commands, with translated tool permissions |
| [Antigravity CLI](#install-from-a-clone) | `make install-antigravity` | Generated plugins containing agents, skills, and commands |
| [GitHub Copilot](#install-from-a-clone) | `make install-copilot` | Generated agent profiles and skills; commands also become invocable skills |
| [Pi](#install-from-a-clone) | `make install-pi` | Generated skills and prompt templates; agents require a subagent extension |

See the [capability matrix](docs/harnesses.md) for model mappings, tool permissions, hooks, and installation differences.

For individual skills, use a [skills-only installer](#skills-only) and select your coding tool.

## Quick start

Choose a plugin for the work you do:

| Plugin | Use it for |
|---|---|
| [python-development](plugins/python-development/) | Python, Django, FastAPI, testing, and packaging |
| [javascript-typescript](plugins/javascript-typescript/) | JavaScript and TypeScript development and project setup |
| [developer-essentials](plugins/developer-essentials/) | Code review, debugging, Git, and testing patterns |
| [security-scanning](plugins/security-scanning/) | Security review, dependency checks, and code scanning |
| [shopify-product-management](plugins/shopify-product-management/) | Chat-controlled Shopify catalog, inventory, media, and publication operations |

See the [plugin catalog](docs/plugins.md) for all 95 plugins and the [usage guide](docs/usage.md) for commands and examples.

### Claude Code

Run these commands inside Claude Code to register the marketplace and install the Python development plugin:

```text
/plugin marketplace add wshobson/agents
/plugin install python-development@claude-code-workflows
```

Then ask Claude to use the Python agents for your task, or run the plugin's scaffolding command:

```text
/python-development:python-scaffold Create a FastAPI service with tests
```

### Codex CLI

Run these commands in a terminal with a current Codex CLI:

```bash
codex plugin marketplace add wshobson/agents
codex plugin add python-development@claude-code-workflows
```

The native Codex manifests expose source skills. The generated TOML agents and command-derived skills use a separate adapter path. Native installation also reads the original skill bodies, while generated copies split oversized bodies into reference files for the 8 KB budget. See the [Codex setup details](docs/harnesses.md#native-install) before choosing an installation route.

### Cursor

Cursor uses the committed [plugin marketplace registry](.cursor-plugin/marketplace.json). Follow the [Cursor setup instructions](docs/harnesses.md#native-install) to add the marketplace and install a plugin.

<a id="skills-only-gh-skill-npx-skills"></a>
<a id="skills-only-gh-skill--npx-skills"></a>

### Skills only

Install an individual skill with GitHub CLI's `gh skill` command or the `npx skills` installer. Select your coding tool when prompted. Both installers read skills from GitHub without cloning the repository and install them without the plugin's agents, commands, or hooks.

```bash
gh skill install wshobson/agents python-testing-patterns
npx skills add wshobson/agents --skill python-testing-patterns
```

`gh skill` requires GitHub CLI 2.90 or later. The `npx` command requires Node.js and npm. See [skills-only installation](docs/harnesses.md#skills-only-installers) for other agents, install scopes, and version pinning.

<a id="codex-cli--cursor--opencode--antigravity-cli--copilot--pi"></a>
<a id="opencode-antigravity-cli-copilot-and-pi"></a>

### Install from a clone

For OpenCode, Antigravity CLI, GitHub Copilot, and Pi, clone the repository and use the installer for your harness. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), Python 3.12 or later, and the coding tool you want to use. The following clone command uses GitHub CLI:

```bash
gh repo clone wshobson/agents ~/agents
cd ~/agents
```

Run the command for your tool. Each target generates the artifacts and links all local plugins into that tool's user configuration:

```bash
make install-opencode
make install-antigravity
make install-copilot
make install-pi
```

Pi's agents require its reference `subagent` extension or a compatible extension. See the [global install guide](docs/harnesses.md#global-install) for configuration paths and uninstall commands.

## What's inside

| Component | Count | Purpose |
|---|---:|---|
| Plugins | 95 | Installable groups of components, including 93 local plugins and 2 external entries |
| Agents | 202 | Instructions for specialist subagents that handle delegated work |
| Skills | 187 | Guidance and reference material that an agent loads when relevant |
| Commands | 107 | Named workflows you invoke, such as project scaffolding or a security scan |

The agent, skill, and command counts cover local source files. External plugins provide their own components and installation requirements.

## How it works

A plugin groups related agents, skills, and commands under `plugins/`. For example, `python-development` contains three agents, sixteen skills, and a scaffolding command. The chosen harness loads the installed components according to its own discovery and invocation rules.

Contributors maintain one Markdown source in the Claude Code plugin format. Native registries point to that source where supported, and adapters generate the formats needed by each harness. Commands may become skills or prompt templates, and agent formats, model choices, and tool permissions vary by harness.

Source agents specify model aliases such as `opus`, `sonnet`, `haiku`, `fable`, or `inherit`. Adapters map those aliases to each harness's model settings, including fixed defaults for some `inherit` entries. See [model configuration](docs/agents.md#model-configuration) and the [adapter mappings](tools/adapters/capabilities.py).

## Quality evaluation

The repository validates plugin structure, generated artifacts, and documentation. Contributors can run these checks from the repository root:

```bash
make generate-all
make validate STRICT=1
make garden
```

[`plugin-eval`](plugins/plugin-eval/) also provides static skill checks without model calls. For example:

```bash
uv run --project plugins/plugin-eval plugin-eval score plugins/python-development/skills/python-testing-patterns --depth quick
```

The LLM judge and Monte Carlo layers are experimental and are not validated against human labels. Their scores describe model assessments and repeated simulations and do not prove that a task succeeds in a project. They require the optional `llm` dependencies. Model calls use `ANTHROPIC_API_KEY` when it is set and bill that API account. Otherwise they use your Claude Code login. See the [evaluation guide](docs/plugin-eval.md) for setup and limits.

## Documentation map

| Guide | Covers |
|---|---|
| [Plugin catalog](docs/plugins.md) | Plugins by task and domain |
| [Agents](docs/agents.md) and [skills](docs/agent-skills.md) | Available components and model configuration |
| [Usage](docs/usage.md) and [tool setup](docs/harnesses.md) | Commands, examples, and installation |
| [Architecture](ARCHITECTURE.md) and [design details](docs/architecture.md) | Source layout and adapters |
| [Quality evaluation](docs/plugin-eval.md) and [CLI verification](docs/round-trip-results.md) | Checks and their limits |

See [CONTRIBUTING.md](CONTRIBUTING.md) to propose a change and [authoring conventions](docs/authoring.md) to write plugin content.

## External memory integration

[Pensyve](https://github.com/major7apps/pensyve) remains an optional external Claude Code marketplace entry. Major7 Apps maintains Pensyve, and this repository's maintainer founded Major7 Apps. Its open-source runtime can run locally or on your own server. [Pensyve Cloud closed on October 1, 2026](https://pensyve.com/), and its dashboard, API, and hosted MCP endpoints are unavailable. Use the [self-hosting guide](https://github.com/major7apps/pensyve/blob/main/docs/self-host.md) when configuring the runtime.

## License

The repository is [MIT licensed](LICENSE). External plugins have their own licenses.

## Star history

[![Star History Chart](https://star-history.dera.page/svg?repos=wshobson/agents&type=date&legend=top-left)](https://star-history.dera.page/#wshobson/agents&type=date&legend=top-left)
