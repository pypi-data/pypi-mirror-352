"""
Workspace-related functionality for Tag Factory CLI.
"""
from tag_factory_cli.utils.api import APIClient
from tag_factory_cli.utils.config import Config


class WorkspaceManager:
    """Manager for workspace operations."""

    def __init__(self, api_client=None):
        """Initialize workspace manager.
        
        Args:
            api_client: API client instance. If None, creates new client.
        """
        self.api_client = api_client or APIClient()
        self.config = Config()

    def list_workspaces(self):
        """List all workspaces.
        
        Returns:
            List of workspaces
        """
        path = "/workspaces"
        return self.api_client.get(path)

    def get_workspace(self, workspace_id):
        """Get workspace details.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Workspace details
        """
        path = f"/workspaces/{workspace_id}"
        return self.api_client.get(path)

    def create_workspace(self, name, description=None):
        """Create new workspace.
        
        Args:
            name: Workspace name
            description: Workspace description
            
        Returns:
            Created workspace
        """
        path = "/workspaces"
        data = {
            "name": name,
            "description": description,
        }
        return self.api_client.post(path, data)
        
    def use_workspace(self, workspace_id):
        """Set the current workspace.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Selected workspace
        """
        # ワークスペースが存在するか確認
        workspace = self.get_workspace(workspace_id)
        
        # 設定を更新
        self.config.set_current_workspace(workspace_id)
        
        return workspace
        
    def get_current_workspace(self):
        """Get the current workspace.
        
        Returns:
            Current workspace ID or None if not set
        """
        workspace_id = self.config.get_current_workspace()
        if workspace_id:
            return self.get_workspace(workspace_id)
        return None
