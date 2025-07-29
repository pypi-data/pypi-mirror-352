# xmltree

Full file(content) tree → XML

## Installation

```bash
# Install globally with uv (recommended)
uv tool install xmltree

# Or use directly without installing
uvx xmltree

# Or install with pipx
pipx install xmltree
```


## Usage

```bash
# Convert current directory
xmltree

# Convert specific directory
xmltree /path/to/project

# Save to file
xmltree -o project.xml

# Only include specific file types
xmltree -I "*.py" -I "*.md"

# Exclude additional patterns  
xmltree -i "*.log" -i "temp/*"

# Show absolute paths
xmltree --full-paths

# Compact output
xmltree --compact
```

## Example

Given a project structure:
```
example_project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── utils/
│       └── helpers.py
├── tests/
│   └── test_main.py
├── .gitignore
├── README.md
└── pyproject.toml
```

Running `xmltree example_project` produces:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<directory path="example_project">
  <directory path="src">
    <file path="src/__init__.py">
      <content><![CDATA[
"""Example package."""

__version__ = "0.1.0"]]></content>
    </file>
    <!-- ... more files ... -->
  </directory>
  <file path="README.md">
    <content><![CDATA[
# Example Project

This is a sample project to demonstrate xmltree.]]></content>
  </file>
</directory>
```

## Features

- Converts directory structures to well-formed XML
- Respects `.gitignore` files by default
- Supports custom ignore and include patterns
- Pretty-printed output by default
- File contents wrapped in CDATA sections
- Pipe-friendly for use with other tools

## Why XML?

XML's explicit closing tags make structure unambiguous, unlike YAML's error-prone indentation. 
File contents can be wrapped in CDATA sections preserving exact formatting, while JSON would require escaping every quote and newline.

