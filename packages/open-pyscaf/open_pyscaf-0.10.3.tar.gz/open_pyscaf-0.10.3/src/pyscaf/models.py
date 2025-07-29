"""
Data models for pyscaf CLI.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class ProjectType(str, Enum):
    """Type of project to generate."""

    PACKAGE = "package"
    NOTEBOOK = "notebook"
    BOOK = "book"
    WEBAPP = "webapp"


class CIOption(str, Enum):
    """CI/CD options to configure."""

    EXECUTE = "execute"
    BUILD = "build"
    PUBLISH = "publish"


class OutputFormat(str, Enum):
    """Output formats to generate."""

    HTML = "html"
    PDF = "pdf"
    IPYNB = "ipynb"


class ProjectConfig(BaseModel):
    """Configuration for a new project."""

    project_name: str
    project_type: List[ProjectType]
    author: str = ""
    formats: Optional[List[OutputFormat]] = None
    use_git: bool = False
    remote_url: Optional[str] = None
    ci_options: Optional[List[CIOption]] = None
    docker: bool = False
    interactive: bool = False
    no_install: bool = False
