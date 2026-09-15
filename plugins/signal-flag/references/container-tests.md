# Test the metrics job through Finch MCP

Use this route when the connected Finch MCP can build images but has no container
execution tool. SDK tests run inside a Linux build stage through explicit `RUN`
instructions. An `ENTRYPOINT` declaration alone is not executed during a build.
Native reader setup does not install or test the Linux SDK.

## Prepare the test stage

Keep one shared `job` stage containing the exact production job, config and
analysis dependencies. Derive separate `test` and `runtime` stages from it:

```dockerfile
FROM public.ecr.aws/resim/open-builds/field-sessions@sha256:68029e0a856cd5aa23471d2aa74f1717b4eb5dc0c9795a0c2444f3a98c78a7c2 AS job
WORKDIR /app
COPY job.py config.resim.yml ./
# Add explicit COPY instructions for the job's inspected analysis dependencies.
ENTRYPOINT ["python", "/app/job.py"]

FROM job AS test
COPY tests/make_fixture.py tests/check_emissions.py /checks/
RUN python -c "from resim.sdk.metrics.emissions import Emitter" \
    && python /checks/make_fixture.py /tmp/resim/inputs/experience \
    && python /app/job.py \
    && python /checks/check_emissions.py /app/config.resim.yml /tmp/resim/outputs/emissions.resim.jsonl

FROM job AS runtime
```

This is a stage pattern, not a bundled test suite: author and review the two
test scripts for the actual job before building. The digest is a published
reader/Emitter base; use the verified base selected by the served workflow if
that version has changed. Do not replace it with an unverified mutable tag.

`make_fixture.py` must generate small synthetic recordings at the supplied folder
path, including nested recording keys and representative boundary cases. It
must not download customer recordings. The explicit `python /app/job.py` command
matches this image's entrypoint and uses the normal ReSim input/output paths.
If the real entrypoint has different arguments or a wrapper, execute that exact
command instead; include the same profile/environment selection as publication.

`check_emissions.py` must exit nonzero on missing, empty or malformed output and
check the actual JSONL emitted by the real SDK against the baked config and
known synthetic inputs. Cover:

- Declared topic names and types, with expected row counts and values for each
  intended emitted signal; merely parsing JSON is insufficient.
- `session_inventory` exact decimal-string nanoseconds and complete recording
  arrays, including relative nested keys and recording boundaries.
- Event rows' event metadata, recording key and exact integer timestamp, plus
  the expected event/no-event cases for the fixture.
- Invalid or unsupported input failing visibly and leaving no successful
  partial output, using additional entrypoint invocations where needed.

Do not substitute a mocked Emitter or skip the SDK checks when its import fails.
For a pytest-based suite, require the intended tests to be collected and executed,
with no SDK skips. Use assertions that fail for the known bad cases. Keep test
dependencies and generated data confined to the `test` stage. Restrict the build
context to the reviewed job, required source and synthetic tests; do not copy
credentials or a full customer checkout into it.

## Build and inspect the result

Discover the connected tool's actual schema. For the official Finch tool, replace
these example absolute paths with the prepared context visible to that MCP server:

```json
{
  "dockerfile_path": "/absolute/path/to/metrics-build/Dockerfile",
  "context_path": "/absolute/path/to/metrics-build",
  "target": "test",
  "platforms": ["linux/amd64"],
  "no_cache": true,
  "quiet": false,
  "progress": "plain"
}
```

Call `finch_build_container_image` with these arguments. Inspect its result and
build output for the actual fixture generation, entrypoint execution and passing
assertions. Preserve the successful command/test summary and the exact source
and base version tested. Missing logs, a tool error, a skipped test or a cached
ordinary build is not evidence of successful execution. The documented tool does
not expose `build_args`; do not invent that argument.

Some Finch versions omit build stdout on success. For those versions, have the
test runner capture combined command output in `/test-results/log.txt`, propagate
every command failure, and write a success receipt only after all intended
assertions execute and pass. Include the executed commands, source/config hashes
and log hash. Export just those files through an additional stage before the
final runtime stage:

```dockerfile
FROM scratch AS test-results
COPY --from=test /test-results/ /
```

Build `target: "test-results"` with `no_cache: true` and
`outputs: "type=local,dest=<fresh-owned-host-results-directory>"`. The official
[server schema](https://github.com/awslabs/mcp/blob/main/src/finch-mcp-server/awslabs/finch_mcp_server/server.py)
defines `outputs` as a string; follow the connected tool's actual schema.
On macOS, choose a destination inside a directory already shared with the Finch
VM, such as the customer workspace. Generic `/tmp` is VM-local in the default
Finch mounts; no output-path rewrite makes it host-visible. Do not alter mounts
to retrieve test results. Read the exported receipt and complete log, verify the hashes and passing checks,
and require a fresh destination for each attempt. Export/readback failure remains
missing test evidence. Do not infer execution from the tool's generic success
message or an old receipt.

After the test target passes, build `target: "runtime"` from the same unchanged
context and base, with the customer's intended image tag. The runtime stage
excludes test scripts, fixtures and generated output. Building it does not rerun
the sibling test stage. Any job/config/dependency change requires another test
build. Publish the runtime image through the existing customer AWS MCP path and
verify its registry digest before build registration. Testing does not approve
an evaluation or prove behavior on all customer data.

If this MCP build capability is unavailable or denied, report that specific
blocker. Do not switch to disallowed daemon/socket commands or change sandbox
policy. This recipe needs no local SDK installation or real recording copy.

Sources: [Finch MCP build tool](https://awslabs.github.io/mcp/servers/finch-mcp-server),
[Dockerfile RUN and ENTRYPOINT](https://docs.docker.com/reference/dockerfile/),
[named build stages](https://docs.docker.com/build/building/multi-stage/).
