import asyncio
from typing import Tuple, Union

import rich_click as click
from rich.console import Console
from rich.pretty import pretty_repr

from . import _common as common


@click.group(name="get")
def get():
    """
    Get the value of a task or environment.
    """


@get.command()
@click.argument("name", type=str, required=False)
@click.pass_obj
def project(cfg: common.CLIConfig, name: str | None = None):
    """
    Get the current project.
    """
    from flyte.remote import Project

    print(cfg)
    cfg.init()

    console = Console()
    if name:
        console.print(pretty_repr(Project.get(name)))
    else:
        console.print(common.get_table("Projects", Project.listall()))


@get.command(cls=common.CommandBase)
@click.argument("name", type=str, required=False)
@click.pass_obj
def run(cfg: common.CLIConfig, name: str | None = None, project: str | None = None, domain: str | None = None):
    """
    Get the current run.
    """
    from flyte.remote import Run, RunDetails

    cfg.init(project=project, domain=domain)

    console = Console()
    if name:
        details = RunDetails.get(name=name)
        console.print(pretty_repr(details))
    else:
        console.print(common.get_table("Runs", Run.listall()))


@get.command(cls=common.CommandBase)
@click.argument("name", type=str, required=False)
@click.argument("version", type=str, required=False)
@click.pass_obj
def task(
    cfg: common.CLIConfig,
    name: str | None = None,
    version: str | None = None,
    project: str | None = None,
    domain: str | None = None,
):
    """
    Get the current task.
    """
    from flyte.remote import Task

    cfg.init(project=project, domain=domain)

    console = Console()
    if name:
        if not version:
            raise click.BadParameter("Version is required when getting a task by name.")
        v = Task.get(name=name, version=version)
        if v is None:
            raise click.BadParameter(f"Task {name} not found.")
        t = v.fetch(v)
        console.print(pretty_repr(t))
    else:
        raise click.BadParameter("Task listing is not supported yet, please provide a name.")
        # console.print(common.get_table("Tasks", Task.listall()))


@get.command(cls=common.CommandBase)
@click.argument("run_name", type=str, required=True)
@click.argument("action_name", type=str, required=False)
@click.pass_obj
def action(
    cfg: common.CLIConfig,
    run_name: str,
    action_name: str | None = None,
    project: str | None = None,
    domain: str | None = None,
):
    """
    Get all actions for a run or details for a specific action.
    """
    import flyte.remote as remote

    cfg.init(project=project, domain=domain)

    console = Console()
    if action_name:
        console.print(pretty_repr(remote.Action.get(run_name=run_name, name=action_name)))
    else:
        # List all actions for the run
        console.print(common.get_table(f"Actions for {run_name}", remote.Action.listall(for_run_name=run_name)))


@get.command(cls=common.CommandBase)
@click.argument("run_name", type=str, required=True)
@click.argument("action_name", type=str, required=False)
@click.option("--lines", "-l", type=int, default=30, help="Number of lines to show, only useful for --pretty")
@click.option("--show-ts", is_flag=True, help="Show timestamps")
@click.option(
    "--pretty",
    is_flag=True,
    default=False,
    help="Show logs in a auto scrolling box, where number of lines is limited to `--lines`",
)
@click.option("--attempt", "-a", type=int, default=None, help="Attempt number to show logs for")
@click.pass_obj
def logs(
    cfg: common.CLIConfig,
    run_name: str,
    action_name: str | None = None,
    project: str | None = None,
    domain: str | None = None,
    lines: int = 30,
    show_ts: bool = False,
    pretty: bool = True,
    attempt: int | None = None,
):
    """
    Get the current run.
    """
    import flyte.remote as remote

    cfg.init(project=project, domain=domain)

    async def _run_log_view(_obj):
        task = asyncio.create_task(_obj.show_logs(max_lines=lines, show_ts=show_ts, raw=not pretty, attempt=attempt))
        try:
            await task
        except KeyboardInterrupt:
            task.cancel()

    if action_name:
        obj = remote.Action.get(run_name=run_name, name=action_name)
    else:
        obj = remote.Run.get(run_name)
    asyncio.run(_run_log_view(obj))


@get.command(cls=common.CommandBase)
@click.argument("name", type=str, required=False)
@click.pass_obj
def secret(
    cfg: common.CLIConfig,
    name: str | None = None,
    project: str | None = None,
    domain: str | None = None,
):
    """
    Get the current secret.
    """
    import flyte.remote as remote

    cfg.init(project=project, domain=domain)

    console = Console()
    if name:
        console.print(pretty_repr(remote.Secret.get(name)))
    else:
        console.print(common.get_table("Secrets", remote.Secret.listall()))


@get.command(cls=common.CommandBase)
@click.argument("run_name", type=str, required=True)
@click.argument("action_name", type=str, required=False)
@click.option("--inputs-only", "-i", is_flag=True, help="Show only inputs")
@click.option("--outputs-only", "-o", is_flag=True, help="Show only outputs")
@click.pass_obj
def io(
    cfg: common.CLIConfig,
    run_name: str,
    action_name: str | None = None,
    project: str | None = None,
    domain: str | None = None,
    inputs_only: bool = False,
    outputs_only: bool = False,
):
    """
    Get the inputs and outputs of a run or action.
    """
    if inputs_only and outputs_only:
        raise click.BadParameter("Cannot use both --inputs-only and --outputs-only")

    import flyte.remote as remote

    cfg.init(project=project, domain=domain)
    console = Console()
    if action_name:
        obj = remote.ActionDetails.get(run_name=run_name, name=action_name)
    else:
        obj = remote.RunDetails.get(run_name)

    async def _get_io(
        details: Union[remote.RunDetails, remote.ActionDetails],
    ) -> Tuple[remote.ActionInputs | None, remote.ActionOutputs | None | str]:
        if inputs_only or outputs_only:
            if inputs_only:
                return await details.inputs(), None
            elif outputs_only:
                return None, await details.outputs()
        inputs = await details.inputs()
        outputs: remote.ActionOutputs | None | str = None
        try:
            outputs = await details.outputs()
        except Exception:
            # If the outputs are not available, we can still show the inputs
            outputs = "[red]not yet available[/red]"
        return inputs, outputs

    inputs, outputs = asyncio.run(_get_io(obj))
    # Show inputs and outputs side by side
    console.print(
        common.get_panel(
            "Inputs & Outputs",
            f"[green bold]Inputs[/green bold]\n{inputs}\n\n[blue bold]Outputs[/blue bold]\n{outputs}",
        )
    )


@get.command(cls=click.RichCommand)
@click.pass_obj
def config(cfg: common.CLIConfig):
    """
    Shows the automatically detected configuration to connect with remote Flyte services.
    """
    console = Console()
    console.print(cfg)
