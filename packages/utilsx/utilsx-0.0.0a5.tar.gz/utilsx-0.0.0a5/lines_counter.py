"""A Python script to count the number of files and lines of code across the project.

Defines its own dependencies to be more standalone and further scalable to other
projects regardless of their virtual environments.

The easiest way to run this script is by using ``uv`` interface,
as described here https://docs.astral.sh/uv/guides/scripts/:

1. Install ``uv`` to your virtual environment or on your machine.
2. Run ``uv run lines_counter.py`` in terminal.
3. When finished, summary statistics will be available at your clipboard, so you can paste it
    to an Excel spreadsheet and format nicely.

Note: the section below (multiple inline comments) is not intended for manual changes.
    It was created with: https://docs.astral.sh/uv/guides/scripts/#creating-a-python-script
    May be changed via: https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pandas",
#     "pygount~=1.8.0",
#     "rich~=13.9.0",
#     "tabulate",
# ]
# ///

import typing as tp
from dataclasses import dataclass
from glob import glob
from time import sleep

import pandas as pd
from pygount import ProjectSummary, SourceAnalysis
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import track
from rich.text import Text

_COLOR_FOR_NUMBERS = "bold magenta"


@dataclass(frozen=True)
class ComponentToAnalyze:
    """Definition of a codebase component to analyze.

    Args:
        name: Human-readable component name, as you wish to report it.
        pathnames: An iterable of path names which contain code of this component.
    """

    name: str
    pathnames: tp.Iterable[str]


class AnalysisResult(tp.TypedDict):
    """A container for component analysis results, includes its name and metrics."""

    component: str
    file_count: int
    source_count: int
    documentation_count: int
    empty_count: int
    line_count: int


def _generate_summary_text(summary_df: pd.DataFrame) -> Text:
    """Given a summary dataframe, generate a text line summarizing it."""
    return Text.assemble(
        (f"{summary_df['line_count'].sum():,}", _COLOR_FOR_NUMBERS),
        " total lines, including",
        (f" {summary_df['source_count'].sum():,}", _COLOR_FOR_NUMBERS),
        " source lines, across",
        (f" {summary_df['file_count'].sum():,}", _COLOR_FOR_NUMBERS),
        " files.",
    )


_COMPONENTS = (
    ComponentToAnalyze(
        name="Source",
        pathnames=("./src/**/*.py",),
    ),
    ComponentToAnalyze(
        name="Docs",
        pathnames=(
            "./docs/**/*.md",
            "mkdocs.yml",
        ),
    ),
    ComponentToAnalyze(
        name="Tests",
        pathnames=("./tests/**/*.py",),
    ),
    ComponentToAnalyze(
        name="Developer tools",
        pathnames=(
            ".codespellrc",
            ".gitignore",
            ".pre-commit-config.yaml",
            "./.github/**/*.yml",
            "lines_counter.py",
            "Makefile",
            "mypy.ini",
            "pyproject.toml",
            "ruff.toml",
            ".vale.ini",
            "./.vale/styles/config/**/*.*",
            "./scripts/*.*",
            "LICENSE",
            "uv.lock",
        ),
    ),
)

console = Console()

results_by_components = []

for component in track(sequence=_COMPONENTS, description="Counting lines...", console=console):
    project_summary = ProjectSummary()

    for pathname in component.pathnames:
        for path in glob(pathname=pathname, recursive=True):
            source_analysis = SourceAnalysis.from_file(path, group="", encoding="utf-8")
            project_summary.add(source_analysis)

    component_result = AnalysisResult(
        component=component.name,
        file_count=project_summary.total_file_count,
        source_count=project_summary.total_source_count,
        documentation_count=project_summary.total_documentation_count,
        empty_count=project_summary.total_empty_count,
        line_count=project_summary.total_line_count,
    )
    results_by_components.append(component_result)
    sleep(0.1)

summary = (
    pd.DataFrame(results_by_components)
    .set_index("component")
    .sort_values(
        by="line_count",
        ascending=False,
    )
)
summary["avg_lines_per_file"] = round(summary["line_count"] / summary["file_count"])
as_markdown = Markdown(summary.to_markdown())
console.print(as_markdown)

summary_text = _generate_summary_text(summary)
console.print(summary_text)

summary.to_clipboard()
