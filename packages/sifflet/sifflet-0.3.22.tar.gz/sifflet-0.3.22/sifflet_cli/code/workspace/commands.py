import sys
import uuid
from pathlib import Path
from typing import List

import click
import yaml
from click import Context
from click.types import UUID
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup
from rich.console import Console
from rich.syntax import Syntax
from sifflet_sdk.client.models.as_code_workspace_dto import AsCodeWorkspaceDto
from sifflet_sdk.client.models.workspace_apply_object_response_dto import (
    WorkspaceApplyObjectResponseDto,
)
from sifflet_sdk.client.models.workspace_apply_response_dto import (
    WorkspaceApplyResponseDto,
)
from sifflet_sdk.code.workspace.service import WorkspaceService
from sifflet_sdk.constants import SIFFLET_CONFIG_CTX


@click.group()
def workspace():
    """Manage and apply workspaces."""


@workspace.command()
@click.option(
    "--file",
    "-f",
    "file_name",
    required=True,
    type=click.Path(exists=False),
    help="Path of the Workspace YAML file",
)
@click.option("--name", "-n", "name", required=True, type=str, help="Name of the workspace")
@click.pass_context
def init(ctx: Context, file_name: str, name: str):
    """
    Creates a new Workspace YAML file locally.
    """
    if Path(file_name).exists():
        raise click.BadParameter("File already exists", ctx, param_hint="--file")

    sifflet_config = ctx.obj[SIFFLET_CONFIG_CTX]
    workspace_service = WorkspaceService(sifflet_config)
    workspace_service.initialize_workspace(Path(file_name), name)


@workspace.command()
@click.pass_context
def list(ctx: Context):
    """
    List all workspaces.
    """
    sifflet_config = ctx.obj[SIFFLET_CONFIG_CTX]
    workspace_service = WorkspaceService(sifflet_config)
    workspace_apply_response: List[AsCodeWorkspaceDto] = workspace_service.list_workspaces()
    # Print list of workspaces
    console = Console()
    for workspace in workspace_apply_response:
        if workspace.description:
            console.print(f" - [bold]{workspace.id}[/bold] - {workspace.name} ({workspace.description})")
        else:
            console.print(f" - [bold]{workspace.id}[/bold] - {workspace.name}")


@workspace.command()
@optgroup.group("Workspace to delete", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("--id", "id", type=UUID, help="ID of the workspace")
@optgroup.option(
    "--file",
    "-f",
    "file_name",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path of the Workspace YAML file",
)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    help="Only return the plan for the changes without executing them",
)
@click.pass_context
@click.option(
    "--verbose",
    "verbose",
    is_flag=True,
    help="Print all changes",
)
def delete(ctx: Context, id: uuid.UUID, file_name: str, dry_run: bool, verbose: bool):
    """
    Deletes a workspace.
    """
    sifflet_config = ctx.obj[SIFFLET_CONFIG_CTX]
    workspace_service = WorkspaceService(sifflet_config)
    workspace_apply_response: WorkspaceApplyResponseDto
    if id:
        workspace_apply_response = workspace_service.delete_workspace_by_id(id, dry_run)
    else:
        workspace_apply_response = workspace_service.delete_workspace_by_file_name(Path(file_name), dry_run)
    print_response(workspace_apply_response, verbose)


@workspace.command()
@click.option(
    "--file",
    "-f",
    "file_name",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path of the Workspace YAML file",
)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    help="Only return the plan for the changes without executing them",
)
@click.option(
    "--force-delete",
    "force_delete",
    is_flag=True,
    help="Allow deleting the objects in the workspace if they are removed from the workspace files",
)
@click.option(
    "--fail-on-error",
    "fail_on_error",
    is_flag=True,
    help="Fail the entire update if any error is detected",
)
@click.option(
    "--verbose",
    "verbose",
    is_flag=True,
    help="Print all changes",
)
@click.pass_context
def apply(
    ctx: Context,
    file_name: str,
    dry_run: bool,
    force_delete: bool,
    fail_on_error: bool,
    verbose: bool,
):
    """
    Apply the specified workspace.
    """
    sifflet_config = ctx.obj[SIFFLET_CONFIG_CTX]
    workspace_service = WorkspaceService(sifflet_config)
    workspace_apply_response, fatal_error_occurred = workspace_service.apply_workspace(
        Path(file_name), dry_run, force_delete, fail_on_error
    )
    print_response(workspace_apply_response, verbose)

    if fatal_error_occurred:
        sys.exit(1)  # Exit because we want the CI for clients to fail in this case


def print_response(response: WorkspaceApplyResponseDto, verbose: bool) -> None:
    console = Console()
    changes = response.changes
    filtered_changes = filter_changes(changes, {"Error", "Fatal"})

    create_success_count = count_changes(changes, "Create", "Success", "Monitor")
    update_success_count = count_changes(changes, "Update", "Success", "Monitor")
    delete_success_count = count_changes(changes, "Delete", "Success", "Monitor")
    no_change_count = count_changes(changes, "None", "Success", "Monitor")
    error_count = len(filtered_changes)

    if verbose:
        syntax = Syntax(yaml.dump(response.to_dict(), sort_keys=False), "yaml")
    else:
        response_dict = {
            **response.to_dict(),
            "changes": [change.to_dict() for change in filtered_changes],
        }
        syntax = Syntax(yaml.dump(response_dict, sort_keys=False), "yaml")

    console.print(syntax)

    console.print(f"\nChange summary:")
    console.print(f"- {create_success_count} monitors created")
    console.print(f"- {update_success_count} monitors updated")
    console.print(f"- {delete_success_count} monitors deleted")
    console.print(f"- {no_change_count} monitors without change")
    console.print(f"- {error_count} errors occurred")


def count_changes(
    changes: List[WorkspaceApplyObjectResponseDto],
    change_type: str,
    sub_status: str,
    kind: str,
) -> int:
    return sum(
        1
        for change in changes
        if change.change
        and change.change.type == change_type
        and change.sub_status == sub_status
        and change.kind == kind
    )


def filter_changes(
    changes: List[WorkspaceApplyObjectResponseDto], statuses: set
) -> List[WorkspaceApplyObjectResponseDto]:
    return [change for change in changes if change.status in statuses]
