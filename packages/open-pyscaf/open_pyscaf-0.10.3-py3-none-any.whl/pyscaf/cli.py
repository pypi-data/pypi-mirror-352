"""
Command-line interface for pyscaf.
"""

import sys

import click
from rich.console import Console

from pyscaf import __version__
from pyscaf.actions import discover_actions
from pyscaf.actions.manager import ActionManager
from pyscaf.preference_chain.topologic_tree import best_execution_order

console = Console()


def print_version(ctx, param, value):
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return
    console.print(f"pyscaf version {__version__}")
    ctx.exit()


def collect_cli_options():
    action_classes = discover_actions()
    deps = []
    action_class_by_id = {}
    for action_cls in action_classes:
        action_id = action_cls.__name__.replace("Action", "").lower()
        deps.append(
            {
                "id": action_id,
                "depends": getattr(action_cls, "depends", []),
                "after": getattr(action_cls, "run_preferably_after", None),
            }
        )
        action_class_by_id[action_id] = action_cls
    order = best_execution_order(
        [
            {"id": d["id"], "fullfilled": [d["id"]], "external": d["depends"] or []}
            for d in deps
        ]
    )
    cli_options = []
    for action_id in order:
        action_cls = action_class_by_id[action_id]
        cli_options.extend(getattr(action_cls, "cli_options", []))
    return cli_options


def add_dynamic_options(command):
    cli_options = collect_cli_options()
    for opt in reversed(cli_options):
        param_decls = [opt.name]
        click_opts = {}
        # Type
        if opt.type == "int":
            click_opts["type"] = int
        elif opt.type == "choice" and opt.choices:
            click_opts["type"] = click.Choice(opt.choices, case_sensitive=False)
            if opt.multiple:
                click_opts["multiple"] = True
        elif opt.type == "str":
            click_opts["type"] = str
        elif opt.type == "bool":
            click_opts["type"] = click.BOOL
            click_opts["is_flag"] = True
            click_opts["default"] = None
        # Help
        if opt.help:
            click_opts["help"] = opt.help
        # Default
        # Required
        if opt.required:
            click_opts["required"] = True
        command = click.option(*param_decls, **click_opts)(command)
    return command


@click.group()
@click.version_option(
    __version__,
    "--version",
    "-V",
    callback=print_version,
    help="Show the version and exit.",
)
def cli():
    """🧪 pyscaf - Project generator for laboratory, teaching and data analysis."""
    pass


@cli.command()
@add_dynamic_options
@click.argument("project_name")
@click.option(
    "--interactive",
    is_flag=True,
    help="Enable interactive mode (asks questions to the user).",
)
@click.option("--no-install", is_flag=True, help="Skip installation step.")
def init(project_name, interactive, no_install, **kwargs):
    """
    Initialize a new customized project structure.
    """
    context = dict(kwargs)
    context["project_name"] = project_name
    context["interactive"] = interactive
    context["no_install"] = no_install
    manager = ActionManager(project_name, context)
    if interactive:
        context = manager.ask_interactive_questions(context)
    manager.create_project()


def main():
    """Entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
