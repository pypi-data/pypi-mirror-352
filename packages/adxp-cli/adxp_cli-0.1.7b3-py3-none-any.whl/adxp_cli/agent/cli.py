import click
import json
from click import secho
import pathlib
import shutil
from typing import Sequence, Optional
from adxp_cli.agent.docker import (
    generate_graph_dockerfile,
    dockerfile_build,
    create_dockerfile_and_build,
)
from adxp_cli.common.exec import Runner, subp_exec
from adxp_cli.common.progress import Progress
from adxp_cli.agent.validation import (
    validate_graph_yaml,
    LanggraphConfig,
)
from adxp_cli.common.utils import (
    get_python_version,
    save_docker_credentials,
    load_docker_credentials,
)
from adxp_cli.agent.run import run_server

from adxp_cli.agent.deployment import (
    get_agent_app_list,
    get_agent_app_detail,
    create_new_apikey,
    regenerate_apikey,
    delete_apikey_by_number,
    stop_deployment,
    restart_deployment,
    delete_app,
    add_agent_deployment,
    update_app,
)
from adxp_cli.agent.deployment import deploy_agent_app


@click.group()
def agent():
    """Command-line interface for AIP server management."""
    pass


# 2. Run API Server on Local
@agent.command(help="🖥 Run the API server on local")
@click.option("--host", default="127.0.0.1", help="Host address")
@click.option("--port", default=28080, type=int, help="Port number")
@click.option("--graph_yaml", default="./graph.yaml", help="Path to graph.yaml")
def run(host, port, graph_yaml):
    run_server(host, port, graph_yaml)


@agent.command(help="🐳 Generate a Dockerfile for Agent API Server")
@click.option("--output", default="./sktaip.Dockerfile", help="Path to Dockerfile")
@click.option("--graph_yaml", default="./graph.yaml", help="Path to graph.yaml")
def dockerfile(output: str, graph_yaml: str) -> None:
    """Dockerfile 내용을 생성합니다."""
    save_path = pathlib.Path(output).absolute()
    secho(f"🔍 Validating configuration at path: {graph_yaml}", fg="yellow")
    config: LanggraphConfig = validate_graph_yaml(graph_yaml)
    secho("✅ Configuration validated!", fg="green")
    secho(f"📝 Generating Dockerfile at {save_path}", fg="yellow")
    python_version = get_python_version()
    dockerfile_content = generate_graph_dockerfile(config, python_version)
    with open(str(save_path), "w", encoding="utf-8") as f:
        f.write(dockerfile_content)
    secho("✅ Created: Dockerfile", fg="green")


@agent.command(help="🐳 Build a Docker image for Agent API Server")
@click.option(
    "--tag",
    "-t",
    help="""Tag for the docker image.

    \b
    Example:
        langgraph build -t my-image

    \b
    """,
    required=True,
)
@click.option(
    "--dockerfile",
    "-f",
    help="""File path to the Dockerfile. If not provided, a Dockerfile will be generated automatically.
    """,
    required=False,
    default=None,
)
@click.option(
    "--base-image",
    hidden=True,
)
@click.option("--graph_yaml", default="./graph.yaml", help="Path to graph.yaml")
@click.option("--pull", is_flag=True, help="Pull the latest base image")
@click.option("--directory", "-d", help="Directory to build the image", default=".")
@click.argument("docker_build_args", nargs=-1, type=click.UNPROCESSED)
def build(
    graph_yaml: str,
    docker_build_args: Sequence[str],
    base_image: Optional[str],
    tag: str,
    pull: bool,
    directory: str,
    dockerfile: Optional[str],
):
    # Docker 설치 확인
    if shutil.which("docker") is None:
        raise click.ClickException("Docker가 설치되어 있지 않습니다.")

    secho(f"🔍 Validating configuration at path: {graph_yaml}", fg="yellow")
    config: LanggraphConfig = validate_graph_yaml(graph_yaml)
    secho("✅ Configuration validated!", fg="green")
    if dockerfile:
        secho(f"📝 Using Dockerfile at {dockerfile}", fg="yellow")
        dockerfile_build(directory, dockerfile, tag, docker_build_args)
    else:
        create_dockerfile_and_build(
            base_image, tag, config, docker_build_args, pull, directory
        )


