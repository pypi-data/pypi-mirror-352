import importlib.metadata

__version__ = importlib.metadata.version("kozmodb")

from kozmodb.client.main import AsyncMemoryClient, MemoryClient  # noqa
from kozmodb.memory.main import AsyncMemory, Memory  # noqa
