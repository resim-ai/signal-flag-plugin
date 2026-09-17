# Signal Flag for Claude Code

Create new metrics using data already available in your ReSim datalake, then review them in the existing metric editor. The plugin connects to your organization's Signal Flag MCP environment; it requires no recording reader or AWS connection.

## Install

Run these commands from the directory where you will use Claude. No source checkout is required:

```bash
claude plugin marketplace add resim-ai/signal-flag-plugin
claude plugin install signal-flag@signal-flag-plugins --scope user
```

Choose the MCP endpoint matching your ReSim web app environment, then add it from the directory where you will launch Claude:

```bash
claude mcp add --scope local --transport http signal-flag 'YOUR_RESIM_MCP_URL'
claude --chrome
```

Replace `YOUR_RESIM_MCP_URL` with the endpoint provided for your environment. Inside Claude, use `/mcp` to authenticate with your own ReSim account and `/chrome` to connect Chrome. Ask Claude to verify that `whoami` matches the environment and organization in the open app tab, then run:

```text
/signal-flag:explore-field-sessions
```

The marketplace is public. Access to your ReSim organization uses your own authorized account. Local MCP configuration belongs to the current working directory; launch Claude there. Keep existing environment/account connections intact and select the matching one if it already exists.

## Update an existing installation

Run `claude plugin list` to check the installed scope, then update that scope:

```bash
claude plugin marketplace update signal-flag-plugins
claude plugin update signal-flag@signal-flag-plugins --scope user
```

Use `project` or `local` instead of `user` when that is the installed scope. Run `/reload-plugins` in an existing Claude session. If you previously installed `signal-flag@resim-tools` from the internal marketplace, disable that copy in its installed scope through `/plugin` before enabling this public copy; keep its MCP connections. Choose one active Signal Flag installation to avoid duplicate commands. The internal `resim-shared` plugin is not required.

## Metric-only workflow

Ask for a new metric and provide the existing session or dataset context. Claude checks available data, proposes unused metric names, previews against a compatible existing instance, and prepares grouped review. Missing fields and unavailable previews are reported explicitly.

The workflow does not inspect recordings or repositories, register sessions, install readers, develop emissions, publish metrics images or launch evaluations. Publishing reusable metric configuration is distinct from adding a chart to a historical instance.

See the [plugin guide](plugins/signal-flag/README.md) for scope, review and connection requirements.

## Validation

```bash
claude plugin validate .
claude plugin validate ./plugins/signal-flag
```

Plugin and marketplace versions must stay aligned. Publication is a separate maintainer-approved step.
