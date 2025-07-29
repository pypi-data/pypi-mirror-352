from pathlib import Path
from typing import get_args

import rich_click as click

import flyte._cli._common as common
from flyte.remote._secret import SecretTypes


@click.group(name="create")
def create():
    """
    Create a new task or environment.
    """


@create.command(cls=common.CommandBase)
@click.argument("name", type=str, required=True)
@click.argument("value", type=str, required=False)
@click.option("--from-file", type=click.Path(exists=True), help="Path to the file with the binary secret.")
@click.option(
    "--type", type=click.Choice(get_args(SecretTypes)), default="regular", help="Type of the secret.", show_default=True
)
@click.pass_obj
def secret(
    cfg: common.CLIConfig,
    name: str,
    value: str | bytes | None = None,
    from_file: str | None = None,
    type: SecretTypes = "regular",
    project: str | None = None,
    domain: str | None = None,
):
    """
    Create a new secret.
    """
    from flyte.remote import Secret

    cfg.init(project, domain)
    if from_file:
        with open(from_file, "rb") as f:
            value = f.read()
    Secret.create(name=name, value=value, type=type)


@create.command(cls=common.CommandBase)
@click.option("--endpoint", type=str, help="Endpoint of the Flyte backend.")
@click.option("--insecure", is_flag=True, help="Use insecure connection to the Flyte backend.")
@click.option(
    "--org",
    type=str,
    required=False,
    help="Organization to use, this will override the organization in the config file.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=Path.cwd(),
    help="Path to the output dir where the config will be saved, defaults to current directory.",
)
def config(
    output: Path,
    endpoint: str | None = None,
    insecure: bool = False,
    org: str | None = None,
    project: str | None = None,
    domain: str | None = None,
):
    """
    Create a new config file.
    """
    import yaml

    output_file = output / "config.yaml"
    with open(output_file, "w") as f:
        d = {
            "admin": {
                "endpoint": endpoint,
                "insecure": insecure,
            },
            "task": {
                "org": org,
                "project": project,
                "domain": domain,
            },
        }
        yaml.dump(d, f)

    click.echo(f"Config file created at {output_file}")
