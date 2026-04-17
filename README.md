# claude-code-homeassistant-hermit

> **Early alpha — this plugin controls real home devices. Review every action before confirming.**

A [`claude-code-hermit`](https://github.com/gtapps/claude-code-hermit) plugin for autonomous Home Assistant management. Ships HA-aware skills, subagents, and a safety hook. Pairs with the `ha-agent-lab` Python CLI for bulk REST operations, entity policy enforcement, YAML simulation, and safe apply.

All MCP actuation calls are pre-screened by `hooks/mcp-safety-gate.py` before reaching Home Assistant. Locks, alarm panels, and security devices are blocked by policy — blocked operations become proposals for human review.

## What this plugin provides

| | |
|---|---|
| **Skills** | `ha-boot`, `ha-house-status`, `ha-morning-brief`, `ha-refresh-context`, `ha-build-automation`, `ha-apply-change`, `ha-analyze-patterns`, `ha-hatch` |
| **Subagents** | `ha-safety-reviewer`, `ha-automation-builder`, `ha-pattern-analyst` |
| **Safety hook** | MCP actuation calls are gated by `hooks/mcp-safety-gate.py` before reaching HA |
| **Python CLI** | `ha-agent-lab` — REST client, entity safety policy, YAML simulation, safe apply |

## Prerequisites

- [Claude Code](https://claude.ai/code) installed
- Python ≥ 3.12 with `pip install --user PyYAML python-dotenv`
- A running [Home Assistant](https://www.home-assistant.io/) instance
- The [claude-code-hermit](https://github.com/gtapps/claude-code-hermit) core plugin

## Setup

### 1. Add marketplaces and install plugins

```
claude marketplace add gtapps/claude-code-hermit
claude marketplace add gtapps/claude-code-homeassistant-hermit
claude plugin install claude-code-hermit@claude-code-hermit
claude plugin install claude-code-homeassistant-hermit@claude-code-homeassistant-hermit
```

Or, if using this repo directly as a local plugin:

```
claude plugin add-local /path/to/claude-code-homeassistant-hermit
```

### 2. Install Python runtime dependencies

```bash
pip install --user PyYAML python-dotenv
```

### 3. Set up your environment file

In your project directory:

```bash
cp .env.example .env
```

Fill in the required values:

```
HOMEASSISTANT_LOCAL_URL=http://homeassistant.local:8123
HOMEASSISTANT_TOKEN=<your long-lived access token>
```

Never commit `.env` — it is gitignored.

### 4. Configure Home Assistant MCP Server

In Home Assistant:

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **"Model Context Protocol Server"** and enable it

Then register it in Claude Code under the canonical name `homeassistant`:

```bash
claude mcp add-json homeassistant '{
  "type": "http",
  "url": "https://<your_home_assistant_url>/api/mcp",
  "headers": { "Authorization": "Bearer <YOUR_TOKEN>" }
}'
```

> **Name matters**: skills and the safety hook expect MCP tool IDs in the form `mcp__homeassistant__*`. If you register under a different name, update `hooks/hooks.json` accordingly.

See the [official HA MCP Server docs](https://www.home-assistant.io/integrations/mcp_server/) for details.

### 5. Hatch core hermit and HA layer

In Claude Code, open your project and run:

```
/claude-code-hermit:hatch
```

Then:

```
/claude-code-homeassistant-hermit:ha-hatch
```

This verifies your `.env`, walks you through MCP setup, updates `CLAUDE.md`, and confirms connectivity.

### 6. Verify

Run `/mcp` inside Claude Code and confirm `homeassistant` is connected.

## Usage

Start every session with:

```
/claude-code-homeassistant-hermit:ha-boot
```

Then use skills as needed:

| Skill | Purpose |
|-------|---------|
| `/claude-code-homeassistant-hermit:ha-house-status` | Live house status snapshot |
| `/claude-code-homeassistant-hermit:ha-morning-brief` | Daily brief — presence, energy, alerts, proposals |
| `/claude-code-homeassistant-hermit:ha-refresh-context` | Fetch and normalize full HA entity inventory |
| `/claude-code-homeassistant-hermit:ha-build-automation` | Draft and validate an automation YAML |
| `/claude-code-homeassistant-hermit:ha-apply-change` | Apply validated YAML with safety checks |
| `/claude-code-homeassistant-hermit:ha-analyze-patterns` | Identify automation opportunities from history data |

## CLI

The `ha-agent-lab` CLI is invoked by skills automatically via `${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab`. You can also run it directly from the plugin directory:

```bash
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha refresh-context
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha simulate <artifact>
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha validate-apply <artifact> --reload automation
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha policy-check <target>
${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab boot status --probe
```

## Safety

The agent never autonomously actuates locks, alarm panels, or security-related covers/buttons/switches. All MCP actuation calls matching `mcp__homeassistant__Hass*` are pre-checked by `hooks/mcp-safety-gate.py` against `src/ha_agent_lab/policy.py`. Calls targeting unresolvable entities (area-only or device-only targets) are blocked by default. Blocked operations become proposals for human review.

**Policy overrides** (add to `.env`, see `.env.example`):

| Variable | Effect |
|---|---|
| `HA_SAFE_ENTITIES=cover.garage_door,...` | Per-entity allow-list. Exact IDs only, no wildcards. |
| `HA_EXTRA_SENSITIVE_DOMAINS=vacuum,...` | Block additional domains entirely. |
| `HA_EXTRA_SENSITIVE_KEYWORDS=pool,...` | Block extra keywords in conditionally-sensitive domains. |

## Architecture

```
claude-code-homeassistant-hermit (this plugin)
  ├── skills/          HA workflow skills
  ├── agents/          HA subagents
  ├── hooks/           Safety gate (mcp-safety-gate.py) + hooks.json
  ├── state-templates/ CLAUDE-APPEND.md (injected by ha-hatch)
  └── src/ha_agent_lab/  Python CLI (REST client, policy, simulation, apply)

claude-code-hermit (core, required)
  └── Session lifecycle, proposals, cost tracking, memory
```

## License

MIT — see [LICENSE](LICENSE).
