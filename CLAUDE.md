# CLAUDE.md — signal-flag-plugin

Repository-specific guidance is in [AGENTS.md](AGENTS.md).

## What this is

A Claude Code plugin marketplace for creating metrics from existing ReSim datalake data. The connected MCP environment serves the workflow; the plugin carries one command and no local runtime.

## Commands

```bash
claude plugin validate .
claude plugin validate ./plugins/signal-flag
```

## Conventions

Use the maintainer's selected PR tooling. Keep public changes free of internal configuration and customer data. Check both JSON manifests and local documentation links. Public pushes, tags and releases require explicit confirmation.

## Directory map

`.claude-plugin/` holds the marketplace manifest. `plugins/signal-flag/` holds the plugin manifest, workflow command and documentation. Local MCP configuration belongs to the directory where Claude starts. Avoid enabling internal and public Signal Flag copies simultaneously.
