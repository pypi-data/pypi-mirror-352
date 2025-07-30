from fabric.dataagent.client._fabric_openai import FabricOpenAI
from fabric.dataagent.client._fabric_data_agent_api import FabricDataAgentAPI
from fabric.dataagent.client._create_delete import create_data_agent, delete_data_agent
from fabric.dataagent.client._fabric_data_agent_mgmt import FabricDataAgentManagement
from fabric.dataagent.client._datasource import Datasource
from fabric.dataagent.client._tagged_value import TaggedValue

__all__ = [
    "Datasource",
    "FabricOpenAI",
    "FabricDataAgentAPI",
    "FabricDataAgentManagement",
    "TaggedValue",
    "create_data_agent",
    "delete_data_agent",
]

_warning_printed = False

if not _warning_printed:
    _warning_printed = True
    try:
        import os

        if os.environ.get("MSNOTEBOOKUTILS_RUNTIME_TYPE", "").lower() != "jupyter":
            print("Warning: This package is only supported in Fabric Python notebook.")
    except:  # noqa: E722
        pass
