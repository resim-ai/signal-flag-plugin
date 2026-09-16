# Signal Flag for Claude Code

Explore robot recording sessions, develop metrics with Claude, and review metrics in the ReSim web app. The plugin connects to your organization’s Signal Flag MCP environment and bundles an optional native recording reader.

## Install

Run these commands from your robot repository or another working directory. No ReSim source checkout is required:

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

The marketplace is public. Access to your ReSim organization and AWS resources uses your own authorized accounts. Local MCP configuration belongs to the current working directory; launch Claude there. Keep existing environment/account connections intact and select the matching one if it already exists.

## Update an existing installation

Run `claude plugin list` to check the installed scope, then update that scope:

```bash
claude plugin marketplace update signal-flag-plugins
claude plugin update signal-flag@signal-flag-plugins --scope user
```

Use `project` or `local` instead of `user` when that is the installed scope. Run `/reload-plugins` in an existing Claude session. If you previously installed `signal-flag@resim-tools` from the internal marketplace, disable that copy in its installed scope through `/plugin` before enabling this public copy; keep its MCP connections. Choose one active Signal Flag installation to avoid duplicate commands. The internal `resim-shared` plugin is not required.

## Recording inspection and image publication

Registered-session metadata and Foxglove links need no Python runtime. The reader supports MCAP recordings, including JSON, ROS 1, ROS 2 and Protobuf messages inside MCAP. To inspect MCAP channels, schemas and values, run `/signal-flag:setup-reader`. The bootstrap requires Python 3.10+ and `uv`; it provisions an isolated Python 3.12 runtime with the bundled reader and pinned dependencies. No backend checkout or Linux SDK is required. Use the returned CLI with `summary <recording.mcap>` for channels, schema definitions and recorded statistics without traversing messages. `inspect` decodes the complete recording and requires an intentional full scan; it is not the default discovery operation. Remote reads validate byte ranges, but range caching can fetch neighboring bytes and is not a strict total-transfer budget. Setup does not download recordings.

Metrics images are built and pushed through the customer’s AWS MCP. Before AWS writes, Claude verifies the effective AWS account and role, shows the region and full destination registry/repository, and waits for explicit confirmation. Session evaluation has its own separate approval.

See the [plugin guide](plugins/signal-flag/README.md) for reader setup, AWS confirmation, Linux SDK tests and troubleshooting.

## Validation

```bash
python3 -m unittest discover -s plugins/signal-flag/scripts/tests -p 'test_*.py'
claude plugin validate .
claude plugin validate ./plugins/signal-flag
```

Plugin version 0.0.8 includes the MCAP-only reader 0.2.3, built from the exact source revision recorded with artifact hashes in [the manifest](plugins/signal-flag/reader/manifest.json). The source, tests and release tooling live in [field-sessions-parser](https://github.com/resim-ai/field-sessions-parser), which is public. The plugin bundles the wheel unchanged from that build and needs no source checkout; customers keep their metrics-build code in their own repository.
