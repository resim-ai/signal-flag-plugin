# signal-flag

The Signal Flag field sessions entry point for Claude Code, distributed from the
`signal-flag-plugins` marketplace in `resim-ai/signal-flag-plugin`. The workflow lives on the ReSim
BFF. This plugin carries its entry command and an explicit setup command for a
bundled native recording reader; it has no install hooks or workflow copy.

## The command

`/signal-flag:explore-field-sessions [what to inspect, evaluate or add]` loads
`explore-field-sessions` from the configured Signal Flag BFF through `get_skill`.
The served resource `resim://skills/explore-field-sessions/SKILL.md` is the same
workflow. Session context comes from an explicit link, ID or S3 folder, or the open Chrome tab when the request refers to it.

The workflow registers folders as sessions, prepares customer metrics in the robot repository, directs the agent to build/push through the customer's AWS MCP, and verifies publication before registration. Before AWS writes or image publication, the person confirms the verified AWS identity and exact registry/repository destination as described below. The human separately approves the exact evaluation request in chat; honor any client permission prompt. Automatic tool acceptance and the confirmation argument do not establish that approval. Later SQL-only metrics score existing evaluations.

Use the plugin command to load the served skill through `get_skill`; there is no separate MCP prompt entry.

## Prerequisites

Connect the Signal Flag MCP endpoint for the intended environment and log in as
an organization member matching the web app account. The default server name is
`signal-flag`; configured alternatives may hold other accounts. Preserve those
mappings and select the account that owns the relevant browser tab.

The BFF must carry the sessions release. Chrome tools need access to the relevant
app/S3 tabs, and the customer's AWS MCP needs the registry build/push capabilities
and access required by their setup. The plugin stores no credentials or workflow
copy. Missing connectivity or a missing served skill is reported with the actual
configured environment; staff membership is not required.

## Confirm AWS identity and publication destination

Signal Flag requires a read-only effective-identity check before AWS writes or image push. Use an available AWS MCP identity tool, or `aws sts get-caller-identity` when the CLI is available and uses the same verified profile and effective credentials as the AWS/Finch MCP publication tools. A CLI identity from unrelated credentials does not verify the MCP's identity. Show the person the returned AWS account ID and caller/role ARN, actual profile (or identified credential source if unnamed), region, and full destination registry/repository URI; wait for explicit confirmation of that identity and destination. If the destination registry belongs to another account, show both caller and destination account IDs explicitly; an authorized cross-account push is valid. Reuse explicit confirmation only while the verified identity, credential source, region and destination remain unchanged. An existing login, default profile, or supplied URI alone is neither identity verification nor approval. If the publication identity cannot be verified, stop before AWS writes and explain the missing capability.

Prepare and test the image first where those steps do not write to AWS. Any change to account, role, profile/credential source, region, or destination invalidates confirmation; verify again and obtain a new confirmation before writes. The agent then performs the authorized build/push through the customer's AWS MCP and verifies the remote image. This does not authorize a local command fallback, new permissions, or evaluation: evaluations require separate explicit approval of the exact request in chat.

## Install

Start in your existing robot repository or another working directory where you will launch Claude. You do not need to clone a ReSim repository: Claude downloads the marketplace/plugin into its managed cache, and Signal Flag includes the reader wheel. Add the marketplace if it is missing, then install Signal Flag if it is not already installed:

```bash
claude plugin marketplace add resim-ai/signal-flag-plugin
claude plugin install signal-flag@signal-flag-plugins --scope user
```

The public marketplace can be downloaded without access to ReSim’s internal repositories. ReSim MCP access still requires your own account in the organization shown in the web app.

For an existing installation, run `claude plugin list` to identify its actual scope, then run `claude plugin marketplace update signal-flag-plugins` and `claude plugin update signal-flag@signal-flag-plugins --scope <existing-scope>`. Update each installed scope explicitly; update defaults to user scope. Run `/reload-plugins` in an open Claude session, or start a new session after the update. Use `install` only for a missing plugin; no uninstall or scope change is required.

## Connect Claude to the browser's environment

Choose the Signal Flag MCP endpoint for the same environment shown in your browser; obtain that endpoint from your ReSim environment owner or environment-specific setup guide. Do not infer it from a generic staging or production default. From the same working directory where you will launch Claude, add a missing local connection using that endpoint:

