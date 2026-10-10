# Catalog

- `artifacts.json`: every source and output `.gmd`, with SHA-256, parsed/stored
  object counts, name, song and handoff status. The portable validator checks it.
- `migration.json`: every copied workspace file and every intentional exclusion.
  Original migration hashes are provenance, not a promise that subsequently
  improved documentation/scripts remain byte-identical. Exports are unchanged.
- `tooling-checks.json`: observed checks for this repository migration.

Do not ingest every multi-megabyte raw plan into an agent context. Use the curated
root/docs guides, then search the specific section or object example needed.

