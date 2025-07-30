#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2025.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import typer
from typing_extensions import Annotated

from ibm_watsonx_ai_cli.utils.chat import ChatAgent
from ibm_watsonx_ai_cli.utils.github import (
    download_and_extract_resource,
    get_available_resources,
)
from ibm_watsonx_ai_cli.utils.utils import (
    ensure_template_is_cli_compatible,
    get_directory,
    get_package_name,
    get_package_root,
    get_resource_name,
    is_cli_compatible,
    load_question_payload,
    prepare_resources_prompt,
    prompt_choice,
)

cli = typer.Typer(no_args_is_help=True)


@cli.command(help="List of available templates.")
def list() -> None:
    """
    List all available templates.

    Usage:
        watsonx-ai template list
    """
    agents = get_available_resources(resource_type="template")
    typer.echo(prepare_resources_prompt(agents, resource_type="template"))


@cli.command(help="Creates a selected template in a local environment.")
def new(
    name: Annotated[str | None, typer.Argument(help="Template name")] = None,
    target: Annotated[
        str | None, typer.Argument(help="The name of the folder to create")
    ] = None,
) -> None:
    """
    Create a template in a local environment.

    Args:
        name (str | None): The name of the template to use. If not provided, the user will be prompted to choose one.
        target (str | None): The target folder where the template will be downloaded. If not provided, the user will be prompted to enter one.

    Usage:
        watsonx-ai template new [TEMPLATE_NAME] [TARGET_FOLDER]
    """
    available_agents = get_available_resources(resource_type="template")
    selected_agent = get_resource_name(
        available_resources=available_agents,
        resource_name=name,
        resource_type="template",
    )
    target_directory = get_directory(
        selected_agent,
        target,
    )

    typer.echo(
        typer.style(
            f"---> Downloading template '{selected_agent}' into '{target_directory}'...",
            fg="bright_green",
            bold=True,
        )
    )
    target_directory = download_and_extract_resource(
        selected_agent, target_directory, resource_type="template"
    )
    typer.echo(
        typer.style(
            f"---> Template '{selected_agent}' downloaded successfully into '{target_directory}'.",
            fg="bright_green",
            bold=True,
        )
    )
    cli_compatible = is_cli_compatible(Path().cwd() / target_directory)

    if cli_compatible:
        typer.echo(
            typer.style(
                "\nNext steps\n",
                fg="bright_blue",
                bold=True,
            )
        )

        typer.echo(
            typer.style(
                "Configure your agent:\n\n"
                "Before running or deploying the agent, copy and update your configuration file:\n\n"
                f"  cd {target_directory}\n"
                "  cp config.toml.example config.toml\n\n"
                "Run the agent locally:\n\n"
                '  watsonx-ai template invoke "<your-question>"\n\n'
                "Deploy the agent as an AI service:\n\n"
                "  watsonx-ai service new\n",
            )
        )
    else:
        typer.echo(
            typer.style(
                "\nPlease refer to the README.md file for usage details.",
                fg="bright_blue",
                bold=True,
            )
        )


@cli.command(help="Executes the template code locally with demo data.")
def invoke(
    query: Annotated[str | None, typer.Argument(help="Content of User Message")] = None,
) -> None:
    """
    Execute the template code locally using demo data.

    Args:
        query (str | None): The query to send to the locally executed template.

    Usage:
        watsonx-ai template invoke "<question>"
    """
    ensure_template_is_cli_compatible(
        project_directory=Path().cwd(), cli_method="watsonx-ai template invoke"
    )

    project_directory = get_package_root()

    template_name = project_directory.name
    pyproject_path = project_directory / "pyproject.toml"
    package_name = get_package_name(pyproject_path)
    package_spec = importlib.util.find_spec(package_name.replace("-", "_"))

    if package_spec is None:
        install_library = prompt_choice(
            question=f"Would you be willing to install the '{package_name}' library? This library is essential for the operation of your AI service.",
            options=["y", "n"],
        )

        if install_library == "y":
            typer.echo(
                typer.style(
                    f"---> Starting installation of `{template_name}` template ...",
                    fg="bright_green",
                    bold=True,
                )
            )
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-qe", "."],
                check=True,
                cwd=project_directory,
            )
            typer.echo(
                typer.style(
                    f"---> Successfully installed `{template_name}` template ...",
                    fg="bright_green",
                    bold=True,
                )
            )
            # Restart the process to pick up the newly installed library.
            if not os.environ.get("RESTARTED"):
                os.environ["RESTARTED"] = "1"
                os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            typer.echo(
                typer.style(
                    "Installation aborted. The library is required to proceed.",
                    fg="bright_red",
                    bold=True,
                )
            )
            raise typer.Exit(code=1)

    chat_agent = ChatAgent(agent_root_directory=project_directory)

    if query is None:
        query = load_question_payload()

    chat_agent.chat_with_agent_locally(agent_payload=query)


if __name__ == "__main__":
    cli()
