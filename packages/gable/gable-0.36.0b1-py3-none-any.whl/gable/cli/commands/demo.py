import os
import subprocess
import tempfile

import click
from click.core import Context as ClickContext
from gable.api.client import GableAPIClient
from gable.cli.helpers.npm import get_sca_cmd, prepare_npm_environment
from gable.cli.options import global_options
from loguru import logger


@click.group(hidden=True)
def demo():
    """Demo commands"""


@demo.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
)
@global_options(add_endpoint_options=False)
@click.option(
    "--project-root",
    help="The root directory of the Java project that will be analyzed.",
    type=click.Path(exists=True),
    required=True,
)
@click.option(
    "--source-root",
    help="The source code directory of the Java project that will be analyzed.",
    type=click.Path(exists=True),
    required=False,
)
@click.option(
    "--build-command",
    help="The build command used to build the Java project (e.g. mvn clean install).",
    type=str,
    required=False,
)
@click.option(
    "--java-version",
    help="The version of Java used to build the project.",
    type=str,
    default="17",
)
@click.option(
    "--llm-extraction/--no-llm-extraction",
    help="Use LLM for feature extraction.",
    type=bool,
    default=False,
    is_flag=True,
)
@click.pass_context
def java_dataflow(
    ctx: ClickContext,
    project_root: str,
    build_command: str,
    java_version: str,
    source_root: str,
    llm_extraction: bool,
):
    """Prints connections between sources and sinks in Java code"""
    if os.getenv("GABLE_CLI_ISOLATION", "false").lower() == "true":
        print("GABLE_CLI_ISOLATION is true, skipping NPM authentication")
    else:
        client: GableAPIClient = ctx.obj.client
        prepare_npm_environment(client)
    args = (
        [
            "java-dataflow",
            project_root,
            "--java-version",
            java_version,
        ]
        + (["--build-command", build_command] if build_command else [])
        + (["--source-root", source_root] if source_root else [])
    )
    cmd = get_sca_cmd(None, args)

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        logger.debug(result.stderr)
        raise click.ClickException(f"Error running Gable SCA: {result.stderr}")

    if not llm_extraction:
        print("Skipping LLM feature extraction")
        print(result.stdout)
        return

    logger.trace(result.stderr)
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".json", encoding="utf-8"
    ) as f:
        f.write(result.stdout)
    feature_extraction_cmd = [
        "./venv/bin/python",
        "-m",
        "main",
        "--repo",
        os.path.abspath(project_root),
        "--sca",
        f.name,
    ]
    feature_extraction_result = subprocess.run(
        feature_extraction_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../../../../sca-pl-mve/",
        ),
    )
    logger.debug(
        f"Calling feature extraction subprocess: {' '.join(feature_extraction_cmd)}"
    )
    if feature_extraction_result.returncode != 0:
        logger.debug(feature_extraction_result.stdout)
        logger.debug(feature_extraction_result.stderr)
        raise click.ClickException(
            f"Error running Gable feature extraction: {feature_extraction_result.stderr}"
        )
    print(feature_extraction_result.stdout)
