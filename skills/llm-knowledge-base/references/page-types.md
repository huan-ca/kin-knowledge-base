# Page Types

Universal page types:

- `source`
- `concept`
- `procedure`
- `glossary-term`
- `decision`
- `open-question`
- `report`

Domain-specific page types come from `knowledge-base.yaml`.
If a recurring pattern does not fit the configured taxonomy, propose a candidate new type in `.kb-state/proposed-types.json` or a generated report rather than silently making it canonical.
Use the nearest configured type plus tags until a human approves the new type.
