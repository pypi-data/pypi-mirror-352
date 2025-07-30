"""
Dataset-related functionality for Tag Factory CLI.
"""
from tag_factory_cli.utils.api import APIClient
from tag_factory_cli.utils.config import Config


class DatasetManager:
    """Manager for dataset operations."""

    def __init__(self, api_client=None):
        """Initialize dataset manager.
        
        Args:
            api_client: API client instance. If None, creates new client.
        """
        self.api_client = api_client or APIClient()
        self.config = Config()

    def list_datasets(self, workspace_id=None):
        """List datasets in workspace.
        
        Args:
            workspace_id: Workspace ID. If None, uses current workspace.
            
        Returns:
            List of datasets
        """
        workspace_id = workspace_id or self.config.get_current_workspace()
        if not workspace_id:
            raise ValueError("Workspace ID is required. Use 'tag-factory use <workspace_id>' to set a default workspace.")
            
        path = "/datasets"
        params = {"workspaceId": workspace_id}
        return self.api_client.get(path, params)

    def get_dataset(self, dataset_id, workspace_id=None):
        """Get dataset details.
        
        Args:
            dataset_id: Dataset ID
            workspace_id: Workspace ID. If None, uses current workspace.
            
        Returns:
            Dataset details
        """
        workspace_id = workspace_id or self.config.get_current_workspace()
        if not workspace_id:
            raise ValueError("Workspace ID is required. Use 'tag-factory use <workspace_id>' to set a default workspace.")
            
        path = f"/datasets/{dataset_id}"
        params = {"workspaceId": workspace_id}
        return self.api_client.get(path, params)

    def create_dataset(self, workspace_id, name, description=None):
        """Create new dataset.
        
        Args:
            workspace_id: Workspace ID
            name: Dataset name
            description: Dataset description
            
        Returns:
            Created dataset
        """
        workspace_id = workspace_id or self.config.get_current_workspace()
        if not workspace_id:
            raise ValueError("Workspace ID is required. Use 'tag-factory use <workspace_id>' to set a default workspace.")
            
        path = "/datasets"
        data = {
            "workspaceId": workspace_id,
            "name": name,
            "description": description,
        }
        return self.api_client.post(path, data)
        
    def export_dataset(self, dataset_id, dest_dir=".", tag_extension="txt"):
        """Export dataset images and tags.
        
        Args:
            dataset_id: Dataset ID
            dest_dir: Destination directory (default: current working directory)
            tag_extension: File extension for tag files (default: txt)
            
        Returns:
            Export result with destination path and image count
        """
        import os
        import requests
        from pathlib import Path
        from urllib.parse import urlparse
        from tqdm import tqdm
        
        dataset = self.get_dataset(dataset_id)
        
        if not dataset.get("images"):
            raise ValueError(f"Dataset has no images")
            
        dest_path = Path(dest_dir).resolve()
        os.makedirs(dest_path, exist_ok=True)
        
        image_count = 0
        for image in tqdm(dataset.get("images", []), desc="Downloading images", unit="image"):
            try:
                image_url = image.get("url")
                if not image_url:
                    continue
                    
                original_filename = image.get("fileName", "")
                if not original_filename:
                    parsed_url = urlparse(image_url)
                    original_filename = os.path.basename(parsed_url.path)
                
                filename_parts = os.path.splitext(original_filename)
                filename = filename_parts[0]
                extension = filename_parts[1].lstrip(".")
                
                if not extension:
                    parsed_url = urlparse(image_url)
                    path_parts = os.path.splitext(parsed_url.path)
                    extension = path_parts[1].lstrip(".")
                    
                if not extension:
                    extension = "jpg"  # Default extension if none is found
                
                image_file_path = dest_path / f"{filename}.{extension}"
                
                response = requests.get(image_url, stream=True)
                response.raise_for_status()
                
                with open(image_file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                tag_file_path = dest_path / f"{filename}.{tag_extension}"
                
                tags = [tag.get("name", "") for tag in image.get("tags", [])]
                
                with open(tag_file_path, "w", encoding="utf-8") as f:
                    f.write(", ".join(tags))
                
                image_count += 1
                
            except Exception as e:
                print(f"Error exporting image {image.get('id')}: {e}")
        
        if image_count == 0:
            raise ValueError("No images were successfully exported")
            
        return {
            "destination": str(dest_path),
            "image_count": image_count
        }
