"""
Tag-related functionality for Tag Factory CLI.
"""
from tag_factory_cli.utils.api import APIClient
from tag_factory_cli.utils.config import Config


class TagManager:
    """Manager for tag operations."""

    def __init__(self, api_client=None):
        """Initialize tag manager.
        
        Args:
            api_client: API client instance. If None, creates new client.
        """
        self.api_client = api_client or APIClient()
        self.config = Config()

    def list_tags(self, workspace_id=None):
        """List tags in workspace.
        
        Args:
            workspace_id: Workspace ID. If None, uses current workspace.
            
        Returns:
            List of tags
        """
        workspace_id = workspace_id or self.config.get_current_workspace()
        if not workspace_id:
            raise ValueError("Workspace ID is required. Use 'tag-factory use <workspace_id>' to set a default workspace.")
            
        path = "/tags"
        params = {"workspaceId": workspace_id}
        return self.api_client.get(path, params)

    def get_tag(self, tag_id):
        """Get tag details.
        
        Args:
            tag_id: Tag ID
            
        Returns:
            Tag details
        """
        path = f"/tags/{tag_id}"
        return self.api_client.get(path)

    def create_tag(self, workspace_id=None, name=None, description=None):
        """Create new tag.
        
        Args:
            workspace_id: Workspace ID. If None, uses current workspace.
            name: Tag name
            description: Tag description
            
        Returns:
            Created tag
        """
        workspace_id = workspace_id or self.config.get_current_workspace()
        if not workspace_id:
            raise ValueError("Workspace ID is required. Use 'tag-factory use <workspace_id>' to set a default workspace.")
            
        if not name:
            raise ValueError("Tag name is required")
            
        path = "/tags"
        data = {
            "workspaceId": workspace_id,
            "name": name,
            "description": description,
        }
        return self.api_client.post(path, data)
