<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License" /></a>
  <a href="https://code.claude.com/docs/en/plugins"><img src="https://img.shields.io/badge/Claude%20Code-plugin-orange.svg" alt="Claude Code Plugin" /></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-0.0.1-green.svg" alt="Version 0.0.1" /></a>
  <img src="https://img.shields.io/badge/Claude-Pro%20%7C%20Max-blueviolet.svg" alt="Claude Pro/Max Compatible" />
  <img src="https://img.shields.io/badge/status-early%20alpha-red.svg" alt="Early Alpha" />
  <img src="https://img.shields.io/badge/Home%20Assistant-MCP-41BDF5.svg" alt="Home Assistant MCP" />
</p>

# claude-code-homeassistant-hermit

**Turn Claude Code into an Always-on Personal AI Assistant for your Home Assistant.**

A [`claude-code-hermit`](https://github.com/gtapps/claude-code-hermit) plugin for the Home Assistant community. It learns your entities, drafts automations under a safety policy, and lets hermit's reflect loop surface integration drops, automation errors, and energy anomalies — as proposals you accept or reject.

Three steps to a running 24/7 pHA hermit:

```bash
# Install
claude plugin marketplace add gtapps/claude-code-hermit
claude plugin marketplace add gtapps/claude-code-homeassistant-hermit
claude plugin install claude-code-hermit@claude-code-hermit --scope project
claude plugin install claude-code-homeassistant-hermit@claude-code-homeassistant-hermit --scope project

# Initialize
/claude-code-homeassistant-hermit:ha-hatch

# Go always-on
/claude-code-hermit:docker-setup
```

---

## How It Works

1. **Install and meet your house.** `ha-hatch` a wizard that creates your personal AI assistant, registers the Home Assistant MCP server and seeds `CLAUDE.md`. `ha-refresh-context` then snapshots every entity, area, device, and automation into `.claude-code-hermit/raw/` and compiles durable profiles your next session reloads instantly — the raw/compiled pattern Andrej Karpathy describes for LLM context, inherited from hermit.

2. **Ask for automations in plain language.** `ha-build-automation` drafts YAML in an isolated worktree, simulates it against your inventory, and hands it to `@ha-safety-reviewer`. `ha-apply-change` only reloads Home Assistant after validation and policy checks pass.

3. **Every actuation is pre-screened.** A PreToolUse hook gates the HA MCP server. Locks, alarm panels, and security-related devices are blocked by policy; unresolvable targets (area- or device-only) are blocked by default. Blocked operations don't fail silently — they become **proposals** for your review.

4. **Routines run themselves.** Morning brief, daily context refresh, weekly safety audit, daily integration-health and automation-error checks — registered as hermit `plugin_checks` and dispatched via reflect. Silence means everything's fine. Do you want a new routine, just ask and hermit sets it up.

5. **Everything is browsable.** HA sessions, proposals, pattern findings, and cost tracking flow into your hermit Cortex — the Obsidian vault hermit maintains — so your house's history is greppable, linkable, and yours.

---

## Quick Start

> **Requirements:** [Claude Code](https://code.claude.com) v2.1.98+, Python ≥ 3.12, a running [Home Assistant](https://www.home-assistant.io/) instance, and the [`claude-code-hermit`](https://github.com/gtapps/claude-code-hermit) core plugin.

### 1. Install

```bash
cd /path/to/your/project
claude plugin marketplace add gtapps/claude-code-hermit
claude plugin marketplace add gtapps/claude-code-homeassistant-hermit
claude plugin install claude-code-hermit@claude-code-hermit --scope project
claude plugin install claude-code-homeassistant-hermit@claude-code-homeassistant-hermit --scope project
pip install --user PyYAML python-dotenv
```

### 2. Configure

Create `.env` in the project directory (gitignored):

```
HOMEASSISTANT_LOCAL_URL=http://homeassistant.local:8123
HOMEASSISTANT_TOKEN=<your long-lived access token>
```

In Home Assistant, enable **Settings → Devices & Services → Add Integration → Model Context Protocol Server** ([docs](https://www.home-assistant.io/integrations/mcp_server/)).

### 3. Initialize

```
/claude-code-hermit:hatch
/claude-code-homeassistant-hermit:ha-hatch
```

`ha-hatch` verifies your `.env`, installs Python deps (creating a `.venv` if needed), writes a project-scoped `.mcp.json` that registers the HA MCP server under the canonical name `homeassistant`, updates `CLAUDE.md`, and confirms connectivity.

After `ha-hatch`: **restart Claude Code**, approve the `homeassistant` server on first use, then verify with `/mcp`.

> **Name matters:** skills and the safety hook expect MCP tool IDs in the form `mcp__homeassistant__*`. The generated `.mcp.json` uses this name automatically.

Then every session starts with:

```
/claude-code-homeassistant-hermit:ha-boot
```

---

## The Learning Loop

- **Reflect daily.** `ha-integration-health` and `ha-automation-error-review` run on a schedule. They flag domains with elevated `unavailable` ratios and automations whose traces errored more than a threshold. Findings arrive as proposals.
- **Audit weekly.** `ha-safety-audit` re-reads every live automation against the current safety policy. Drift becomes a proposal, not a silent regression.
- **Propose, don't mutate.** Every finding — safety drift, dropped integration, recurring error, new automation opportunity — is a proposal. Accept, reject, defer, dismiss. You stay in control.

---

## Safety

Every MCP actuation is pre-checked by `hooks/mcp-safety-gate.py` against `src/ha_agent_lab/policy.py`:

- **Hard-blocked domains:** `lock`, `alarm_control_panel`, and security-related `cover` / `button` / `switch`.
- **Blocked by default:** calls whose target resolves to area or device IDs only (no explicit entity IDs). Blocked operations become proposals.

Override via `.env`:

| Variable | Effect |
|---|---|
| `HA_SAFE_ENTITIES=cover.garage_door,...` | Per-entity allow-list. Exact IDs only, no wildcards. |
| `HA_EXTRA_SENSITIVE_DOMAINS=vacuum,...` | Block additional domains entirely. |
| `HA_EXTRA_SENSITIVE_KEYWORDS=pool,...` | Block extra keywords in conditionally-sensitive domains. |

---

## Skills & Agents

All skills are namespaced `/claude-code-homeassistant-hermit:ha-*`.

| Skill | Purpose |
|-------|---------|
| `ha-boot` | Start session, check HA connectivity, context freshness, locale |
| `ha-house-status` | Live house status snapshot via MCP |
| `ha-morning-brief` | Daily brief — presence, energy, alerts, proposals |
| `ha-refresh-context` | Fetch and normalize full HA entity inventory |
| `ha-build-automation` | Draft and validate automation YAML |
| `ha-apply-change` | Apply validated YAML with safety checks |
| `ha-analyze-patterns` | Identify automation opportunities from history |
| `ha-safety-audit` | Re-audit live automations against policy (weekly `plugin_check`) |
| `ha-integration-health` | Detect dropped integrations via unavailable ratios (daily `plugin_check`) |
| `ha-automation-error-review` | Flag automations with recurring errors in HA's log (daily `plugin_check`) |

| Agent | Purpose |
|-------|---------|
| `@ha-automation-builder` | Drafts YAML in an isolated worktree |
| `@ha-pattern-analyst` | Analyzes history for patterns (Haiku, cheap) |
| `@ha-safety-reviewer` | Reviews YAML for policy compliance (read-only) |

---

## CLI

Skills call `ha-agent-lab` automatically. Run it directly if you want:

```bash
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha refresh-context
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha simulate <artifact>
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha validate-apply <artifact> --reload automation
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha policy-check <target>
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha audit-automations
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha automation-errors [--min-hits N]
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab boot status --probe
```

---

## Running 24/7

A hermit doesn't sleep. If you can run Claude Code, you can run this — laptop, Raspberry Pi, home server, anywhere.

Follow hermit's always-on path:

```
/claude-code-hermit:docker-setup
```

HA routines (`daily-ha-context`, `morning-brief`, and the three `plugin_checks`) load automatically at startup — no interactive `hermit-routines load` needed. Make sure the container can reach `HOMEASSISTANT_LOCAL_URL` and mount `.env` read-only.

---

## Your House, Your Rules

- **Tune the safety policy** via the `.env` overrides above.
- **Teach the agent your house** in `MEMORY.md` — language, schedules, learned patterns, known issues.
- **Add your own skill** — drop a directory into `skills/` named `ha-your-thing/`. Skills, agents, and hooks are plain files; fork and bend them.

---

## Credits

- [`claude-code-hermit`](https://github.com/gtapps/claude-code-hermit) — session lifecycle, reflect, Cortex, proposals
- [Home Assistant MCP Server](https://www.home-assistant.io/integrations/mcp_server/) — live operations
- Andrej Karpathy's raw/compiled memory pattern, via hermit
- [Claude Code](https://code.claude.com) — the plugin runtime

---

## License

MIT — see [LICENSE](LICENSE).
