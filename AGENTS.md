# Signal Flag public plugin

This repository distributes the Claude Code Signal Flag plugin and its marketplace. It contains no customer data, credentials, internal workspace configuration or backend checkout.

`.claude-plugin/marketplace.json` lists only `plugins/signal-flag`. Keep its version aligned with `plugins/signal-flag/.claude-plugin/plugin.json`. The plugin’s [AGENTS.md](plugins/signal-flag/AGENTS.md) owns its runtime conventions. `README.md` owns public installation and update instructions; `CLAUDE.md` provides the repository command index. `.gitignore` excludes Python-generated files.

Keep the plugin name `signal-flag` and marketplace name `signal-flag-plugins` stable. Use the public repository in installation commands and homepage metadata. `plugins/signal-flag/reader/` holds the 0.2.2 MCAP reader wheel, native hash lock and provenance manifest. Preserve these artifacts together; regenerate artifacts from committed reader source rather than editing wheel contents.

Write each prose paragraph on one source line. Do not add credentials, signed recording URLs, customer fixtures or internal workspace history. Validate changes with Python bootstrap tests, JSON parsing, manifest hash checks and Claude plugin validation where available. Do not claim a native or SDK test passed from bootstrap tests alone.

Obtain Pete’s explicit confirmation before any public code push, tag or release. Prepare the exact repository contents and release changes for review first; prior publication or a request to update the plugin does not waive confirmation.
