import rich_click as click

import flyte._cli._common as common


@click.group(name="delete")
def delete():
    """
    Delete a task or environment.
    """


@click.command(cls=common.CommandBase)
@click.argument("name", type=str, required=True)
@click.pass_obj
def secret(cfg: common.CLIConfig, name: str, project: str | None = None, domain: str | None = None):
    """
    Delete a secret.
    """
    from flyte.remote import Secret

    cfg.init(project, domain)
    Secret.delete(name=name)
