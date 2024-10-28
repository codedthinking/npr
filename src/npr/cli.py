import subprocess
from pathlib import Path
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
import jinja2
from dataclasses import dataclass, field
from typing import List
from importlib import resources
from jinja2 import Environment, FileSystemLoader

def get_template_dir() -> Path:
    """Get the template directory path that works both in development and after installation."""
    try:
        # Python 3.9+, without using context manager
        template_dir = resources.files('npr').joinpath('templates')
        return Path(template_dir)
    except AttributeError:
        # Fallback for older Python versions
        import pkg_resources
        return Path(pkg_resources.resource_filename('npr', 'templates'))

def create_jinja_env() -> Environment:
    """Create a Jinja environment with the correct template loader."""
    template_dir = get_template_dir()
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True
    )

def render_template(template_name: str, **kwargs) -> str:
    """Render a template with the given variables."""
    env = create_jinja_env()
    template = env.get_template(template_name)
    return template.render(**kwargs)

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

def init_project(project):
    gitignore = []
    for tool in project.tools:
        gitignore.extend(tool.gitignore)

    for tool in project.tools:
        if tool.inside_folder:
            subprocess.run(tool.init.format(name=project.name).split(), cwd=project.name, check=True)
        else:
            subprocess.run(tool.init.format(name=project.name).split(), check=True)

    with open(f'{project.name}/.gitignore', 'w') as f:
        f.write('\n'.join(gitignore))


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

# list of Tool objects
git = Tool([], 'git init', inside_folder=True)
bead = Tool(['input/', 'temp/'], 'bead new {name}', inside_folder=False)
poetry = Tool(['poetry.lock'], 'poetry init', inside_folder=True)
julia = Tool(['Manifest.toml'], 'julia --project=. -e "using Pkg; Pkg.instantiate()"', inside_folder=True)


@click.command()
@click.option('--path', '-p', default='.',
              help='Path where project will be created',
              type=click.Path())
def main(path: str):
    print(
        get_template_dir()
    )
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
        new_project = Project(path, name, [bead, git])
        init_project(new_project)

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
