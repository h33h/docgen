# docgen

Generate structured DOCX documents and PPTX presentations from validated JSON configurations.

`docgen` provides a small CLI and Python API for data-driven document generation without assumptions about organization, subject, or document category.

## What it does

- Builds DOCX files from ordered sections and reusable content blocks.
- Builds PPTX files from typed slide configurations.
- Generates bar, horizontal bar, pie and structure diagrams.
- Embeds external images and tables by stable resource IDs.
- Numbers `{{cite:id}}` citations by first use and creates a bibliography.
- Validates the complete project before writing output.
- Writes output atomically and cleans temporary chart files.

## Installation

Python 3.10 or newer is required.

```bash
python -m pip install .
```

For development:

```bash
python -m pip install -e '.[dev]'
python -m pytest
```

## Quick start

Create and build a minimal document:

```bash
docgen init ./my-document
docgen build ./my-document/document.json
```

Create and build a presentation:

```bash
docgen init ./my-slides --kind presentation
docgen build ./my-slides/presentation.json
```

Override the output path with `-o`:

```bash
docgen build ./my-document/document.json -o ./result.docx
```

## Document configuration

A minimal `document.json`:

```json
{
  "kind": "document",
  "output": "result.docx",
  "sections": [
    {
      "type": "content",
      "title": "Overview",
      "content": [
        {"type": "paragraph", "text": "Hello."}
      ]
    }
  ]
}
```

Unknown fields and invalid combinations are rejected. Relative paths are resolved from the directory containing the root configuration and cannot escape it.

### Sections

Documents contain an ordered `sections` array with three section types:

- `content` renders an optional title and content blocks;
- `toc` inserts a Word table-of-contents field;
- `bibliography` lists cited sources in first-use order.

A `content` section must provide exactly one of:

- `content`: an inline array of blocks;
- `content_file`: a relative path to a JSON file containing the same block array.

Example external section:

```json
{
  "type": "content",
  "title": "Results",
  "level": 1,
  "content_file": "content/results.json",
  "page_break_before": true
}
```

### Content blocks

Seven block types are supported:

- `paragraph`: text, alignment, bold, italic and spacing;
- `heading`: text, level 1–6, alignment and TOC inclusion;
- `bullet_list`: non-empty list of strings;
- `numbered_list`: non-empty list with optional `start`;
- `table`: a table resource `ref`;
- `figure`: a figure resource `ref` and optional width override;
- `page_break`: an explicit page break.

Example content file:

```json
[
  {"type": "heading", "text": "Measurements", "level": 2},
  {"type": "paragraph", "text": "The result is reproducible {{cite:source-a}}."},
  {"type": "table", "ref": "measurements"},
  {"type": "figure", "ref": "trend"},
  {"type": "page_break"}
]
```

### Resources

Tables and figures live in the root `resources` object and have unique IDs:

```json
{
  "resources": {
    "tables": [
      {
        "id": "measurements",
        "headers": ["Sample", "Value"],
        "rows": [["A", "10"], ["B", "14"]],
        "caption": "Measurements"
      }
    ],
    "figures": [
      {
        "id": "trend",
        "type": "bar",
        "labels": ["A", "B"],
        "values": [10, 14],
        "caption": "Measured values"
      }
    ]
  }
}
```

Figure types are `image`, `bar`, `horizontal_bar`, `pie` and `structure`. An `image` uses a project-relative `path`; charts use validated data and options.

### Citations and bibliography

References contain user-formatted text. `docgen` does not impose a bibliography style.

```json
{
  "references": [
    {"id": "source-a", "text": "Author. Source title. 2025."}
  ],
  "sections": [
    {
      "type": "content",
      "content": [
        {"type": "paragraph", "text": "A claim {{cite:source-a}}."}
      ]
    },
    {"type": "bibliography", "title": "Sources"}
  ]
}
```

The first citation becomes `[1]`; repeated citations retain their number. Only used references are rendered.

### Formatting

Neutral defaults are A4, 2 cm margins, Arial 11 pt, 1.15 line spacing and no page number. The `formatting` object can override:

- A4/Letter and portrait/landscape;
- four margins;
- body font and heading sizes 1–6;
- line spacing, paragraph indent and spacing;
- page numbers in the header or footer.

Metadata supports `title`, `author`, `subject`, `keywords`, `comments` and `category` as DOCX properties.

## Presentation configuration

A minimal `presentation.json`:

```json
{
  "kind": "presentation",
  "title": "Demo",
  "slides": [
    {"type": "title"},
    {"type": "text", "title": "One", "text": "Hello."}
  ]
}
```

Themes are `classic` and `modern`. Slide types are `title`, `contents`, `text`, `bullets`, `two_column`, `table`, `figure`, `sources` and `thanks`. Table and figure slides reference the same typed resources used by documents.

## CLI reference

```text
docgen init PATH [--kind document|presentation]
docgen build CONFIG [-o OUTPUT]
docgen --help
docgen --version
python -m docgen ...
```

`build` always validates before rendering. Success returns exit code 0; configuration or generation errors return 1; CLI syntax errors return 2.

## Development

Runtime code is in `docgen/`; automated tests are in `tests/`.

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m compileall -q docgen
```

See `AGENTS.md` for architecture, change routing and repository-specific agent guidance.

## Known limitations

- Word or LibreOffice may need to refresh the TOC field after opening a DOCX.
- OOXML tests cannot guarantee visual layout; inspect formatting changes in an office application.
- Formulas, footnotes, arbitrary HTML and Markdown rendering are not supported.
- Citation text is numbered but not reformatted into a particular bibliography standard.
