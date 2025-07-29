"""
Action classes for project scaffolding.
"""

import importlib
import os
import pkgutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel


class CLIOption(BaseModel):
    name: str  # e.g. '--author'
    type: str = "str"  # 'str', 'bool', 'int', 'choice', etc.
    help: Optional[str] = None
    default: Any = None
    prompt: Optional[str] = None
    choices: Optional[List[Any]] = None  # For choice type
    is_flag: Optional[bool] = None  # For bool
    multiple: Optional[bool] = None  # For multi-choice
    required: Optional[bool] = None


class Action(ABC):
    """
    Abstract base class for all project actions.
    Now supports explicit dependencies, preferences, and CLI options.

    Actions can:
    1. Generate file/directory skeleton via the skeleton() method
    2. Initialize content/behavior via the init() method
    3. Install dependencies via the install() method
    """

    # Explicit dependencies and preferences
    depends: List[str] = []
    run_preferably_after: Optional[str] = None
    cli_options: List[CLIOption] = []

    def __init_subclass__(cls):
        # Validation: if multiple depends and no run_preferably_after, raise error
        if (
            hasattr(cls, "depends")
            and len(cls.depends) > 1
            and not getattr(cls, "run_preferably_after", None)
        ):
            raise ValueError(
                f"Action '{cls.__name__}' has multiple depends but no run_preferably_after"
            )

    def __init__(self, project_path: Union[str, Path]):
        self.project_path = Path(project_path)

    @abstractmethod
    def skeleton(self, context: dict) -> Dict[Path, Optional[str]]:
        """
        Define the filesystem skeleton for this action, using the provided context.

        Returns a dictionary mapping paths to create to their content:
        - If the value is None, a directory is created
        - If the value is a string, a file is created with that content

        Returns:
            Dictionary mapping paths to content
        """
        pass

    def init(self, context: dict) -> None:
        """
        Initialize the action after skeleton creation, using the provided context.

        This method is called after all skeletons have been created.
        Use it to run tools, modify files, etc.
        """
        pass

    def install(self, context: dict) -> None:
        """
        Install dependencies or run post-initialization commands, using the provided context.

        This method is called after all actions have been initialized.
        Use it to install dependencies, run commands like 'poetry install', etc.
        """
        pass

    def create_skeleton(self, context: dict) -> Set[Path]:
        """
        Create the filesystem skeleton for this action using the provided context.

        Returns:
            Set of paths created
        """
        created_paths = set()
        skeleton = self.skeleton(context)

        for path, content in skeleton.items():
            full_path = self.project_path / path

            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if content is None:
                # Create directory
                full_path.mkdir(exist_ok=True)
            else:
                # Create file with content or append if exists
                if full_path.exists():
                    # Append content to existing file
                    with open(full_path, "a") as f:
                        f.write("\n" + content)
                else:
                    # Create new file with content
                    full_path.write_text(content)

            created_paths.add(full_path)

        return created_paths

    def activate(self, context: dict) -> bool:
        """
        Return True if this action's question/step should be executed given the current context.
        Override in subclasses for conditional logic.
        """
        return True


def discover_actions():
    """
    Dynamically discover all Action subclasses in the actions package (excluding base/manager/pycache).
    Returns a list of Action classes.
    """
    actions = []
    actions_dir = os.path.dirname(__file__)
    for _, module_name, is_pkg in pkgutil.iter_modules([actions_dir]):
        if module_name in ("base", "manager", "__pycache__"):
            continue
        mod = importlib.import_module(f"pyscaf.actions.{module_name}")
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type) and issubclass(obj, Action) and obj is not Action:
                actions.append(obj)
    return actions
