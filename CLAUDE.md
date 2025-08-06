# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NPR (New Project Initializer) is a CLI tool that creates project directories and initializes them with various tools like git, bead, and poetry. It uses a template system with Jinja2 to generate project scaffolding.

## Development Commands

### Installation and Setup
```bash
# Install for development
poetry install

# Install globally with pipx
pipx install .
```

### Running the CLI
```bash
# Run directly
python -m npr.cli

# Run after installation
npr

# Run with custom path
npr --path /path/to/parent/directory
```

## Architecture

### Core Components

- **Tool System**: The `Tool` dataclass defines project initialization tools (git, bead, poetry, julia) with gitignore patterns, shell commands, and template directories
- **Template Engine**: Uses Jinja2 with FileSystemLoader to process template files from the `templates/` directory
- **CLI Interface**: Click-based command line interface with Rich for enhanced terminal output

### Template Structure
The `templates/` directory contains subdirectories for each tool:
- `bead/`: Bead data management templates 
- `git/`: Git initialization templates
- `poetry/`: Poetry project templates
- `project/`: Base project templates (README.md, Makefile)

### Key Flow
1. User runs `npr` and provides project name
2. Creates a `Project` object with selected tools (currently hardcoded to `[bead, git]`)
3. `init_project()` runs each tool's init command and combines gitignore patterns
4. Templates are processed but the current implementation has incomplete Jinja2 integration

### Package Structure
- Uses Poetry for dependency management
- Packaged with `src/` layout: `src/npr/`
- Templates included in package via `include = ["templates/**/*"]`
- Entry point: `npr = "npr.cli:main"`

## Key Dependencies

- **click**: CLI framework
- **rich**: Terminal formatting and prompts  
- **jinja2**: Template processing
- **poetry**: Build system and dependency management