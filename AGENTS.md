# Signal Flag public plugin

This repository distributes the Claude Code Signal Flag plugin and its marketplace. It contains no customer data, credentials, internal workspace configuration or backend checkout.

`.claude-plugin/marketplace.json` lists only `plugins/signal-flag`. Keep its version aligned with `plugins/signal-flag/.claude-plugin/plugin.json`. The plugin's [AGENTS.md](plugins/signal-flag/AGENTS.md) owns runtime conventions. Only the metric-only workflow command is discoverable. `README.md` owns installation and update instructions; `CLAUDE.md` provides the repository command index.

Keep the plugin name `signal-flag` and marketplace name `signal-flag-plugins` stable. Use the public repository in installation commands and homepage metadata. The workflow uses existing datalake data; do not reintroduce reader bundles, setup commands, source inspection or build publication.

Write each prose paragraph on one source line. Do not add credentials, signed recording URLs, customer fixtures or internal workspace history. Validate JSON, local links and plugin structure with the installed Claude plugin validator.

Obtain Pete's explicit confirmation before any public code push, tag or release. Prepare exact contents for review first; prior publication or a request to update the plugin does not waive confirmation.
