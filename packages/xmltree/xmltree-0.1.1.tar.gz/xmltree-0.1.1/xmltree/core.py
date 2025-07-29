#!/usr/bin/env python3
"""Convert directory structures to XML format"""

import xml.etree.ElementTree as ET
from pathlib import Path

from .logger import get_logger

logger = get_logger(__name__)


def directory_to_xml(
    path: Path,
    ignore_patterns: list[str] | None = None,
    include_patterns: list[str] | None = None,
    respect_gitignore: bool = True,
    root_name: str | None = None,
    full_paths: bool = False,
) -> ET.Element:
    """Convert a directory structure to XML format.

    Args:
        path: Directory path to convert
        ignore_patterns: Patterns to exclude (glob patterns)
        include_patterns: Only include files matching these patterns
        respect_gitignore: Whether to respect .gitignore files
        root_name: Name for the root directory element
    """
    # Input validation
    assert isinstance(path, Path), f"Expected Path, got {type(path)}"
    assert path.exists(), f"Path does not exist: {path}"
    assert path.is_dir(), f"Path must be a directory: {path}"

    # Get gitignore patterns if needed
    gitignore_patterns = []
    if respect_gitignore:
        gitignore_patterns = parse_gitignore(path)

    # Create root directory element
    root_path = str(path.resolve()) if full_paths else str(path)
    root = ET.Element("directory", path=root_path)

    # Process the contents of the directory
    process_directory_contents(
        root, path, path, ignore_patterns, include_patterns, gitignore_patterns, full_paths
    )

    return root


def parse_gitignore(base_path: Path) -> list[str]:
    """Parse .gitignore file and return patterns."""
    gitignore_path = base_path / ".gitignore"
    if not gitignore_path.exists():
        return []

    patterns = []
    try:
        content = gitignore_path.read_text()
        for line in content.splitlines():
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                patterns.append(line)
    except Exception as e:
        logger.warning(f"Could not read .gitignore: {e}")

    return patterns


def should_ignore(path: Path, base_path: Path, ignore_patterns: list[str]) -> bool:
    """Check if path should be ignored based on patterns."""
    relative_path = path.relative_to(base_path)

    # Always ignore these
    if path.name in {".git", "__pycache__", ".DS_Store", "node_modules", ".venv", "venv"}:
        return True

    # Check against patterns
    for pattern in ignore_patterns:
        # Simple pattern matching (could be enhanced with fnmatch or pathspec)
        if pattern.endswith("/"):
            # Directory pattern
            if path.is_dir() and path.name == pattern.rstrip("/"):
                return True
        elif "*" in pattern:
            # Glob pattern - simple implementation
            import fnmatch

            if fnmatch.fnmatch(str(relative_path), pattern):
                return True
            if fnmatch.fnmatch(path.name, pattern):
                return True
        else:
            # Exact match
            if path.name == pattern or str(relative_path) == pattern:
                return True

    return False


def should_include(path: Path, include_patterns: list[str] | None) -> bool:
    """Check if path should be included based on patterns."""
    if not include_patterns or path.is_dir():
        return True

    import fnmatch

    for pattern in include_patterns:
        if fnmatch.fnmatch(path.name, pattern):
            return True
        if fnmatch.fnmatch(str(path), pattern):
            return True

    return False


def process_directory_contents(
    parent_element: ET.Element,
    current_path: Path,
    base_path: Path,
    ignore_patterns: list[str] | None,
    include_patterns: list[str] | None,
    gitignore_patterns: list[str],
    full_paths: bool = False,
) -> None:
    """Process contents of a directory without including the directory itself."""
    # Combine all ignore patterns
    all_ignore_patterns = (ignore_patterns or []) + gitignore_patterns

    # Get items in directory
    try:
        items = sorted(current_path.iterdir())
    except PermissionError:
        logger.warning(f"Permission denied: {current_path}")
        return

    # Process directories first, then files
    dirs = [item for item in items if item.is_dir()]
    files = [item for item in items if item.is_file()]

    for item in dirs + files:
        # Check if should ignore
        if should_ignore(item, base_path, all_ignore_patterns):
            continue

        # Check if should include
        if not should_include(item, include_patterns):
            continue

        # Make path relative or absolute based on full_paths option
        display_path = str(item.resolve()) if full_paths else str(item.relative_to(base_path))

        if item.is_dir():
            # Create directory element
            dir_elem = ET.SubElement(parent_element, "directory", path=display_path)
            # Recurse into directory
            process_directory_contents(
                dir_elem,
                item,
                base_path,
                ignore_patterns,
                include_patterns,
                gitignore_patterns,
                full_paths,
            )
        else:
            # Create file element
            file_elem = ET.SubElement(parent_element, "file", path=display_path)
            # Read and add file content
            try:
                content = item.read_text(encoding="utf-8")
                content_elem = ET.SubElement(file_elem, "content")
                # Use CDATA to preserve content exactly
                content_elem.text = content
            except Exception as e:
                logger.warning(f"Could not read file {item}: {e}")


def format_xml(root: ET.Element, pretty: bool = True) -> str:
    """Convert XML element to formatted string."""
    if pretty:
        # Add indentation
        indent_xml(root)

    # Convert to string with CDATA sections
    xml_str = ET.tostring(root, encoding="unicode", method="xml")

    # Wrap file contents in CDATA
    import re

    def wrap_content(match):
        content = match.group(1)
        return f"<content><![CDATA[\n{content}]]></content>"

    xml_str = re.sub(r"<content>(.*?)</content>", wrap_content, xml_str, flags=re.DOTALL)

    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str


def indent_xml(elem: ET.Element, level: int = 0) -> None:
    """Add indentation to XML for pretty printing."""
    indent = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent
