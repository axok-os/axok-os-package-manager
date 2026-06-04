"""Package exports for aopmAPI."""

# Use an explicit relative import so importing the package works when the
# package is loaded as `aopmAPI` (otherwise Python tries to import a top-level
# module named `main` and raises ModuleNotFoundError).
from .main import *

# Optionally, define __all__ in the future to control public API.
