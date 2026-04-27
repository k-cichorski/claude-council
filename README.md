# council

Multi-perspective deliberation for Claude Code. A leader orchestrates parallel-subagent council members through structured research → critique → consensus rounds, then drives implementation through `superpowers:writing-plans` + `executing-plans` with per-phase checkpoints.

## Install

```
/plugin marketplace add github.com/k-cichorski/claude-council
/plugin install council@council
```

Restart Claude Code (or `/plugins reload`). The `/council` slash command and the `council-architect` / `council-skeptic` / `council-user-advocate` agent types should appear.

## Quick start

```
/council <brief>            # start a new deliberation
/council                    # interactive: leader prompts for brief
/council --resume <slug>    # resume an interrupted council
/council --list             # show .council/INDEX.md
```

Full usage, lifecycle, and the smoke-test runbook are documented in [`.claude-plugin/README.md`](.claude-plugin/README.md).

## Repo layout

```
.
├── .claude-plugin/          # the plugin (commands, skills, agents, library)
│   ├── marketplace.json     # marketplace manifest (lists this plugin)
│   ├── plugin.json          # plugin manifest
│   ├── commands/            # /council slash command
│   ├── skills/              # using-council orchestration skill + helpers
│   ├── agents/              # 3 fixed-core member personas
│   └── library/
│       ├── specialists/     # 29 curated specialist personas
│       └── templates/       # 6 prompt/output templates
└── tests/                   # pytest suite (developer-facing, not shipped)
```

## Development

```bash
python -m venv venv
venv/bin/pip install pytest
venv/bin/pytest tests/ -v
```

47 tests covering helper round-trips, schema validation, structural consistency of templates / agents / specialists / skill, and command/manifest correctness.

## License

MIT
