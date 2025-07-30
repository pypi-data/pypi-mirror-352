import importlib.metadata

__version__ = importlib.metadata.version(__package__ or __name__)

from kozmochain.app import App  # noqa: F401
from kozmochain.client import Client  # noqa: F401
from kozmochain.pipeline import Pipeline  # noqa: F401

# Setup the user directory if doesn't exist already
Client.setup()
