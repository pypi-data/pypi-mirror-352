# project_root/graphstat/src/graphstat/__init__.py

# Expose the main function
from .core import \
    graph_hypothesis  # Assuming _permutation_core.py is your core.py file

# Explicitly list what 'from graphstat import *' would import (good practice)
__all__ = ["graph_hypothesis"]
