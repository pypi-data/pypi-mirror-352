import json
import os
import re
import subprocess
import time
from typing import Optional

import boto3
import click
import requests

import docker
from docker.client import DockerClient
from docker.models.containers import Container
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import coro
from tinybird.tb.modules.exceptions import CLIException, CLILocalException
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.local_common import TB_CONTAINER_NAME, TB_IMAGE_NAME, TB_LOCAL_ADDRESS, TB_LOCAL_PORT
from tinybird.tb.modules.telemetry import add_telemetry_event


def start_tinybird_local(
    docker_client: DockerClient,
    use_aws_creds: bool,
) -> None:
    """Start the Tinybird container."""
    pull_show_prompt = False
    pull_required = False
    try:
        local_image = docker_client.images.get(TB_IMAGE_NAME)
        local_image_id = local_image.attrs["RepoDigests"][0].split("@")[1]
        remote_image = docker_client.images.get_registry_data(TB_IMAGE_NAME)
        pull_show_prompt = local_image_id != remote_image.id
    except Exception:
        pull_show_prompt = False
        pull_required = True

    if pull_show_prompt and click.confirm(
        FeedbackManager.warning(message="△ New version detected, download? [y/N]:"),
        show_default=False,
        prompt_suffix="",
    ):
        click.echo(FeedbackManager.info(message="* Downloading latest version of Tinybird Local..."))
        pull_required = True

    if pull_required:
        docker_client.images.pull(TB_IMAGE_NAME, platform="linux/amd64")

    environment = get_use_aws_creds() if use_aws_creds else {}

    container = get_existing_container_with_matching_env(docker_client, TB_CONTAINER_NAME, environment)

    if container and not pull_required:
        # Container `start` is idempotent. It's safe to call it even if the container is already running.
        container.start()
    else:
        if container:
            container.remove(force=True)

        container = docker_client.containers.run(
            TB_IMAGE_NAME,
            name=TB_CONTAINER_NAME,
            detach=True,
            ports={"7181/tcp": TB_LOCAL_PORT},
            remove=False,
            platform="linux/amd64",
            environment=environment,
        )

    click.echo(FeedbackManager.info(message="* Waiting for Tinybird Local to be ready..."))
    while True:
        container.reload()  # Refresh container attributes
        health = container.attrs.get("State", {}).get("Health", {}).get("Status")
        if health == "healthy":
            break
        if health == "unhealthy":
            raise CLILocalException(
                FeedbackManager.error(
                    message="Tinybird Local is unhealthy. Try running `tb local restart` in a few seconds."
                )
            )

        time.sleep(5)

    # Remove tinybird-local dangling images to avoid running out of disk space
    images = docker_client.images.list(name=re.sub(r":.*$", "", TB_IMAGE_NAME), all=True, filters={"dangling": True})
    for image in images:
        image.remove(force=True)


def get_existing_container_with_matching_env(
    docker_client: DockerClient, container_name: str, required_env: dict[str, str]
) -> Optional[Container]:
    """
    Checks if a container with the given name exists and has matching environment variables.
    If it exists but environment doesn't match, it returns None.

    Args:
        docker_client: The Docker client instance
        container_name: The name of the container to check
        required_env: Dictionary of environment variables that must be present

    Returns:
        The container if it exists with matching environment, None otherwise
    """
    container = None
    containers = docker_client.containers.list(all=True, filters={"name": container_name})
    if containers:
        container = containers[0]

    if container and required_env:
        container_info = container.attrs
        container_env = container_info.get("Config", {}).get("Env", [])
        env_missing = False
        for key, value in required_env.items():
            env_var = f"{key}={value}"
            if env_var not in container_env:
                env_missing = True
                break

        if env_missing:
            container.remove(force=True)
            container = None

    return container


def get_docker_client() -> DockerClient:
    """Check if Docker is installed and running."""
    try:
        docker_host = os.getenv("DOCKER_HOST")
        if not docker_host:
            # Try to get docker host from docker context
            try:
                try:
                    output = subprocess.check_output(["docker", "context", "inspect"], text=True)
                except Exception as e:
                    add_telemetry_event(
                        "docker_error",
                        error=f"docker_context_inspect_error: {str(e)}",
                    )
                    raise e
                try:
                    context = json.loads(output)
                except Exception as e:
                    add_telemetry_event(
                        "docker_error",
                        error=f"docker_context_inspect_parse_output_error: {str(e)}",
                        data={
                            "docker_context_inspect_output": output,
                        },
                    )
                    raise e
                if context and len(context) > 0:
                    try:
                        docker_host = context[0].get("Endpoints", {}).get("docker", {}).get("Host")
                        if docker_host:
                            os.environ["DOCKER_HOST"] = docker_host
                    except Exception as e:
                        add_telemetry_event(
                            "docker_error",
                            error=f"docker_context_parse_host_error: {str(e)}",
                            data={
                                "context": json.dumps(context),
                            },
                        )
                        raise e
            except Exception:
                pass
        try:
            client = docker.from_env()  # type: ignore
        except Exception as e:
            add_telemetry_event(
                "docker_error",
                error=f"docker_get_client_from_env_error: {str(e)}",
            )
            raise e
        try:
            client.ping()
        except Exception as e:
            client_dict_non_sensitive = {k: v for k, v in client.api.__dict__.items() if "auth" not in k}
            add_telemetry_event(
                "docker_error",
                error=f"docker_ping_error: {str(e)}",
                data={
                    "client": repr(client_dict_non_sensitive),
                },
            )
            raise e
        return client
    except Exception:
        docker_location_message = ""
        if docker_host:
            docker_location_message = f"Trying to connect to Docker-compatible runtime at {docker_host}"

        raise CLILocalException(
            FeedbackManager.error(
                message=(
                    f"No container runtime is running. Make sure a Docker-compatible runtime is installed and running. "
                    f"{docker_location_message}\n\n"
                    "If you're using a custom location, please provide it using the DOCKER_HOST environment variable."
                )
            )
        )


def get_use_aws_creds() -> dict[str, str]:
    credentials: dict[str, str] = {}
    try:
        # Get the boto3 session and credentials
        session = boto3.Session()
        creds = session.get_credentials()

        if creds:
            # Create environment variables for the container based on boto credentials
            credentials["AWS_ACCESS_KEY_ID"] = creds.access_key
            credentials["AWS_SECRET_ACCESS_KEY"] = creds.secret_key

            # Add session token if it exists (for temporary credentials)
            if creds.token:
                credentials["AWS_SESSION_TOKEN"] = creds.token

            # Add region if available
            if session.region_name:
                credentials["AWS_DEFAULT_REGION"] = session.region_name

            click.echo(
                FeedbackManager.success(
                    message=f"✓ AWS credentials found and will be passed to Tinybird Local (region: {session.region_name or 'not set'})"
                )
            )
        else:
            click.echo(
                FeedbackManager.warning(
                    message="△ No AWS credentials found. S3 operations will not work in Tinybird Local."
                )
            )
    except Exception as e:
        click.echo(
            FeedbackManager.warning(
                message=f"△ Error retrieving AWS credentials: {str(e)}. S3 operations will not work in Tinybird Local."
            )
        )

    return credentials


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
