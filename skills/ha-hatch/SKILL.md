---
name: ha-hatch
description: One-time Home Assistant setup for this hermit. Configures HA access, connects to the official Home Assistant MCP Server integration, and verifies both the Python CLI and HA MCP. Run once per project after /claude-code-hermit:hatch.
---

# Home Assistant Hatch

Set up the Home Assistant layer for this project. Idempotent — safe to re-run; will skip completed steps and offer re-verify only.

## Plan

### 1. Prereq check

Read `.claude-code-hermit/config.json`.

- If the file is missing or `_hermit_versions["claude-code-hermit"]` is absent or less than `1.0.0`:
  - `AskUserQuestion`: "Core hermit is not initialized. Run `/claude-code-hermit:hatch` now?"
  - Yes → invoke `/claude-code-hermit:hatch`, then continue.
  - No → stop and explain what is required.

### 2. Idempotency check

Read `_hermit_versions["claude-code-homeassistant-hermit"]` from `config.json`. Read the `version` field from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`.

- If versions match → `AskUserQuestion`: "Already set up. Re-verify HA access only (skip setup wizard)?". Yes → skip to §6. No → continue.
- If stale or absent → continue with setup.

### 3. Verify .env

Check that `.env` exists at the project root and contains `HOMEASSISTANT_TOKEN` and `HOMEASSISTANT_LOCAL_URL`.

- **If `.env` is missing or incomplete**: stop and tell the user:
  ```
  Please set up your .env file first:
    cp .env.example .env
  Then fill in HOMEASSISTANT_TOKEN and HOMEASSISTANT_LOCAL_URL and re-run this hatch.
  ```
  Do not write or modify `.env` — it is the user's responsibility.

- **If `.env` is present and has both required keys**: proceed.

Also ask the user one question:

- **Language / locale**: What language should the agent use for HA-facing output? (e.g. `en`, `pt`, `es`)

Store the locale in `MEMORY.md` House Profile (create the section if missing). Do not collect or store the token — it stays in `.env` only.

### 4. Python runtime deps + CLI check

Run `python3 -c "import yaml, dotenv"`.

- If it fails, stop and tell the user:
  ```
  The ha-agent-lab CLI needs PyYAML and python-dotenv.
  Install with:  pip install --user PyYAML python-dotenv
  Docker users:  add "RUN pip install PyYAML python-dotenv" to your image.
  Then re-run /claude-code-homeassistant-hermit:ha-hatch.
  ```
- If it passes, run `${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab boot status` (read-only, no `--probe`) to confirm the CLI loads correctly.

### 5. Home Assistant MCP Server guidance

Surface the official setup instructions. Present each step clearly:

**Step A — Enable the integration in Home Assistant**

Go to Home Assistant → Settings → Devices & Services → Add Integration → search "Model Context Protocol Server". Enable it. This exposes the MCP endpoint at `https://<your_ha_url>/api/mcp`.

Reference: https://www.home-assistant.io/integrations/mcp_server/

**Step B — Connect Claude Code**

Run this command in your terminal (replace with your actual URL and token):

```
claude mcp add-json homeassistant '{
  "type": "http",
  "url": "https://<your_home_assistant_url>/api/mcp",
  "headers": { "Authorization": "Bearer <HOMEASSISTANT_TOKEN>" }
}'
```

OAuth note: If your HA instance supports it, the official docs also document an OAuth flow via `--oauth-client-information`. The token fallback above works for all cases.

Important: The registration name **must be `homeassistant`** to match the tool IDs expected by this plugin's skills, agents, and safety hook. If you use a different name, update the `hooks/hooks.json` matcher and `.claude/settings.json` accordingly.

**Step C — Verify MCP connectivity**

Run `/mcp` inside Claude Code and confirm `homeassistant` appears as connected.

Ask the user to confirm they have completed Steps A–C before proceeding.

### 6. Verify Python CLI (full probe)

Run `${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab boot status --probe` and present the result. If it fails:

- Missing deps → instruct the user to run `pip install --user PyYAML python-dotenv`.
- Connection refused → check `HOMEASSISTANT_LOCAL_URL` in `.env`.
- Auth error → check `HOMEASSISTANT_TOKEN`.

### 7. Append to CLAUDE.md

Read `${CLAUDE_PLUGIN_ROOT}/state-templates/CLAUDE-APPEND.md`.

Check CLAUDE.md for the marker comment `<!-- claude-code-homeassistant-hermit: Home Assistant Workflow -->`:

- Absent → append the full CLAUDE-APPEND.md content.
- Present and version matches current plugin version → skip.
- Present and version is stale → replace the block between the opening and closing markers with the updated content.

### 8. Stamp version

Write `_hermit_versions["claude-code-homeassistant-hermit"]` into `.claude-code-hermit/config.json` with the current plugin version.

Also prompt: "Add the default HA daily context-refresh routine (08:30 every day)? It runs `${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab ha refresh-context` automatically." — Yes adds `routines.daily-ha-context` entry to `config.json`; No skips.

### 9. Final report

Summarize:

```
ha-hatch complete
  ✓  .env verified (user-managed)
  ✓  Python CLI: ${CLAUDE_PLUGIN_ROOT}/bin/ha-agent-lab boot status --probe → OK / FAILED
  ?  HA MCP Server: manually verified via /mcp
  ✓  CLAUDE.md updated
  ✓  config.json stamped v<version>

Manual steps remaining:
  - Enable 'mcp_server' integration in Home Assistant (if not done)
  - Run: claude mcp add-json homeassistant '{...}' (if not done)
  - Run /mcp in Claude Code to confirm 'homeassistant' is connected
  - If you registered under a different name: update hooks/hooks.json matcher
```