@agent.command(help="Get List of Deployed Agents")
@click.option("--page", default=1, help="page number, default: 1")
@click.option("--size", default=10, help="size of page, default: 10")
@click.option("--search", default=None, help="search app by name")
@click.option(
    "--all", "-a", is_flag=True, default=False, help="show agents with all columns"
)
def ls(page: int, size: int, search: Optional[str], all: bool):
    """Get List of Agents"""
    get_agent_app_list(page, size, search, all)


@agent.command(help="Get Detail of Deployed Agent")
@click.option("--app-id", "-i", required=True, help="Agent App ID")
@click.option(
    "--dev", is_flag=True, default=False, help="Include development information"
)
def get(app_id: str, dev: bool):
    """Get Detail of Deployed Agent"""
    get_agent_app_detail(app_id, dev)


@agent.command(help="Create Additional Api Key for Deployed Agent")
@click.option("--app-id", "-i", required=True, help="Agent App ID")
def create_apikey(app_id: str):
    """Create Additional Api Key for Deployed Agent"""
    create_new_apikey(app_id)


@agent.command(help="Regenerate Api Key for Deployed Agent")
@click.option("--app-id", "-i", required=True, help="Agent App ID")
@click.option(
    "--number",
    "-n",
    required=True,
    type=int,
    default=1,
    help="Number of Api Key to Regenerate. Default: 1. Check number of api key with 'adxp-cli agent get -i <app_id>'",
)
def regen_apikey(app_id: str, number: int):
    """Regenerate Api Key for Deployed Agent"""
    regenerate_apikey(app_id, number)


@agent.command(help="Delete Api Key for Deployed Agent")
@click.option("--app-id", "-i", required=True, help="Agent App ID")
@click.option(
    "--number", "-n", required=True, type=int, help="Number of Api Key to Delete"
)
def delete_apikey(app_id: str, number: int):
    """Delete Api Key for Deployed Agent"""
    delete_apikey_by_number(app_id, number)


@agent.command(help="Deploy Agent App to A.X Platform")
@click.option(
    "--image",
    "-t",
    required=True,
    help="Image Tag. Example: https://myregistry.azurecr.io/myrepo/sample-app:v0.0.1",
)
@click.option("--model", "-m", required=False, multiple=True, help="Model")
@click.option("--name", "-n", required=True, help="Name")
@click.option("--description", "-d", required=False, default="", help="Description")
@click.option("--env-path", "-e", required=False, help="Path to .env file")
@click.option("--app-id", "-i", required=False, help="App ID")
def deploy(
    image: str,
    model: list[str],
    name: str,
    description: str,
    env_path: str,
    app_id: Optional[str],
):
    """Deploy Agent App to A.X Platform"""
    if app_id is None:
        deploy_agent_app(image, list(model), name, description, env_path)
    else:
        add_agent_deployment(image, list(model), name, description, env_path, app_id)


@agent.command(help="Stop Deployment")
@click.option("--deployment-id", "-d", required=True, help="Deployment ID")
def stop(deployment_id: str):
    """Stop Deployment"""
    stop_deployment(deployment_id)


@agent.command(help="Restart Deployment")
@click.option("--deployment-id", "-d", required=True, help="Deployment ID")
def restart(deployment_id: str):
    """Restart Deployment"""
    restart_deployment(deployment_id)


@agent.command(help="Delete Deployment or APP")
@click.option("--deployment-id", "-d", required=False, help="Deployment ID")
@click.option("--app-id", "-i", required=False, help="App ID")
def delete(deployment_id: Optional[str], app_id: Optional[str]):
    """Delete Deployment or APP"""
    if not deployment_id and not app_id:
        raise click.ClickException("Deployment ID or App ID must be provided")
    if deployment_id and app_id:
        raise click.ClickException(
            "Deployment ID and App ID cannot both be provided. Please provide only one of them."
        )
    delete_app(deployment_id, app_id)


@agent.command(help="Update App")
@click.option("--app-id", "-i", required=True, help="App ID")
@click.option("--name", "-n", required=False, help="Name")
@click.option("--description", "-d", required=False, help="Description")
def update(app_id: str, name: Optional[str], description: Optional[str]):
    """Update App"""
    update_app(app_id, name, description)
