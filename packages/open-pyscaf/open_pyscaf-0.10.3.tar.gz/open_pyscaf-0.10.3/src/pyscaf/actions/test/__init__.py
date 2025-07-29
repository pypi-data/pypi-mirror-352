"""
Test initialization actions using pytest.
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


class TestAction(Action):
    """Action to initialize a project with pytest testing framework."""

    depends = ["core"]
    run_preferably_after = "core"
    cli_options = [
        CLIOption(
            name="--testing",
            type="bool",
            help="Enable testing with pytest",
            prompt="Do you want to set up testing with pytest?",
            default=False,
        ),
    ]

    def __init__(self, project_path):
        super().__init__(project_path)

    def activate(self, context: dict) -> bool:
        """Activate this action only if testing is enabled."""
        return context.get("testing") is None or context.get("testing", True)

    def skeleton(self, context: dict) -> Dict[Path, Optional[str]]:
        """
        Define the filesystem skeleton for pytest initialization.

        Returns:
            Dictionary mapping paths to content
        """
        # Read pytest documentation
        pytest_doc_path = Path(__file__).parent / "README.md"
        pytest_doc = pytest_doc_path.read_text() if pytest_doc_path.exists() else ""

        # Read test example template
        test_example_path = Path(__file__).parent / "template_test_example.py"
        test_example_template = (
            test_example_path.read_text() if test_example_path.exists() else ""
        )

        # Basic test example
        project_name = context.get("project_name", "myproject")
        curated_project_name = project_name.replace("-", "_")

        # Format the test example with project variables
        test_example = test_example_template.format(
            project_name=project_name, curated_project_name=curated_project_name
        )

        # Return skeleton dictionary
        return {
            Path("tests"): None,  # Create tests directory
            Path("tests/__init__.py"): "",  # Empty init file for tests package
            Path(f"tests/test_{curated_project_name}.py"): test_example,
            Path("tests/README.md"): pytest_doc,
        }

    def init(self, context: dict) -> None:
        """
        Initialize pytest by adding dependencies and configuration to pyproject.toml.

        This will add the necessary testing dependencies and configuration to pyproject.toml.
        """
        console.print("[bold blue]Setting up pytest testing framework...[/bold blue]")

        try:
            # Change to project directory
            os.chdir(self.project_path)

            # Add testing dependencies to poetry dev group
            console.print(
                "[bold cyan]Adding testing dependencies to poetry dev group...[/bold cyan]"
            )

            test_deps = {
                "pytest": "*",
                "pytest-cov": "*",
            }

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
            for dep, version in test_deps.items():
                pyproject["tool"]["poetry"]["group"]["dev"]["dependencies"][dep] = (
                    version
                )
                console.print(
                    f"[bold green]Added {dep} {version} to dev dependencies[/bold green]"
                )

            # Read pytest configuration
            config_path = Path(__file__).parent / "config.toml"
            if config_path.exists():
                with open(config_path, "rb") as f:
                    pytest_config = tomli.load(f)

                # Merge pytest configuration into pyproject
                for section, content in pytest_config.items():
                    if section not in pyproject:
                        pyproject[section] = {}
                    pyproject[section].update(content)

                console.print(
                    "[bold green]Added pytest configuration to pyproject.toml[/bold green]"
                )

            # Write back to pyproject.toml
            with open(pyproject_path, "wb") as f:
                tomli_w.dump(pyproject, f)

            console.print(
                "[bold green]Testing dependencies and configuration added to pyproject.toml![/bold green]"
            )

        except FileNotFoundError:
            console.print(
                "[bold yellow]pyproject.toml not found. Please ensure you are in a Poetry project.[/bold yellow]"
            )

    def install(self, context: dict) -> None:
        """
        Install test dependencies and run initial test.
        """
        console.print("[bold blue]Installing test dependencies...[/bold blue]")

        try:
            # Ensure we're in the right directory
            os.chdir(self.project_path)

            # Run a quick test to validate setup
            console.print("[bold cyan]Running initial test validation...[/bold cyan]")
            result = subprocess.call(
                ["poetry", "run", "pytest", "--version"],
                stdin=None,
                stdout=None,
                stderr=None,
            )

            if result == 0:
                console.print(
                    "[bold green]Pytest setup validated successfully![/bold green]"
                )

                # Run the actual tests
                console.print("[bold cyan]Running initial tests...[/bold cyan]")
                test_result = subprocess.call(
                    ["poetry", "run", "pytest", "tests/", "-v"],
                    stdin=None,
                    stdout=None,
                    stderr=None,
                )

                if test_result == 0:
                    console.print("[bold green]All tests passed![/bold green]")
                else:
                    console.print(
                        f"[bold yellow]Some tests failed (exit code {test_result})[/bold yellow]"
                    )
            else:
                console.print(
                    f"[bold yellow]Pytest validation failed (exit code {result})[/bold yellow]"
                )

        except FileNotFoundError:
            console.print(
                "[bold yellow]Poetry not found. Please install it first:[/bold yellow]"
            )
            console.print("https://python-poetry.org/docs/#installation")
