import subprocess
from pathlib import Path
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def print_welcome():
    """Display a welcome message."""
    welcome = Panel.fit(
        "[bold magenta]Project Initializer[/bold magenta]\n"
        "[cyan]Create a new project directory and initialize git[/cyan]",
        border_style="bright_blue"
    )
    console.print(welcome)
    console.print()

def create_project(name: str, path: Path) -> None:
    """Create project directory and initialize git."""
    project_path = path / name
    
    # Create project directory
    project_path.mkdir(parents=True)
    
    # Initialize git
    subprocess.run(['git', 'init'], cwd=project_path, check=True)

@click.command()
@click.option('--path', '-p', default='.', 
              help='Path where project will be created',
              type=click.Path())
def main(path: str):
    """Create a new project directory and initialize git."""
    try:
        print_welcome()
        
        # Get project name
        name = Prompt.ask(
            "[bold cyan]Project name[/bold cyan]",
            default="my-project"
        )
        
        # Create project
        path = Path(path)
        with console.status("[bold green]Creating project...", spinner="dots"):
            create_project(name, path)
        
        # Success message
        console.print(f"\n[bold green]✓[/bold green] Project created at [cyan]{path / name}[/cyan]")
        
        # Show next steps
        next_steps = """
[bold cyan]Next steps:[/bold cyan]
1. [green]cd[/green] {0}
2. Start adding your project files!
""".format(name)
        
        console.print(Panel(next_steps, border_style="bright_blue"))
        
    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]Error:[/red] Failed to initialize git repository")
        raise click.Abort()
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise click.Abort()

if __name__ == "__main__":
    main()