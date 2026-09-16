---
description: Install or verify the bundled Python 3.12 recording reader in an isolated local environment, without the Linux SDK.
argument-hint: "[check]"
---

This is explicit setup for native recording inspection. Registered-session
metadata, folder inventory, identity and Foxglove-link tools do not need it.
Inspecting MCAP channels/schemas/values does need a reader runtime. No install hook
runs automatically.

Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/setup_reader.py"`; if the argument is
`check`, append `--check` for a read-only, offline verification. Use the actual
plugin root supplied by Claude Code, not a guessed installation cache path.
Python 3.10+ can run this bootstrap. It first finds an existing Python 3.12 without
downloading, then creates an isolated virtual environment from it. Only if none
is available does it download uv-managed Python 3.12 into private state. It never
uses Python 3.14 as the reader runtime. `uv` must already be available through
the customer's approved setup. macOS 12+ and Linux are supported targets.

The script checks the bundled wheel and dependency hashes, installs into a private
versioned environment, and returns its exact Python, CLI and state paths. It uses
a private home cache by default; if that default is unwritable, it reports a
fallback to an owned mode-0700 directory under the system temporary directory.
Explicitly selected state/cache paths are never silently replaced.
If an existing `UV_CACHE_DIR` or
`UV_PYTHON_INSTALL_DIR` is not writable, report that path and let the user select
an authorized location; do not change permissions or sandbox rules. The user can
set `SIGNAL_FLAG_READER_HOME` to an absolute writable state directory.

Report the actual result and use the returned Python path for subsequent native reader snippets. Use the returned CLI with `summary <recording.mcap>` for recorded metadata without message traversal. `inspect` decodes the complete recording and is not a default discovery step. A missing or malformed summary fails without a scan fallback; range caching can fetch neighboring bytes and is not a strict transfer budget. No rerun checkout or PYTHONPATH is needed. This does not install `resim-open-core`, prove AWS access, prove HTTP Range works, or authorize execution of customer robot code. A blocked download or truncated signed-HTTPS response is a runtime limitation; do not download an MCAP locally or bypass the proxy/hooks.

For SDK/build tests, discover the customer's connected AWS/Finch MCP tools and
their actual container execution/build/push capabilities. A connected server or
local Docker/Finch executable alone proves none of those capabilities. When
Finch exposes image builds but no run tool, use the explicit `RUN` test-stage
pattern in `${CLAUDE_PLUGIN_ROOT}/references/container-tests.md`: execute the
actual job on synthetic fixtures with `target: "test"` and `no_cache: true`, and
require passing emitted-output assertions. A build that only declares an
`ENTRYPOINT` does not test the job. If the required build/execution capability is
unavailable or denied, report that blocker and stop the dependent test. Do not
switch to disallowed host execution or alter `.claude/settings.json` to evade a
denial.
