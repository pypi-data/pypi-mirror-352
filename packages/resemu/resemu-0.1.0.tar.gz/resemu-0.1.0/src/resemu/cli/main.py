from pathlib import Path
from importlib.metadata import version as get_version
from importlib.metadata import PackageNotFoundError

import typer
import yaml
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table

from resemu.models.resume import Resume
from resemu.generators.latex import generate_latex
from resemu.generators.pdf import compile_pdf

app = typer.Typer(
    name="resemu",
    help="Generate solid resumes from YAML data.",
    rich_markup_mode="rich",
)
console = Console()


@app.command()
def generate(
    data_file: Path = typer.Argument(
        ...,
        help="YAML file containing resume data",
    ),
    template: str = typer.Option(
        "engineering",
        "--template",
        "-t",
        help="Resume template to use",
        rich_help_panel="Template Options",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (defaults to input filename with .pdf extension)",
        rich_help_panel="Output Options",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing output file without confirmation",
        rich_help_panel="Output Options",
    ),
) -> None:
    """
    [bold green]Generate a PDF resume from a YAML data file.[/bold green]

    This command processes your YAML resume data and generates a clean PDF using the specified template.
    """
    if not data_file.exists():
        console.print(f"[bold red]❌ Error:[/bold red] File '{data_file}' not found", style="red")
        raise typer.Exit(1)

    output_path = output or data_file.with_suffix(".pdf")

    if output_path.exists() and not force:
        if not Confirm.ask(
            f"Output file '{output_path}' already exists. Overwrite?",
            default=False,
        ):
            console.print("[yellow]Operation cancelled[/yellow]")
            raise typer.Exit(0)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            # Load and validate YAML
            task = progress.add_task("[cyan]Loading YAML data...", total=100)
            with open(data_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            progress.update(task, advance=25)

            # Validate data structure
            progress.update(task, description="[cyan]Validating data structure...")
            resume = Resume(**data)
            progress.update(task, advance=25)

            # Generate LaTeX
            progress.update(task, description="[cyan]Generating LaTeX content...")
            latex_content = generate_latex(resume, template)
            progress.update(task, advance=25)

            # Compile PDF
            progress.update(task, description="[cyan]Compiling PDF...")
            pdf_path = compile_pdf(latex_content, output_path)
            progress.update(task, advance=25)

        success_panel = Panel(
            f"[bold green]✅ Resume generated successfully![/bold green]\n\n"
            f"📄 Template: [bold]{template}[/bold]\n"
            f"📁 Output: [bold blue]{pdf_path}[/bold blue]\n"
            f"📊 Size: {pdf_path.stat().st_size / 1024:.1f} KB",
            title="[bold green]Generation Complete[/bold green]",
            border_style="green",
        )
        console.print(success_panel)

    except yaml.YAMLError as e:
        console.print(f"[bold red]❌ YAML error:[/bold red] {e}", style="red")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Generation error:[/bold red] {e}", style="red")
        raise typer.Exit(1)


@app.command()
def validate(
    data_file: Path = typer.Argument(
        ...,
        help="YAML file to validate",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation information",
    ),
) -> None:
    """
    [bold blue]Validate a YAML resume data file.[/bold blue]

    Checks if your YAML file is properly formatted and contains all required fields.
    """
    if not data_file.exists():
        console.print(f"[bold red]❌ Error:[/bold red] File '{data_file}' not found", style="red")
        raise typer.Exit(1)

    try:
        with console.status("[bold blue]Validating YAML file...", spinner="dots"):
            with open(data_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            resume = Resume(**data)

        if verbose:
            console.print(make_verbose_resume_table(resume))

        success_panel = Panel(
            f"[bold green]✅ YAML file is valid![/bold green]\n\n"
            f"📄 File: [bold blue]{data_file}[/bold blue]\n"
            f"📊 Size: {data_file.stat().st_size / 1024:.1f} KB",
            title="[bold green]Validation Success[/bold green]",
            border_style="green",
        )
        console.print(success_panel)

    except yaml.YAMLError as e:
        error_panel = Panel(
            f"[bold red]YAML parsing error:[/bold red]\n{e}",
            title="[bold red]Validation Failed[/bold red]",
            border_style="red",
        )
        console.print(error_panel)
        raise typer.Exit(1)
    except Exception as e:
        error_panel = Panel(
            f"[bold red]Validation error:[/bold red]\n{e}",
            title="[bold red]Validation Failed[/bold red]",
            border_style="red",
        )
        console.print(error_panel)
        raise typer.Exit(1)


@app.command()
def templates() -> None:
    """
    [bold magenta]List available resume templates.[/bold magenta]

    Shows all available templates you can use with the generate command.
    """
    available_templates = [
        ("engineering", "Technical/Software Engineering focused resume"),
    ]

    table = Table(title="Available Templates", show_header=True, header_style="bold magenta")
    table.add_column("Template", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")

    for template, description in available_templates:
        table.add_row(template, description)

    console.print(table)
    console.print(
        "\n[dim]Use: [bold]resemu generate data.yaml --template TEMPLATE_NAME[/bold][/dim]"
    )


@app.command()
def version() -> None:
    """Show version information."""
    try:
        __version__ = get_version("resemu")
    except PackageNotFoundError:
        __version__ = "unknown"

    console.print(f"[bold blue]resemu[/bold blue] version [bold green]{__version__}[/bold green]")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """
    📄 [bold blue]resemu - Simple resume generator[/bold blue]

    Generate solid PDF resumes from YAML data files using LaTeX templates.
    """
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold blue]Welcome to resemu![/bold blue] 🎯\n\n"
                "To get started:\n\n"
                "• [bold]resemu generate resume.yaml[/bold] - Generate a PDF\n"
                "• [bold]resemu validate resume.yaml[/bold] - Validate your YAML\n"
                "• [bold]resemu templates[/bold] - List available templates\n"
                "• [bold]resemu version[/bold] - Show version\n"
                "• [bold]resemu --help[/bold] - Show detailed help\n\n"
                "[dim]Need help? Check the documentation or run any command with --help[/dim]",
                title="[bold green]Resume Generator[/bold green]",
                border_style="blue",
            )
        )


def make_verbose_resume_table(resume: Resume) -> Table:
    """Make a rich Table displaying resume info for use in validation verbose mode."""
    table = Table(title="Validation details", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Value/Count")

    table.add_row("Name", "✅", f"{resume.contact.name}")
    table.add_row(
        "Experience", "✅", f"{len(resume.experience) if resume.experience else 0} entries"
    )
    table.add_row("Education", "✅", f"{len(resume.education) if resume.education else 0} entries")
    table.add_row("Skills", "✅", f"{len(resume.skills) if resume.skills else 0} categories")

    return table


if __name__ == "__main__":
    app()
