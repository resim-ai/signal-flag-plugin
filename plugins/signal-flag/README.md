# Signal Flag

Create new metrics over data already available in your ReSim datalake. This plugin supplies a command; the connected ReSim MCP environment serves the workflow.

## Use

`/signal-flag:explore-field-sessions [metric request or session link]` loads `explore-field-sessions` through `get_skill`. The served resource `resim://skills/explore-field-sessions/SKILL.md` exposes the same instructions.

Connect the MCP endpoint for the intended ReSim environment and authenticate with the organization account that owns the data. Preserve existing account mappings. When a request refers to the web app, connect your signed-in Chrome tab and verify that its environment matches the MCP identity. Explicit links and IDs can supply context without a browser.

The workflow checks existing topics and data, proposes new metric names, previews against a compatible existing instance, and prepares grouped review in the existing metric editor. Saved edits and decisions remain authoritative. Publishing reusable configuration does not add charts to a historical instance or run an evaluation; instance-only additions use the existing Add Metric flow.

If required fields are missing, the workflow reports that limitation. If data exists but no compatible rendered preview is available, it can prepare a draft with that limitation disclosed. It does not inspect recordings or source repositories, install readers, register sessions, develop emissions, publish images or launch evaluations.

## Installation and development

Install from the public `resim-ai/signal-flag-plugin` marketplace using its root README. No ReSim source checkout, Python runtime or AWS MCP connection is required.

For local development, load this plugin without changing installed plugins or MCP mappings:

```bash
claude --chrome --plugin-dir ./plugins/signal-flag
```

Validate the plugin with `claude plugin validate ./plugins/signal-flag`. A missing server or served skill is a connection/deployment problem, not permission to reconstruct the removed workflow.
