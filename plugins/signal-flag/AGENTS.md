# Signal Flag plugin

This is a Claude Code plugin. Preserve `.claude-plugin/plugin.json` and the
existing marketplace/account configuration; do not add Codex plugin metadata.

`commands/` contains the workflow entry point and explicit reader setup command. `scripts/setup_reader.py` verifies the bundled `reader/` wheel, dependency lock and provenance manifest, then creates an isolated Python 3.12 inspection runtime. `scripts/tests/test_setup_reader.py` covers integrity and bootstrap isolation. The `resim-ai/field-sessions-parser` repository owns the reader source and release artifacts and is public; do not patch wheel contents or maintain another reader implementation here.

No install hooks, policy changes, local recording copies or SDK installation are
part of native setup. Run the setup tests with Python's standard-library unittest.
Mac/Linux real installs and container SDK tests are separate validation gates.

`references/container-tests.md` documents the Finch MCP test-build route with
explicit entrypoint execution and synthetic emissions validation. It is a stage
pattern, not a bundled test suite or permission to change container policy.
`references/native-reader-test.Dockerfile` tests the bundled native reader's
clean Linux Python 3.12 setup and subsequent `--check` inside a disposable image.
Use the plugin root as its build context; this check installs no ReSim SDK.

The reader requires exact HTTP206 byte ranges and rejects ignored-Range full responses. Keep bounded truncation retries and credential-safe diagnostics in the reader package; native setup success alone is not remote-read evidence.

The native reader supports MCAP only, including JSON, ROS 1, ROS 2 and Protobuf messages inside MCAP. Keep the bootstrap smoke imports aligned with those decoding dependencies; do not require HDF5 or Parquet libraries. The public command loads the served workflow through `get_skill`, without a separate MCP prompt surface.

The bundled reader 0.2.3 provides `summary` for metadata-only discovery. `inspect` traverses and decodes the complete recording; never use it as default discovery. Summary failures do not authorize full scans, recovery or local recording downloads.
