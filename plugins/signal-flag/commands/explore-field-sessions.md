---
description: Explore session folders from the open Chrome tab, prepare customer metrics and evaluate with approval, or add SQL metrics to existing evaluations.
argument-hint: "[what to inspect, evaluate or add]"
---

Run this plugin command directly; do not delegate to an MCP slash command.
Load the `explore-field-sessions` skill with `get_skill` from the configured
Signal Flag MCP server. The served copy is the workflow's source of truth;
follow it with `$ARGUMENTS` as the request, or the current user request when
arguments are empty. Discover the session/folder from Chrome as the skill directs.

The default server name is `signal-flag`. If several configured Signal Flag
accounts are available, use the one matching the connected app tab. Preserve
existing account mappings. Verify `whoami` before project work.

Registered-session metadata, folder inventory, identity and Foxglove-link tools
need no local reader install. MCAP channels/schemas/values require an available
reader runtime. Before native recording
inspection, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/setup_reader.py" --check`.
If the bundled runtime is missing, use `/signal-flag:setup-reader` for explicit
setup and use its returned Python path. Do not install the Linux SDK on macOS or
assume a rerun checkout/PYTHONPATH exists. An unavailable reader or blocked remote
transport remains an inspection limit, not permission to bypass local controls.

If the server is unavailable, report its configured name/endpoint and that it
needs connecting and OAuth login as the app's organization member. If the skill
is not served, identify the connected environment and the missing skill. Do not
invent the old field-session tools or reproduce the workflow from memory.

Before any AWS writes or image push, verify the effective AWS identity read-only using an available AWS MCP identity tool, or `aws sts get-caller-identity` if the AWS CLI is available and demonstrably uses the same profile and effective credentials as the AWS/Finch MCP publication tools. Do not assume the CLI and MCP share credentials. Show the returned account ID and caller/role ARN, the actual profile (or explicitly identified credential source when no named profile is used), region, and full destination registry/repository URI. Ask the person to confirm that identity and destination explicitly, and wait for their answer before writes or publication. If the destination registry belongs to another account, show both caller and destination account IDs explicitly; an authorized cross-account push is valid. Reuse explicit confirmation only while the verified identity, credential source, region and destination remain unchanged. Existing login, a default profile, or a registry URI alone proves neither effective identity nor approval. If the identity cannot be verified for the publication tools, report the blocker; do not publish. A change to account, role, profile/credential source, region, or destination invalidates the confirmation and requires renewed verification and confirmation.

Prepare and test the concrete image before requesting publication confirmation when those steps need no AWS writes. After confirmation, the agent still builds/pushes through the customer's authorized AWS MCP capabilities and verifies the remote publication; do not replace that work with manual push instructions or a disallowed local fallback. This publication confirmation is separate from evaluation approval: evaluation requires the human's client permission prompt and matching confirmation. Never add an allowlist rule, change permissions, or bypass either approval.
