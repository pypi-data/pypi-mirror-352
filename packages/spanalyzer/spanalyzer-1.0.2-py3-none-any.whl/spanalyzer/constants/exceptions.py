# Constants that will be used to cover some exceptions in the project

from enum import Enum


class ExcludedPaths(str, Enum):
    """
    Default paths to exclude from code analysis.

    Args:
        VENV [str]: the path to the virtual environment
        TESTS [str]: the path to the tests
        NODE_MODULES [str]: the path to the node modules
        PYCACHE [str]: the path to the pycache
        GIT [str]: the path to the git
        INIT [str]: the path to the init
    """

    VENV = "venv"
    TESTS = "tests"
    NODE_MODULES = "node_modules"
    PYCACHE = "__pycache__"
    GIT = ".git"
    INIT = "__init__.py"

    @classmethod
    def values(cls) -> set[str]:
        """Get all keyword values as a set."""
        return {member.value for member in cls}
