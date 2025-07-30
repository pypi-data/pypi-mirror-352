import subprocess

import click
import requests

from docker.client import DockerClient
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import coro
from tinybird.tb.modules.exceptions import CLIException
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.local_common import (
    TB_CONTAINER_NAME,
    TB_LOCAL_ADDRESS,
    get_docker_client,
    get_existing_container_with_matching_env,
    start_tinybird_local,
)


def stop_tinybird_local(docker_client: DockerClient) -> None:
    """Stop the Tinybird container."""
    try:
        container = docker_client.containers.get(TB_CONTAINER_NAME)
        container.stop()
    except Exception:
        pass


def remove_tinybird_local(docker_client: DockerClient) -> None:
    """Remove the Tinybird container."""
    try:
        container = docker_client.containers.get(TB_CONTAINER_NAME)
        if click.confirm(
            FeedbackManager.warning(
                message="△ This step will remove all your data inside Tinybird Local. Are you sure? [y/N]:"
            ),
            show_default=False,
            prompt_suffix="",
        ):
            container.remove(force=True)
    except Exception:
        pass


def update_cli() -> None:
    click.echo(FeedbackManager.highlight(message="» Updating Tinybird CLI..."))

    try:
        process = subprocess.Popen(
            ["uv", "tool", "upgrade", "tinybird"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        raise CLIException(
            FeedbackManager.error(
                message="Cannot find required tool: uv. Reinstall using: curl https://tinybird.co | sh"
            )
        )

    stdout, stderr = process.communicate()
    if "Nothing to upgrade" not in stdout + stderr:
        for line in stdout.split("\n") + stderr.split("\n"):
            if "Updated tinybird" in line:
                click.echo(FeedbackManager.info(message=f"» {line}"))
        click.echo(FeedbackManager.success(message="✓ Tinybird CLI updated"))
    else:
        click.echo(FeedbackManager.info(message="✓ Tinybird CLI is already up-to-date"))


@cli.command()
def update() -> None:
    """Update Tinybird CLI to the latest version."""
    update_cli()


@cli.command(name="upgrade", hidden=True)
def upgrade() -> None:
    """Update Tinybird CLI to the latest version."""
    update_cli()


@cli.group()
@click.pass_context
def local(ctx: click.Context) -> None:
    """Manage the local Tinybird instance."""


@local.command()
@coro
async def stop() -> None:
    """Stop Tinybird Local"""
    click.echo(FeedbackManager.highlight(message="» Shutting down Tinybird Local..."))
    docker_client = get_docker_client()
    stop_tinybird_local(docker_client)
    click.echo(FeedbackManager.success(message="✓ Tinybird Local stopped."))


@local.command()
@coro
async def status() -> None:
    """Check status of Tinybird Local"""
    docker_client = get_docker_client()
    container = get_existing_container_with_matching_env(docker_client, TB_CONTAINER_NAME, {})

    if container:
        status = container.status
        health = container.attrs.get("State", {}).get("Health", {}).get("Status")

        if status == "running" and health == "healthy":
            click.echo(FeedbackManager.success(message="✓ Tinybird Local is ready!"))
        elif status == "restarting" or (status == "running" and health == "starting"):
            click.echo(FeedbackManager.highlight(message="* Tinybird Local is starting..."))
        elif status == "removing":
            click.echo(FeedbackManager.highlight(message="* Tinybird Local is stopping..."))
        else:
            click.echo(
                FeedbackManager.info(message="✗ Tinybird Local is not running. Run 'tb local start' to start it")
            )
    else:
        click.echo(FeedbackManager.info(message="✗ Tinybird Local is not running. Run 'tb local start' to start it"))


@local.command()
@coro
async def remove() -> None:
    """Remove Tinybird Local"""
    click.echo(FeedbackManager.highlight(message="» Removing Tinybird Local..."))
    docker_client = get_docker_client()
    remove_tinybird_local(docker_client)
    click.echo(FeedbackManager.success(message="✓ Tinybird Local removed"))


@local.command()
@coro
@click.option(
    "--use-aws-creds",
    default=False,
    is_flag=True,
    help="Use local AWS credentials from your environment and pass them to the Tinybird docker container",
)
async def start(use_aws_creds: bool) -> None:
    """Start Tinybird Local"""
    click.echo(FeedbackManager.highlight(message="» Starting Tinybird Local..."))
    docker_client = get_docker_client()
    start_tinybird_local(docker_client, use_aws_creds)
    click.echo(FeedbackManager.success(message="✓ Tinybird Local is ready!"))


@local.command()
@coro
@click.option(
    "--use-aws-creds",
    default=False,
    is_flag=True,
    help="Use local AWS credentials from your environment and pass them to the Tinybird docker container",
)
async def restart(use_aws_creds: bool) -> None:
    """Restart Tinybird Local"""
    click.echo(FeedbackManager.highlight(message="» Restarting Tinybird Local..."))
    docker_client = get_docker_client()
    remove_tinybird_local(docker_client)
    click.echo(FeedbackManager.info(message="✓ Tinybird Local stopped"))
    start_tinybird_local(docker_client, use_aws_creds)
    click.echo(FeedbackManager.success(message="✓ Tinybird Local is ready!"))


@local.command()
def version() -> None:
    """Show Tinybird Local version"""
    response = requests.get(f"{TB_LOCAL_ADDRESS}/version")
    click.echo(FeedbackManager.success(message=f"✓ Tinybird Local version: {response.text}"))
