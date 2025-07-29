from __future__ import annotations

import inspect
from dataclasses import dataclass, field, fields
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, cast

import click
from click import Context, Parameter
from rich.console import Console
from typing_extensions import get_args

import flyte

from .._code_bundle._utils import CopyFiles
from .._task import TaskTemplate
from ..remote import Run
from . import _common as common
from ._common import CLIConfig
from ._params import to_click_option


@dataclass
class RunArguments:
    project: str = field(
        default=cast(str, common.PROJECT_OPTION.default), metadata={"click.option": common.PROJECT_OPTION}
    )
    domain: str = field(
        default=cast(str, common.DOMAIN_OPTION.default), metadata={"click.option": common.DOMAIN_OPTION}
    )
    local: bool = field(
        default=False,
        metadata={
            "click.option": click.Option(
                ["--local"],
                is_flag=True,
                help="Run the task locally",
            )
        },
    )
    copy_style: CopyFiles = field(
        default="loaded_modules",
        metadata={
            "click.option": click.Option(
                ["--copy-style"],
                type=click.Choice(get_args(CopyFiles)),
                default="loaded_modules",
                help="Copy style to use when running the task",
            )
        },
    )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> RunArguments:
        return cls(**d)

    @classmethod
    def options(cls) -> List[click.Option]:
        """
        Return the set of base parameters added to run subcommand.
        """
        return [common.get_option_from_metadata(f.metadata) for f in fields(cls) if f.metadata]


class RunTaskCommand(click.Command):
    def __init__(self, obj_name: str, obj: Any, run_args: RunArguments, *args, **kwargs):
        self.obj_name = obj_name
        self.obj = cast(TaskTemplate, obj)
        self.run_args = run_args
        kwargs.pop("name", None)
        super().__init__(obj_name, *args, **kwargs)

    def invoke(self, ctx: Context):
        obj: CLIConfig = ctx.obj or CLIConfig()
        assert obj.endpoint, "CLI Config should have an endpoint"
        obj.init(self.run_args.project, self.run_args.domain)

        r = flyte.with_runcontext(
            copy_style=self.run_args.copy_style,
            version=self.run_args.copy_style,
            mode="local" if self.run_args.local else "remote",
        ).run(self.obj, **ctx.params)
        if isinstance(r, Run) and r.action is not None:
            console = Console()
            console.print(
                common.get_panel(
                    "Run",
                    f"[green bold]Created Run: {r.name} [/green bold] "
                    f"(Project: {r.action.action_id.run.project}, Domain: {r.action.action_id.run.domain})\n\n"
                    f"[blue bold]{r.url}[/blue bold]",
                )
            )

    def get_params(self, ctx: Context) -> List[Parameter]:
        # Note this function may be called multiple times by click.
        task = self.obj
        from .._internal.runtime.types_serde import transform_native_to_typed_interface

        interface = transform_native_to_typed_interface(task.native_interface)
        if interface is None:
            return super().get_params(ctx)
        inputs_interface = task.native_interface.inputs

        params: List[Parameter] = []
        for name, var in interface.inputs.variables.items():
            default_val = None
            if inputs_interface[name][1] is not inspect._empty:
                default_val = inputs_interface[name][1]
            params.append(to_click_option(name, var, inputs_interface[name][0], default_val))

        self.params = params
        return super().get_params(ctx)


class TaskPerFileGroup(common.ObjectsPerFileGroup):
    """
    Group that creates a command for each task in the current directory that is not __init__.py.
    """

    def __init__(self, filename: Path, run_args: RunArguments, *args, **kwargs):
        args = (filename, *args)
        super().__init__(*args, **kwargs)
        self.run_args = run_args

    def _filter_objects(self, module: ModuleType) -> Dict[str, Any]:
        return {k: v for k, v in module.__dict__.items() if isinstance(v, TaskTemplate)}

    def _get_command_for_obj(self, ctx: click.Context, obj_name: str, obj: Any) -> click.Command:
        obj = cast(TaskTemplate, obj)
        return RunTaskCommand(
            obj_name=obj_name,
            obj=obj,
            help=obj.docs.__help__str__() if obj.docs else None,
            run_args=self.run_args,
        )


class TaskFiles(common.FileGroup):
    """
    Group that creates a command for each file in the current directory that is not __init__.py.
    """

    common_options_enabled = False

    def __init__(
        self,
        *args,
        directory: Path | None = None,
        **kwargs,
    ):
        if "params" not in kwargs:
            kwargs["params"] = []
        kwargs["params"].extend(RunArguments.options())
        super().__init__(*args, directory=directory, **kwargs)

    def get_command(self, ctx, filename):
        run_args = RunArguments.from_dict(ctx.params)
        fp = Path(filename)
        if not fp.exists():
            raise click.BadParameter(f"File {filename} does not exist")
        if fp.is_dir():
            return TaskFiles(directory=fp)
        return TaskPerFileGroup(
            filename=Path(filename),
            run_args=run_args,
            name=filename,
            help=f"Run, functions decorated `env.task` or instances of Tasks in {filename}",
        )


run = TaskFiles(
    name="run",
    help="Run a task from a python file",
)