```bash
claude mcp add --transport http --scope local signal-flag '<matching-environment-mcp-url>'
claude --chrome
```

Replace the URL placeholder before running the command. Preserve an existing connection and account mapping; inspect it with `claude mcp get signal-flag` and select the matching configured name if several accounts exist. Local MCP connections are tied to the directory where they were added, unlike the user-scoped plugin, so launch Claude from that same directory. See [Claude Code's MCP scope documentation](https://code.claude.com/docs/en/mcp#local-scope).

In Claude, use `/mcp` to connect and complete OAuth as the organization member matching the web app. Ask Claude to verify `whoami` and the matching browser environment before project work, then use `/signal-flag:explore-field-sessions`. Native recording inspection uses `/signal-flag:setup-reader` and the bundled reader; no ReSim source checkout or `PYTHONPATH` is needed. Connecting MCP does not authorize AWS publication or evaluation; the separate confirmations above still apply.

## Plugin development only

During local development, load this checkout directly without changing installed
plugins or MCP account mappings. From this repository:

```bash
claude --chrome --plugin-dir ./plugins/signal-flag
```

The local plugin takes precedence over an installed copy with the same name. After editing it, `/reload-plugins` refreshes the local plugin. The workflow is loaded from the connected server through `get_skill`.
See [Claude Code's local plugin documentation](https://code.claude.com/docs/en/plugins#test-your-plugins-locally).

## Native recording inspection

Registered-session metadata, folder inventory, identity and Foxglove-link tools
do not require Python. Inspecting MCAP channels, schemas or values does require
an available reader runtime. Before executing reader code,
run `/signal-flag:setup-reader`. The bootstrap can run under system Python 3.10+
(including macOS Python 3.14). It finds an installed **Python 3.12** without
downloading and creates a separate virtual environment. If none is installed,
it downloads uv-managed Python 3.12 into private state. It never uses Python 3.14
as the reader runtime or inherits system site packages.
Install `uv` through your approved package manager first. The pinned native wheels
target macOS 12+ (Apple Silicon or Intel) and Linux; unsupported platforms fail
rather than compiling dependencies or changing pins.

The plugin bundles a `field-sessions-parser` wheel, native dependency hash lock, and source-commit/checksum manifest under `reader/`. The package is not fetched from PyPI and needs no private rerun checkout or `PYTHONPATH`. Native recording inspection supports MCAP files with JSON, ROS 1, ROS 2 or Protobuf messages; separate ROS bag, text, CSV, Parquet and HDF5 files are not supported. ROS decoding dependencies remain included for messages inside MCAP.

After checking session metadata, compatible builds and relevant customer code, use `<returned-cli> summary <recording.mcap>` when recording metadata is needed. Reader 0.2.3 returns header, channels, schema definitions and recorded counts/time bounds without traversing, decompressing or decoding messages. Missing statistics are unknown; schema definitions do not establish observed values or signal meaning. Missing, oversized or malformed summaries fail without a scan or full-download fallback. Range caches can fetch neighboring payload bytes, so this is not a strict total-transfer budget.

`<returned-cli> inspect <recording.mcap>` decodes the complete recording. Topic-filtered `iter_messages` can also traverse the entire file; neither is a bounded discovery sample. Full scans belong in the metrics job by default. A discovery sample needs a concrete purpose and bounded read scope; this reader has no bounded sampling API.

Setup verifies hashes, installs only binary dependencies, checks dependency consistency and imports the MCAP decoding and remote-read dependencies before reporting ready. It also writes and decodes a tiny synthetic MCAP entirely in memory, checking exact nanoseconds. SDK/test dependencies are excluded from the native runtime.

For direct invocation from this checkout:

```bash
python3 plugins/signal-flag/scripts/setup_reader.py
python3 plugins/signal-flag/scripts/setup_reader.py --check
```

In an installed plugin the command uses the actual `${CLAUDE_PLUGIN_ROOT}/scripts/setup_reader.py` path, as supported by [Claude Code's plugin reference](https://code.claude.com/docs/en/plugins-reference). Use the returned `python` path for reader snippets and `cli` path for reader commands. `--check` performs no installs or network calls. The runtime is keyed by the bundle contents and platform, so refreshing the plugin does not overwrite another bundle's runtime or alter the system Python.

The default writable state is `~/.cache/signal-flag/reader`, including dedicated
uv cache and Python directories. If this default is unwritable, setup reports a
fallback to an owned mode-0700 `signal-flag-reader-<uid>` directory under the
system temporary directory; shared directories and symlinks are refused. Temporary
state may be cleaned by the OS, in which case run setup again.
Set `SIGNAL_FLAG_READER_HOME` to another absolute,
authorized writable location when required. Newly created private directories
use mode 0700; existing directories are not chmodded. Explicit `UV_CACHE_DIR` and
`UV_PYTHON_INSTALL_DIR` values are honored and checked for actual write access;
an unwritable configured path is an actionable setup error, not a reason to
change filesystem permissions or conceal environment access from hooks.

Native setup does not prove remote access. A signed HTTPS URL still requires
correct Range responses through the customer's network/proxy. The reader
validates byte offsets and lengths, retries incomplete bodies within a fixed
attempt limit, and rejects Range-ignored responses before reading their bodies.
Persistent truncation must fail visibly. Use an already authorized remote execution capability when
available, or report the blocked read. Never substitute a local recording copy,
strip credential-bearing query parameters, or disable sandbox/proxy controls.

## SDK and container tests

`resim-open-core` is a Linux SDK dependency for the customer metrics image, not
native inspection. Discover the connected AWS/Finch MCP's actual execution,
build and push tools before attempting SDK tests in the verified Linux base.
Being connected to that MCP, or finding a local `finch`/`docker` binary, does not
establish authorized container execution. Missing or denied capabilities remain
explicit blockers; the plugin does not install a daemon, fall back to disallowed
host commands, or modify `.claude/settings.json` or any hooks.

The official Finch MCP's image build tool can execute SDK and synthetic job tests
through an explicit Dockerfile `RUN` in a `test` stage, even without a container
run tool. See [container tests](references/container-tests.md) for the shared
job/test/runtime stage pattern and required emissions checks. A normal successful
image build does not itself exercise its `ENTRYPOINT`.

The [field-sessions-parser repository](https://github.com/resim-ai/field-sessions-parser) owns the source, tests, wheel/lock generation and source provenance. Plugin release validation must exercise a clean installation on supported macOS and Linux, in addition to source reader tests and Linux SDK image tests. Bootstrap logic tests alone do not establish native wheel or remote Range compatibility.

For the Linux native-reader release check, build
[`references/native-reader-test.Dockerfile`](references/native-reader-test.Dockerfile)
through Finch MCP with this plugin root as `context_path`, the Dockerfile's
absolute path, `target: "test-results"`, the native Linux platform of the Finch VM, `no_cache: true`,
`quiet: false` and `progress: "plain"`. The disposable Python 3.12 image installs
the [pinned uv release](https://pypi.org/project/uv/0.9.26/) and explicitly runs
bootstrap followed by `--check`. Export the scratch results stage with
`outputs: "type=local,dest=<fresh-shared-workspace-directory>"` (Finch VM-local
`/tmp` is not a host export on macOS); read `runtime.txt`,
`setup.json` and `check.json`. Require both successful `status: "ready"` receipts
and synthetic MCAP checks; successful Finch responses can omit stdout. Use
Linux ARM64 on an ARM64 VM to avoid the observed amd64 uv emulation crash.
This installs no SDK and does not replace separate macOS, remote Range or SDK
validation gates.

## Reader provenance

The bundled reader wheel and dependency lock are verified against `reader/manifest.json` before installation. Its `source_repository` and full `source_revision` identify the committed source used to build the wheel. The source repository is public. Plugin version 0.0.7 bundles reader 0.2.3 unchanged from that build; installation does not require cloning the source repository.

## Investigation and editing scope

`explore-field-sessions` owns registration, summary inspection, replay, signal interpretation and approved evaluation. `author-session-metrics-build` owns editable customer source and synthetic SDK tests. The existing `author-metrics-config` skill owns SQL-only chart editing, grouped review and reusable publication. Existing results or SQL over sufficient emissions can answer a question without a new image or evaluation. Saved browser definitions and rejection decisions remain authoritative; reusable configuration publication is separate from a historical chart edit. Interactive message sampling is unsupported; use summary metadata, existing emissions or requested Foxglove replay.
