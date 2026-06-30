# Copyright (C) 2024 DocScan Team
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
cli.py — DocScan CLI entry point.
Usage: docscan scan <file> [--schema receipt|medical|generic] [--output out.json]
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from docscan.extractor import extract_text
from docscan.inference import run_inference
from docscan.schemas import SchemaName

app = typer.Typer(
    name="docscan",
    help="Offline-first structured data extraction from documents. CPU only.",
    add_completion=False,
)
console = Console()


@app.command()
def scan(  # type: ignore[no-untyped-def]
    file: Path = typer.Argument(..., help="Path to PDF, image, or TXT file"),
    schema: SchemaName = typer.Option(
        SchemaName.generic, "--schema", "-s", help="Output schema: receipt | medical | generic"
    ),
    output: Path = typer.Option(
        None, "--output", "-o", help="Write JSON output to this file instead of stdout"
    ),
    model: Path = typer.Option(
        Path("models/phi3-mini-q4.gguf"), "--model", "-m", help="Path to GGUF model file"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show extracted text"),
):
    """Extract structured JSON from a document. Runs fully offline."""

    if not file.exists():
        console.print(f"[red]File not found:[/red] {file}")
        raise typer.Exit(1)

    with console.status(f"[cyan]Extracting text from {file.name}..."):
        try:
            text = extract_text(file)
        except Exception as e:
            console.print(f"[red]Extraction failed:[/red] {e}")
            raise typer.Exit(1)

    if verbose:
        console.print(
            Panel(
                text[:1000] + ("..." if len(text) > 1000 else ""),
                title="Extracted Text",
                border_style="dim",
            )
        )

    console.print(f"[green]OK[/green] Extracted {len(text)} characters")

    with console.status("[cyan]Running local inference (CPU)... this may take 10-30s"):
        try:
            result = run_inference(text, schema, model_path=model)
        except FileNotFoundError as e:
            console.print(f"[red]Model not found:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Inference failed:[/red] {e}")
            raise typer.Exit(1)

    console.print(f"[green]OK[/green] Inference complete -- schema: [bold]{schema.value}[/bold]")

    json_str = json.dumps(result, indent=2)

    if output:
        output.write_text(json_str, encoding="utf-8")
        console.print(f"[green]OK[/green] Saved to {output}")
    else:
        console.print(Syntax(json_str, "json", theme="monokai"))


@app.command()
def version() -> None:
    """Print version info."""
    console.print("[bold]DocScan CLI[/bold] v0.1.0 - CPU-first, offline-first")


if __name__ == "__main__":
    app()
