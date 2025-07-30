from .sws_api_client import SwsApiClient
from .discover import Discover
from .datasets import Datasets
from .datatable import Datatables
from .tasks import (
    TaskManager,
    PluginPayload,
    TaskDataset,
    TaskInfo,
    TaskResponse
)
from .tags import Tags
from .plugins import Plugins
from .codelist import Codelists
from .flaglist import Flaglists
from .sessions import Sessions

__version__ = "1.0.12-beta.1"