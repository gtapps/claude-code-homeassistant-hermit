# Changelog

All notable changes to `claude-code-homeassistant-hermit` / `ha-agent-lab` are documented here.

## [Unreleased]

### Fixed

- **`audit_automations` 404 on bulk endpoint** — replaced the non-existent `GET /api/config/automation/config` call with a two-step fetch: enumerate automation entities via `/api/states`, then fetch each config individually via `/api/config/automation/config/{id}` in parallel (up to 20 concurrent requests). Automations lacking a numeric `id` (YAML-packaged) are counted in `unmanaged`; per-ID 404s are counted in `fetch_failures`; other errors still propagate loudly. Fixes `ha audit-automations` and the `ha-safety-audit` scheduled check.

### Added

- **`ha probe <path>` CLI subcommand** — `bin/ha-agent-lab ha probe /api/config/automation/config/1234` GETs a raw HA REST path and pretty-prints the JSON response. Provides a safe alternative to `curl` when the `Bash(*TOKEN*)` deny-pattern hook is active, and a quick way to verify whether a REST endpoint exists before writing code against it.
- **HA API references in `CLAUDE.md`** — links to the authoritative REST and WebSocket API docs, a verification rule ("probe a live instance or WebFetch upstream before assuming an endpoint exists"), and a known-gotchas section seeded with the automation-listing lesson from this bug.

---

## [0.0.3] — 2026-04-22

### Changed

- **Align with claude-code-hermit 1.0.16: scheduled-checks decoupled from reflect** — all references to "plugin_check via reflect" updated to "scheduled check via reflect-scheduled-checks" across skill descriptions, hatch instructions, and docs. The `scheduled-checks` routine (registered by core hermit 1.0.16's hatch/evolve) is now the correct driver of our four HA checks; reflect no longer runs them. Updated files: `skills/ha-safety-audit`, `ha-integration-health`, `ha-automation-error-review`, `ha-analyze-patterns`, `hatch`, `docs/knowledge-schema.md`, `CLAUDE.md`.
- **Minimum core hermit requirement bumped to ≥ 1.0.16** — ensures the core `scheduled-checks` routine is registered on fresh installs; on 1.0.15 that routine is absent and scheduled checks would silently never fire.

---

## [0.0.2] — 2026-04-22

### Fixed

- **`plugin_checks` → `scheduled_checks` (hermit 1.0.15 rename)** — `hatch` now writes scheduled checks under the `scheduled_checks` config key. Prior installs registered checks under the old `plugin_checks` key, which reflect silently ignored after the core hermit upgrade. Operator-facing copy ("Plugin Checks") updated to "Scheduled Checks" throughout.
- **Missing `config.boot_skill` write in hatch (hermit 1.0.14)** — `hatch` now explicitly writes `boot_skill: "/claude-code-homeassistant-hermit:ha-boot"` to `config.json` during setup. The field was declared in `plugin.json` and handled by `hermit-evolve` for upgrades, but was never written on fresh installs — so always-on mode booted with the generic session skill instead of `ha-boot`.

### Changed

- **Minimum core hermit requirement bumped to ≥ 1.0.15** — required for `scheduled_checks` key support and `boot_skill` config field.

## [0.0.1] — 2026-04-21

Initial public release.
