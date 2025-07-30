"""
Tag Factory CLI tool main entry point.
"""
import click

from tag_factory_cli import __version__
from tag_factory_cli.utils.config import Config
from tag_factory_cli.datasets import DatasetManager
from tag_factory_cli.hashtags import HashTagManager
from tag_factory_cli.tags import TagManager
from tag_factory_cli.workspaces import WorkspaceManager


@click.group()
@click.version_option(version=__version__)
def cli():
    """Tag Factory CLI tool."""
    pass


@cli.command()
def hello():
    """Simple command to test the CLI."""
    click.echo("Hello from Tag Factory CLI!")


@cli.command()
@click.argument("workspace_id")
def use(workspace_id):
    """Set the current workspace."""
    try:
        workspace_manager = WorkspaceManager()
        workspace = workspace_manager.use_workspace(workspace_id)
        click.echo(f"Now using workspace: {workspace['name']} (ID: {workspace['id']})")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.group()
def datasets():
    """Commands for managing datasets."""
    pass


@datasets.command("list")
@click.option("--workspace", help="Workspace ID (optional if workspace is set with 'use' command)")
def list_datasets(workspace):
    """List all datasets in a workspace."""
    try:
        dataset_manager = DatasetManager()
        datasets = dataset_manager.list_datasets(workspace)
        
        if not datasets:
            click.echo("No datasets found.")
            return
            
        current_workspace = workspace or Config().get_current_workspace()
        click.echo(f"Datasets in workspace {current_workspace}:")
        for dataset in datasets:
            image_count = dataset.get("_count", {}).get("images", 0)
            click.echo(f"- {dataset['name']} (ID: {dataset['id']}): {dataset.get('description', 'No description')} ({image_count} images)")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@datasets.command("export")
@click.argument("dataset_id")
@click.option("--dest_dir", default=".", help="Destination directory for exported files (default: current working directory)")
@click.option("--tag_extension", default="txt", help="File extension for tag files (default: txt)")
def export_dataset(dataset_id, dest_dir, tag_extension):
    """Export a dataset with images and tags.
    
    This command exports a dataset's images and their associated tags.
    For each image, it creates two files: the image file named "{filename}.{extension}"
    and a tag file named "{filename}.{tag_extension}" containing the associated tags.
    """
    try:
        dataset_manager = DatasetManager()
        result = dataset_manager.export_dataset(dataset_id, dest_dir, tag_extension)
        click.echo(f"Successfully exported dataset (ID: {dataset_id}) to {result['destination']}")
        click.echo(f"Exported {result['image_count']} images with their tags")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.group()
def tags():
    """Commands for managing tags."""
    pass


@tags.command("list")
@click.option("--workspace", help="Workspace ID (optional if workspace is set with 'use' command)")
def list_tags(workspace):
    """List all tags in a workspace."""
    try:
        tag_manager = TagManager()
        tags = tag_manager.list_tags(workspace)
        
        if not tags:
            click.echo("No tags found.")
            return
            
        current_workspace = workspace or Config().get_current_workspace()
        click.echo(f"Tags in workspace {current_workspace}:")
        for tag in tags:
            image_count = tag.get("image_count", 0)
            click.echo(f"- {tag['name']}: {tag.get('description', 'No description')} ({image_count} images)")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.group()
def hashtags():
    """Commands for managing hashtags."""
    pass


@hashtags.command("list")
@click.option("--workspace", help="Workspace ID (optional if workspace is set with 'use' command)")
def list_hashtags(workspace):
    """List all hashtags in a workspace."""
    try:
        hashtag_manager = HashTagManager()
        hashtags = hashtag_manager.list_hashtags(workspace)
        
        if not hashtags:
            click.echo("No hashtags found.")
            return
            
        current_workspace = workspace or Config().get_current_workspace()
        click.echo(f"HashTags in workspace {current_workspace}:")
        for hashtag in hashtags:
            image_count = hashtag.get("image_count", 0)
            click.echo(f"- #{hashtag['name']} ({image_count} images)")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.group()
def workspaces():
    """Commands for managing workspaces."""
    pass


@workspaces.command("list")
def list_workspaces():
    """List all workspaces."""
    try:
        workspace_manager = WorkspaceManager()
        workspaces = workspace_manager.list_workspaces()
        
        config = Config()
        current_workspace = config.get_current_workspace()
        
        click.echo(f"Total workspaces: {len(workspaces)}")
        click.echo("Available workspaces:")
        for workspace in workspaces:
            is_current = " (current)" if workspace["id"] == current_workspace else ""
            click.echo(f"- {workspace['name']} (ID: {workspace['id']}){is_current}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@workspaces.command()
@click.argument("id")
def get(id):
    """Get workspace details."""
    try:
        workspace_manager = WorkspaceManager()
        workspace = workspace_manager.get_workspace(id)
        click.echo(f"Workspace: {workspace['name']}")
        click.echo(f"ID: {workspace['id']}")
        click.echo(f"Description: {workspace.get('description', 'No description')}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    cli()
