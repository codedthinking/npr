import subprocess
from pathlib import Path
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
import jinja2
from dataclasses import dataclass, field
from typing import List

console = Console()

# dataclass of a Tool object, with name, description, list of paths to create and a list of gitignore lines
# there is also an f string that uses variables from the class, which will be run in the shell upon initializing the tools
@dataclass
class Tool:
    gitignore: List[str]
    init: str = field(default="")
    inside_folder: bool = field(default=True)
    template: jinja2.Template = field(init=False)

@dataclass
class Project:
    path: Path
    name: str
    tools: List[Tool]

# list of Tool objects
project = Tool([], 'mkdir -p {name}', inside_folder=False)
git = Tool([], 'git init', inside_folder=True)
bead = Tool(['input/', 'temp/'], 'bead new {name}', inside_folder=False)
poetry = Tool(['poetry.lock'], 'poetry init', inside_folder=True)
julia = Tool(['Manifest.toml'], 'julia --project=. -e "using Pkg; Pkg.instantiate()"', inside_folder=True)

def add_tool(project, tool):
    '''
    Add a tool to the project. If `inside_folder`, change to `name` and then run the `init` command of the tool. Add the list in `gitignore` to `name/.gitignore`.
    '''
    project.tools.append(tool)
    commands = []
    if tool.inside_folder:
        commands.append(f'cd {project.name}')
    commands.append(tool.init)
    subprocess.run(' && '.join(commands), check=True)
    with open(f'{project.name}/.gitignore', 'a') as f:
        f.write('\n'.join(tool.gitignore))

def print_welcome():
    """Display a welcome message."""
    welcome = Panel.fit(
        "[bold magenta]Project Initializer[/bold magenta]\n"
        "[cyan]Create a new project directory and initialize git[/cyan]",
        border_style="bright_blue"
    )
    console.print(welcome)
    console.print()

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
        # Convert path to Path object
        path = Path(path)
        new_project = Project(path, name, [project, git, bead])
        for tool in new_project.tools:
            add_tool(new_project, tool)

        # Success message
        console.print(f"\n[bold green]✓[/bold green] Project created at [cyan]{path / name}[/cyan]")

    except subprocess.CalledProcessError as e:
        console.print(f"\n[red]Error:[/red] Failed to initialize git repository")
        raise click.Abort()
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise click.Abort()

if __name__ == "__main__":
    main()
