"""
HashTag-related functionality for Tag Factory CLI.
"""
from tag_factory_cli.utils.api import APIClient
from tag_factory_cli.utils.config import Config


class HashTagManager:
    """Manager for hashtag operations."""

    def __init__(self, api_client=None):
        """Initialize hashtag manager.
        
        Args:
            api_client: API client instance. If None, creates new client.
        """
        self.api_client = api_client or APIClient()
        self.config = Config()

    def list_hashtags(self, workspace_id=None):
        """List hashtags in workspace.
        
        Args:
            workspace_id: Workspace ID. If None, uses current workspace.
            
        Returns:
            List of hashtags
        """
        workspace_id = workspace_id or self.config.get_current_workspace()
        if not workspace_id:
            raise ValueError("Workspace ID is required. Use 'tag-factory use <workspace_id>' to set a default workspace.")
            
        path = "/hashtags"
        params = {"workspaceId": workspace_id}
        return self.api_client.get(path, params)

    def get_hashtag(self, hashtag_id):
        """Get hashtag details.
        
        Args:
            hashtag_id: HashTag ID
            
        Returns:
            HashTag details
        """
        path = f"/hashtags/{hashtag_id}"
        return self.api_client.get(path)

    def create_hashtag(self, workspace_id, name):
        """Create new hashtag.
        
        Args:
            workspace_id: Workspace ID
            name: HashTag name
            
        Returns:
            Created hashtag
        """
        workspace_id = workspace_id or self.config.get_current_workspace()
        if not workspace_id:
            raise ValueError("Workspace ID is required. Use 'tag-factory use <workspace_id>' to set a default workspace.")
            
        path = "/hashtags"
        data = {
            "workspaceId": workspace_id,
            "name": name,
        }
        return self.api_client.post(path, data)
