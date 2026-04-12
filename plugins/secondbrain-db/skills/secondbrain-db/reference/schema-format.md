# Schema Format Reference

Schemas are YAML files in `schemas/` that define entity types.

## Structure

```yaml
version: 1
entity: <name>                    # entity name
docs_dir: <path>                  # where .md files live
filename: "{field}.md"            # filename template
records_dir: <path>               # where records.yaml lives
partition: none                   # "none" or "monthly"
date_field: <field>               # required when partition=monthly
id_field: <field>                 # primary key (default: "id")
integrity: strict                 # "strict", "warn", "off"

fields:
  <name>: { type: <type>, required: <bool>, default: <value> }

virtuals:
  <name>:
    returns: <type>
    source: |
      def compute(content, fields):
          return ...
```

## Field types

| Type | Stored in | Example |
|------|-----------|---------|
| `string` | frontmatter + records | `{ type: string, required: true }` |
| `int` | frontmatter + records | `{ type: int, default: 0 }` |
| `float` | frontmatter + records | `{ type: float }` |
| `bool` | frontmatter + records | `{ type: bool, default: false }` |
| `date` | frontmatter + records | `{ type: date, required: true }` |
| `datetime` | frontmatter + records | `{ type: datetime }` |
| `enum` | frontmatter + records | `{ type: enum, values: [a, b, c] }` |
| `ref` | frontmatter + records | `{ type: ref, entity: adrs }` |
| `list` | frontmatter only | `{ type: list, items: { type: string } }` |
| `object` | frontmatter only | `{ type: object, fields: { ... } }` |

**Scalar types** → stored in both frontmatter AND records.yaml → queryable without file I/O.
**Complex types** → stored in frontmatter only → require `--load-content` to query.

## ref type

Creates edges in the knowledge graph:

```yaml
fields:
  parent: { type: ref, entity: notes }              # single ref
  related: { type: list, items: { type: ref, entity: adrs } }  # list of refs
```

## Virtual fields

Starlark functions computed from content. Sandboxed: no I/O, no imports.

```yaml
virtuals:
  title:
    returns: string
    source: |
      def compute(content, fields):
          for line in content.splitlines():
              if line.startswith("# "):
                  return line.removeprefix("# ").strip()
          return fields["id"]

  ticket_refs:
    returns: list[string]
    edge: true                    # creates KG edges from returned values
    edge_entity: tickets          # target entity
    source: |
      def compute(content, fields):
          return re.findall("[A-Z]+-[0-9]+", content)
```

Available builtins: `re.findall(pattern, text)`, all Python string methods.

**Scalar return** (`string`, `int`, `float`, `bool`) → stored in both frontmatter + records.
**Complex return** (`list[string]`, etc.) → frontmatter only.
