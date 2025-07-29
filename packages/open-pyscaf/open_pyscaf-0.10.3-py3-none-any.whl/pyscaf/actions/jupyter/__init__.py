"""
Jupyter initialization actions.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Optional

import tomli
import tomli_w
from rich.console import Console

from pyscaf.actions import Action, CLIOption

console = Console()


class JupyterAction(Action):
    """Action to initialize Jupyter notebook support in a project."""

    depends = ["core"]
    run_preferably_after = "core"
    cli_options = [
        CLIOption(
            name="--jupyter",
            type="bool",
            help="Handle Jupyter notebook support",
            prompt="Does this project will use Jupyter notebook ?",
            default=True,
        ),
    ]  # Add Jupyter-specific options if needed

    def __init__(self, project_path):
        super().__init__(project_path)

    def activate(self, context: dict) -> bool:
        return context.get("jupyter") is None or context.get("jupyter", True)

    def skeleton(self, context: dict) -> Dict[Path, Optional[str]]:
        """
        Define the filesystem skeleton for Jupyter notebook support.

        Returns:
            Dictionary mapping paths to content
        """
        project_name = context.get("project_name", "myproject")

        # Read Jupyter documentation
        jupyter_doc_path = Path(__file__).parent / "README.md"
        jupyter_doc = jupyter_doc_path.read_text() if jupyter_doc_path.exists() else ""

        # Create a README for notebooks
        notebook_readme = f"""# {project_name} - Notebooks

This directory contains Jupyter notebooks for the {project_name} project.

{jupyter_doc}
"""

        # Create .gitignore for notebooks to ignore checkpoints
        gitignore_content = """# Jupyter Notebook
.ipynb_checkpoints
*/.ipynb_checkpoints/*

# IPython
profile_default/
ipython_config.py
"""

        # Return skeleton dictionary
        return {
            Path("notebooks"): None,  # Create main notebook directory
            Path("notebooks/README.md"): notebook_readme,
            # Append Jupyter gitignore to root .gitignore
            Path(".gitignore"): gitignore_content,
        }

    def init(self, context: dict) -> None:
        """
        Initialize Jupyter notebook support after skeleton creation.

        This will add the necessary dependencies to pyproject.toml.
        """
        console.print("[bold blue]Initializing Jupyter notebook support...[/bold blue]")

        try:
            # Change to project directory
            os.chdir(self.project_path)

            # Add Jupyter dependencies to poetry dev group
            console.print(
                "[bold cyan]Adding Jupyter dependencies to poetry dev group...[/bold cyan]"
            )

            jupyter_deps = [
                "jupyter",
                "notebook",
                "nbconvert",
                "ipykernel",
                "matplotlib",
                "pandas",
            ]

            # Read current pyproject.toml
            pyproject_path = Path("pyproject.toml")
            with open(pyproject_path, "rb") as f:
                pyproject = tomli.load(f)

            # Ensure tool.poetry.group.dev exists
            if "tool" not in pyproject:
                pyproject["tool"] = {}
            if "poetry" not in pyproject["tool"]:
                pyproject["tool"]["poetry"] = {}
            if "group" not in pyproject["tool"]["poetry"]:
                pyproject["tool"]["poetry"]["group"] = {}
            if "dev" not in pyproject["tool"]["poetry"]["group"]:
                pyproject["tool"]["poetry"]["group"]["dev"] = {"dependencies": {}}

            # Add each dependency to the dev group
            for dep in jupyter_deps:
                pyproject["tool"]["poetry"]["group"]["dev"]["dependencies"][dep] = "*"
                console.print(
                    f"[bold green]Added {dep} to dev dependencies[/bold green]"
                )

            # Write back to pyproject.toml
            with open(pyproject_path, "wb") as f:
                tomli_w.dump(pyproject, f)

            console.print(
                "[bold green]Jupyter dependencies added to poetry.dev group![/bold green]"
            )

        except FileNotFoundError:
            console.print(
                "[bold yellow]pyproject.toml not found. Please ensure you are in a Poetry project.[/bold yellow]"
            )

    def install(self, context: dict) -> None:
        """
        Set up the Jupyter kernel for the project.

        This will create a Jupyter kernel specific to this project.
        """
        console.print(
            "[bold blue]Setting up Jupyter kernel for the project...[/bold blue]"
        )

        try:
            # Ensure we're in the right directory
            os.chdir(self.project_path)

            # Create a Jupyter kernel for this project
            console.print(
                "[bold cyan]Creating Jupyter kernel for this project...[/bold cyan]"
            )

            project_name = context.get("project_name", "myproject")

            # Run the ipykernel installation via poetry
            result = subprocess.call(
                [
                    "poetry",
                    "run",
                    "python",
                    "-m",
                    "ipykernel",
                    "install",
                    "--user",
                    "--name",
                    project_name,
                    "--display-name",
                    f"{project_name} (Poetry)",
                ],
                stdin=None,
                stdout=None,
                stderr=None,
            )

            if result == 0:
                console.print(
                    "[bold green]Jupyter kernel created successfully![/bold green]"
                )
                console.print(
                    f"[bold green]You can now use the '{project_name} (Poetry)' kernel in Jupyter.[/bold green]"
                )
            else:
                console.print(
                    f"[bold yellow]Jupyter kernel creation exited with code {result}[/bold yellow]"
                )

        except FileNotFoundError:
            console.print(
                "[bold yellow]Poetry or Jupyter not found. Make sure they are installed.[/bold yellow]"
            )
            console.print("https://python-poetry.org/docs/#installation")
