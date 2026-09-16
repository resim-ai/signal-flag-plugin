# CLAUDE.md — signal-flag-plugin

Repository-specific guidance is in [AGENTS.md](AGENTS.md). Customer installation requires only this public marketplace and the user’s own ReSim account.

## What this is

A Claude Code plugin marketplace distributing Signal Flag commands and a bundled Python reader. The workflow itself is served by the connected ReSim MCP environment.

## Commands

```bash
python3 -m unittest discover -s plugins/signal-flag/scripts/tests -p 'test_*.py'
claude plugin validate .
claude plugin validate ./plugins/signal-flag
```

## PRs

Follow the maintainer’s existing PR-tool preference; use GitHub CLI or Graphite as agreed for the task. Keep public changes free of internal workspace configuration and customer data.

## Testing conventions

Bootstrap tests use standard-library unittest. Validate both manifests and reader artifact hashes. Native installation and Linux SDK integration tests are separate from bootstrap tests.

## Gotchas

Preserve the reader wheel and lock hashes in the provenance manifest. Do not patch a wheel. Avoid enabling the internal and public copies of Signal Flag simultaneously. Local MCP configuration belongs to the directory where Claude starts.

## Directory map

`.claude-plugin/` holds the marketplace manifest. `plugins/signal-flag/` holds the plugin, commands, reader bundle, setup script, tests and container references.

`plugins/signal-flag/reader/` contains the 0.2.3 wheel, native dependency lock and provenance manifest. The `resim-ai/field-sessions-parser` repository owns reader source and releases and is public. Keep its repository URL and immutable source revision in the bundled provenance manifest.
