import os
import sys
import click
from click import secho
from adxp_cli.agent.validation import (
    validate_graph_yaml,
    LanggraphConfig,
    get_file_path,
)
from typing import Sequence, Optional, List, cast
from adxp_sdk.serves.schema import GraphPath


def run_server(host: str, port: int, graph_yaml: str):
    """Run the development server."""
    try:
        from adxp_sdk.serves.server import run_server
    except ImportError as e:
        py_version_msg = ""
        if sys.version_info < (3, 10) or sys.version_info > (3, 13):
            py_version_msg = (
                "\n\nNote: The in-mem server requires Python 3.10 ~ 3.12."
                f" You are currently using Python {sys.version_info.major}.{sys.version_info.minor}."
                ' Please upgrade your Python version before installing "adxp-cli". (run error)'
            )
        try:
            from importlib import util

            if not util.find_spec("adxp_sdk"):
                raise click.UsageError(
                    "Required package 'adxp-sdk' is not installed.\n"
                    "Please install it with:\n\n"
                    '    pip install -U "adxp-sdk"'
                    f"{py_version_msg}"
                )
        except ImportError:
            raise click.UsageError(
                "Could not verify package installation. Please ensure Python is up to date and\n"
                "Please install it with:\n\n"
                '    pip install -U "adxp-sdk"'
                f"{py_version_msg}"
            )
        raise click.UsageError(
            "Could not import run_server. This likely means your installation is incomplete.\n"
            "Please install it with:\n\n"
            '    pip install -U "adxp-sdk"'
            f"{py_version_msg}"
        )

    config_path = get_file_path(graph_yaml)
    config: LanggraphConfig = validate_graph_yaml(config_path)

    # include_path를 Python 경로에 추가
    include_path = config.package_directory
    include_path = get_file_path(include_path)
    if include_path not in sys.path:
        sys.path.append(include_path)

    env_path = config.env_file
    if env_path is not None:
        env_path = get_file_path(env_path)

    if isinstance(config.graph_path, str):
        graph_path = config.graph_path
        abs_graph_path = get_file_path(graph_path)
        secho(
            f"Starting server at {host}:{port}. Graph path: {abs_graph_path}",
            fg="green",
        )
        run_server(
            host=host,
            port=port,
            graph_path=abs_graph_path,
            env_file=env_path,
        )
    elif isinstance(config.graph_path, list):
        abs_graph_path = []
        graph_paths: List[GraphPath] = cast(List[GraphPath], config.graph_path)
        for g in graph_paths:
            g.object_path = get_file_path(g.object_path)
            abs_graph_path.append(g)
        graph_path_msg = "\n".join(
            [f"  - {g.name}: '{g.object_path}'" for g in abs_graph_path]
        )
        secho(
            f"Starting server at {host}:{port}.\n Graph path:\n{graph_path_msg}",
        )
        run_server(
            host=host,
            port=port,
            graph_path=abs_graph_path,
            env_file=env_path,
        )
    else:
        raise click.UsageError(
            "Invalid graph_path in yaml file. graph_path must be a string or a list of dicts."
        )
