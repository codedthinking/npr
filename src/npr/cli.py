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

def create_jinja_env(template_dir: Path) -> Environment:
    """Create a Jinja environment with the correct template loader."""
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True
    )

def get_template(template_dir: Path, template_name: str) -> jinja2.Template:
    """Get a template from the template directory."""
    env = create_jinja_env(template_dir)
    return env.get_template(template_name)

# dataclass of a Tool object, with name, description, list of paths to create and a list of gitignore lines
# there is also an f string that uses variables from the class, which will be run in the shell upon initializing the tools
@dataclass
class Tool:
    gitignore: List[str]
    init: str = field(default="")
    inside_folder: bool = field(default=True)
    templates: Path

@dataclass
class Project:
    path: Path
    name: str
    tools: List[Tool]
    title: str = ""
    description: str = ""
    authors: List[str] = field(default_factory=list)
    stata_version: str = "18"

def init_project(project):
    gitignore = []
    for tool in project.tools:
        gitignore.extend(tool.gitignore)

    for tool in project.tools:
        if tool.inside_folder:
            subprocess.run(tool.init.format(project=project).split(), cwd=project.name, check=True)
        else:
            subprocess.run(tool.init.format(project=project).split(), check=True)

    # Create .gitignore
    with open(f'{project.name}/.gitignore', 'w') as f:
        f.write('\n'.join(gitignore))

    # Generate README.md and Makefile from templates
    template_dir = get_template_dir()
    project_template_dir = template_dir / 'project'
    
    # Render README.md template
    readme_template = get_template(project_template_dir, 'README.md')
    readme_content = readme_template.render(project=project)
    with open(f'{project.name}/README.md', 'w') as f:
        f.write(readme_content)
    
    # Copy Makefile
    makefile_template = get_template(project_template_dir, 'Makefile')
    makefile_content = makefile_template.render(project=project)
    with open(f'{project.name}/Makefile', 'w') as f:
        f.write(makefile_content)


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

git = Tool([], 'git init', inside_folder=True, templates=template_dir/'git')
bead = Tool(['input/', 'temp/'], 'bead new {project.name}', inside_folder=False, templates=template_dir/'bead')
poetry = Tool(['poetry.lock'], 'poetry init', inside_folder=True, templates=template_dir/'poetry')
julia = Tool(['Manifest.toml'], 'julia --project=. -e "using Pkg; Pkg.instantiate()"', inside_folder=True, templates=template_dir/'julia')
@click.command()
@click.option('--path', '-p', default='.',
              help='Path where project will be created',
              type=click.Path())
def main(path: str):
    template_dir = get_template_dir()
    # list of Tool objects

    """Create a new project directory and initialize git."""
    try:
        print_welcome()

        # Get project details
        name = Prompt.ask(
            "[bold cyan]Project name[/bold cyan]",
            default="my-project"
        )
        
        title = Prompt.ask(
            "[bold cyan]Project title[/bold cyan]",
            default=name
        )
        
        description = Prompt.ask(
            "[bold cyan]Project description[/bold cyan]",
            default=""
        )
        
        authors = []
        console.print("\n[bold cyan]Authors (press Enter on empty line to finish):[/bold cyan]")
        while True:
            author = Prompt.ask("Author name", default="")
            if not author:
                break
            authors.append(author)

        # Create project using bead (which creates the directory structure)
        # Convert path to Path object
        path = Path(path)
        new_project = Project(path, name, [bead, git], title, description, authors)
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
