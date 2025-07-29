"""A script to check that all functions defined in the source have a section in docs."""

import ast
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

SRC_DIR = Path("./src")
DOCS_DIR = Path("./docs")


def get_function_names_from_src(src_dir: Path) -> set[str]:
    """Get function names from a source directory."""
    functions = set()

    for py_file in src_dir.rglob("*.py"):
        with open(py_file, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(py_file))
            for node in tree.body:  # Ignore nested functions
                if isinstance(node, ast.FunctionDef):
                    functions.add(node.name)

    return functions


def get_documented_functions_from_docs(docs_dir: Path) -> set[str]:
    """Get the names of documented functions from the documentation files."""
    doc_pattern = re.compile(r"### \[`(\w+)`\]\[.*\.(\w+)\]")
    documented: set[str] = set()
    for md_file in docs_dir.rglob("*.md"):
        with open(md_file, encoding="utf-8") as f:
            content = f.read()
            matches = doc_pattern.findall(content)
            documented.update(name for _, name in matches)
    return documented


def main() -> None:
    """The entrypoint to the script."""
    all_functions = get_function_names_from_src(SRC_DIR)
    documented_functions = get_documented_functions_from_docs(DOCS_DIR)
    n_functions = len(all_functions)

    if not all_functions or not documented_functions:
        raise RuntimeError("❌ Parsed no functions.")

    undocumented = sorted(all_functions - documented_functions)

    if undocumented:
        logger.warning("❌ The following functions are missing documentation:")
        for func in undocumented:
            logger.warning(f"- {func}")
        sys.exit(1)
    else:
        logger.warning(f"✅ All {n_functions} functions are documented.")


if __name__ == "__main__":
    main()
