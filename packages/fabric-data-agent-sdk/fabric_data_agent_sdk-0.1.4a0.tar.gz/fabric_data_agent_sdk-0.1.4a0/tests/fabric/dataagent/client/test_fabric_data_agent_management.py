import unittest
from unittest.mock import patch

from fabric.dataagent.client._datasource import Datasource
from fabric.dataagent.client._fabric_data_agent_mgmt import FabricDataAgentManagement
from fabric.dataagent.client._tagged_value import TaggedValue


class TestFabricDataAgentManagement(unittest.TestCase):

    @patch('fabric.dataagent.client._fabric_data_agent_mgmt.FabricDataAgentAPI')
    @patch('fabric.dataagent.client._fabric_data_agent_mgmt.get_artifact_by_id_or_name')
    @patch('fabric.dataagent.client._fabric_data_agent_mgmt.list_items')
    @patch('fabric.dataagent.client._fabric_data_agent_mgmt.get_notebook_workspace_id')
    @patch('fabric.dataagent.client._fabric_data_agent_mgmt.resolve_workspace_id')
    def setUp(
        self,
        MockResolveWorkspaceID,
        MockGetNotebookWorkspaceID,
        MockListItems,
        MockGetArtifactByIDOrName,
        MockFabricDataAgentAPI,
    ):
        self.mock_client = MockFabricDataAgentAPI.return_value
        self.mock_get_artifact_by_id_or_name = MockGetArtifactByIDOrName
        self.mock_list_items = MockListItems
        self.mock_get_notebook_workspace_id = MockGetNotebookWorkspaceID
        self.mock_resolve_workspace_id = MockResolveWorkspaceID
        self.data_agent_management = FabricDataAgentManagement(
            data_agent="test_data_agent", workspace="test_workspace"
        )

    def test_update_configuration(self):
        self.mock_client.get_configuration.return_value = TaggedValue(
            {"additionalInstructions": "", "userDescription": ""}, "etag"
        )
        self.data_agent_management.update_configuration(
            instructions="New instructions", user_description="New description"
        )
        self.mock_client.set_configuration.assert_called_once()
        updated_config = self.mock_client.set_configuration.call_args[0][0]
        self.assertEqual(
            updated_config.value["additionalInstructions"], "New instructions"
        )
        self.assertEqual(updated_config.value["userDescription"], "New description")

    def test_get_configuration(self):
        self.mock_client.get_configuration.return_value = TaggedValue(
            {
                "additionalInstructions": "instructions",
                "userDescription": "description",
            },
            "etag",
        )
        config = self.data_agent_management.get_configuration()
        self.assertEqual(config.instructions, "instructions")
        self.assertEqual(config.user_description, "description")

    def test_publish(self):
        self.mock_client.get_configuration.return_value = TaggedValue({}, "etag")
        self.data_agent_management.publish()
        self.mock_client.publish.assert_called_once()

    def test_get_datasources(self):
        self.mock_client.get_datasources.return_value = iter(
            [TaggedValue({"id": "ds1"}, "etag"), TaggedValue({"id": "ds2"}, "etag")]
        )
        datasources = self.data_agent_management.get_datasources()
        self.assertEqual(len(datasources), 2)
        self.assertIsInstance(datasources[0], Datasource)
        self.assertEqual(datasources[0]._id, "ds1")

    def test_remove_datasource(self):
        self.mock_client.get_configuration.return_value = TaggedValue({}, "etag")
        self.mock_client.get_datasources.return_value = iter(
            [TaggedValue({"id": "ds1", "display_name": "datasource1"}, "etag")]
        )
        self.data_agent_management.remove_datasource("datasource1")
        self.mock_client.remove_datasource.assert_called_once_with("ds1", "etag")
