from __future__ import annotations

import pathlib
import uuid
from typing import TYPE_CHECKING, Any, Literal, Optional, Tuple, Union, cast

from flyte.errors import InitializationError

from ._api_commons import syncer
from ._context import contextual_run, internal_ctx
from ._environment import Environment
from ._initialize import (
    _get_init_config,
    get_client,
    get_common_config,
    get_storage,
    requires_initialization,
    requires_storage,
)
from ._logging import logger
from ._task import P, R, TaskTemplate
from ._tools import ipython_check
from .models import ActionID, Checkpoints, CodeBundle, RawDataPath, SerializationContext, TaskContext

if TYPE_CHECKING:
    from flyte.remote import Run

    from ._code_bundle import CopyFiles

Mode = Literal["local", "remote", "hybrid"]


async def _get_code_bundle_for_run(name: str) -> CodeBundle | None:
    """
    Get the code bundle for the run with the given name.
    This is used to get the code bundle for the run when running in hybrid mode.
    """
    from flyte._internal.runtime.task_serde import extract_code_bundle
    from flyte.remote import Run

    run = await Run.get.aio(Run, name=name)
    if run:
        run_details = await run.details()
        spec = run_details.action_details.pb2.resolved_task_spec
        return extract_code_bundle(spec)
    return None


@syncer.wrap
class _Runner:
    def __init__(
        self,
        force_mode: Mode | None = None,
        name: Optional[str] = None,
        service_account: Optional[str] = None,
        version: Optional[str] = None,
        copy_style: CopyFiles = "loaded_modules",
        dry_run: bool = False,
        copy_bundle_to: pathlib.Path | None = None,
        interactive_mode: bool | None = None,
        raw_data_path: str | None = None,
        metadata_path: str | None = None,
        run_base_dir: str | None = None,
    ):
        init_config = _get_init_config()
        client = init_config.client if init_config else None
        if not force_mode and client is not None:
            force_mode = "remote"
        force_mode = force_mode or "local"
        logger.debug(f"Effective run mode: {force_mode}, client configured: {client is not None}")
        self._mode = force_mode
        self._name = name
        self._service_account = service_account
        self._version = version
        self._copy_files = copy_style
        self._dry_run = dry_run
        self._copy_bundle_to = copy_bundle_to
        self._interactive_mode = interactive_mode if interactive_mode else ipython_check()
        self._raw_data_path = raw_data_path
        self._metadata_path = metadata_path or "/tmp"
        self._run_base_dir = run_base_dir or "/tmp/base"

    @requires_initialization
    async def _run_remote(self, obj: TaskTemplate[P, R], *args: P.args, **kwargs: P.kwargs) -> Run:
        from flyte.remote import Run

        from ._code_bundle import build_code_bundle, build_pkl_bundle
        from ._deploy import build_images, plan_deploy
        from ._internal.runtime.convert import convert_from_native_to_inputs
        from ._internal.runtime.task_serde import translate_task_to_wire
        from ._protos.common import identifier_pb2
        from ._protos.workflow import run_definition_pb2, run_service_pb2

        cfg = get_common_config()

        if obj.parent_env is None:
            raise ValueError("Task is not attached to an environment. Please attach the task to an environment.")

        deploy_plan = plan_deploy(cast(Environment, obj.parent_env()))
        image_cache = await build_images(deploy_plan)

        if self._interactive_mode:
            code_bundle = await build_pkl_bundle(
                obj, upload_to_controlplane=not self._dry_run, copy_bundle_to=self._copy_bundle_to
            )
        else:
            if self._copy_files != "none":
                code_bundle = await build_code_bundle(
                    from_dir=cfg.root_dir, dryrun=self._dry_run, copy_bundle_to=self._copy_bundle_to
                )
            else:
                code_bundle = None

        version = self._version or (
            code_bundle.computed_version if code_bundle and code_bundle.computed_version else None
        )
        if not version:
            raise ValueError("Version is required when running a task")
        s_ctx = SerializationContext(
            code_bundle=code_bundle,
            version=version,
            image_cache=image_cache,
            root_dir=cfg.root_dir,
        )
        task_spec = translate_task_to_wire(obj, s_ctx)
        inputs = await convert_from_native_to_inputs(obj.native_interface, *args, **kwargs)

        if not self._dry_run:
            if get_client() is None:
                # This can only happen, if the user forces flyte.run(mode="remote") without initializing the client
                raise InitializationError(
                    "ClientNotInitializedError",
                    "user",
                    "flyte.run requires client to be initialized. "
                    "Call flyte.init() with a valid endpoint or api-key before using this function.",
                )
            run_id = None
            project_id = None
            if self._name:
                run_id = run_definition_pb2.RunIdentifier(
                    project=cfg.project,
                    domain=cfg.domain,
                    org=cfg.org,
                    name=self._name if self._name else None,
                )
            else:
                project_id = identifier_pb2.ProjectIdentifier(
                    name=cfg.project,
                    domain=cfg.domain,
                    organization=cfg.org,
                )
            # Fill in task id inside the task template if it's not provided.
            # Maybe this should be done here, or the backend.
            if task_spec.task_template.id.project == "":
                task_spec.task_template.id.project = cfg.project if cfg.project else ""
            if task_spec.task_template.id.domain == "":
                task_spec.task_template.id.domain = cfg.domain if cfg.domain else ""
            if task_spec.task_template.id.org == "":
                task_spec.task_template.id.org = cfg.org if cfg.org else ""
            if task_spec.task_template.id.version == "":
                task_spec.task_template.id.version = version

            resp = await get_client().run_service.CreateRun(
                run_service_pb2.CreateRunRequest(
                    run_id=run_id,
                    project_id=project_id,
                    task_spec=task_spec,
                    inputs=inputs.proto_inputs,
                ),
            )
            return Run(pb2=resp.run)

        class DryRun(Run):
            def __init__(self, _task_spec, _inputs, _code_bundle):
                super().__init__(
                    pb2=run_definition_pb2.Run(
                        action=run_definition_pb2.Action(
                            id=run_definition_pb2.ActionIdentifier(
                                name="a0", run=run_definition_pb2.RunIdentifier(name="dry-run")
                            )
                        )
                    )
                )
                self.task_spec = _task_spec
                self.inputs = _inputs
                self.code_bundle = _code_bundle

        return DryRun(_task_spec=task_spec, _inputs=inputs, _code_bundle=code_bundle)

    @requires_storage
    @requires_initialization
    async def _run_hybrid(self, obj: TaskTemplate[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        """
        Run a task in hybrid mode. This means that the parent action will be run locally, but the child actions will be
        run in the cluster remotely. This is currently only used for testing,
        over the longer term we will productize this.
        """
        import flyte.report
        from flyte._code_bundle import build_code_bundle, build_pkl_bundle
        from flyte._deploy import build_images, plan_deploy
        from flyte.models import RawDataPath
        from flyte.storage import ABFS, GCS, S3

        from ._internal import create_controller
        from ._internal.runtime.taskrunner import run_task

        cfg = get_common_config()

        if obj.parent_env is None:
            raise ValueError("Task is not attached to an environment. Please attach the task to an environment.")

        deploy_plan = plan_deploy(cast(Environment, obj.parent_env()))
        image_cache = await build_images(deploy_plan)

        code_bundle = None
        if self._name is not None:
            # Check if remote run service has this run name already and if exists, then extract the code bundle from it.
            code_bundle = await _get_code_bundle_for_run(name=self._name)

        if not code_bundle:
            if self._interactive_mode:
                code_bundle = await build_pkl_bundle(
                    obj, upload_to_controlplane=not self._dry_run, copy_bundle_to=self._copy_bundle_to
                )
            else:
                if self._copy_files != "none":
                    code_bundle = await build_code_bundle(
                        from_dir=cfg.root_dir, dryrun=self._dry_run, copy_bundle_to=self._copy_bundle_to
                    )
                else:
                    code_bundle = None

        version = self._version or (
            code_bundle.computed_version if code_bundle and code_bundle.computed_version else None
        )
        if not version:
            raise ValueError("Version is required when running a task")

        project = cfg.project
        domain = cfg.domain
        org = cfg.org
        action_name = "a0"
        run_name = self._name
        random_id = str(uuid.uuid4())[:6]

        controller = create_controller("remote", endpoint="localhost:8090", insecure=True)
        action = ActionID(name=action_name, run_name=run_name, project=project, domain=domain, org=org)

        inputs = obj.native_interface.convert_to_kwargs(*args, **kwargs)
        # TODO: Ideally we should get this from runService
        # The API should be:
        # create new run, from run, in mode hybrid -> new run id, output_base, raw_data_path, inputs_path
        storage = get_storage()
        if type(storage) not in (S3, GCS, ABFS):
            raise ValueError(f"Unsupported storage type: {type(storage)}")
        if self._run_base_dir is None:
            raise ValueError(
                "Raw data path is required when running task, please set it in the run context:",
                " flyte.with_runcontext(run_base_dir='s3://bucket/metadata/outputs')",
            )
        output_path = self._run_base_dir
        raw_data_path = f"{output_path}/rd/{random_id}"
        raw_data_path_obj = RawDataPath(path=raw_data_path)
        checkpoint_path = f"{raw_data_path}/checkpoint"
        prev_checkpoint = f"{raw_data_path}/prev_checkpoint"
        checkpoints = Checkpoints(checkpoint_path, prev_checkpoint)

        async def _run_task() -> Tuple[Any, Optional[Exception]]:
            ctx = internal_ctx()
            tctx = TaskContext(
                action=action,
                checkpoints=checkpoints,
                code_bundle=code_bundle,
                output_path=output_path,
                version=version if version else "na",
                raw_data_path=raw_data_path_obj,
                compiled_image_cache=image_cache,
                run_base_dir=self._run_base_dir,
                report=flyte.report.Report(name=action.name),
            )
            async with ctx.replace_task_context(tctx):
                return await run_task(tctx=tctx, controller=controller, task=obj, inputs=inputs)

        outputs, err = await contextual_run(_run_task)
        if err:
            raise err
        return outputs

    async def _run_local(self, obj: TaskTemplate[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        from flyte._internal.controllers import create_controller
        from flyte._internal.runtime.convert import (
            convert_error_to_native,
            convert_from_native_to_inputs,
            convert_outputs_to_native,
        )
        from flyte._internal.runtime.entrypoints import direct_dispatch

        controller = create_controller("local")
        inputs = await convert_from_native_to_inputs(obj.native_interface, *args, **kwargs)
        if self._name is None:
            action = ActionID.create_random()
        else:
            action = ActionID(name=self._name)
        out, err = await direct_dispatch(
            obj,
            action=action,
            raw_data_path=internal_ctx().raw_data,
            version="na",
            controller=controller,
            inputs=inputs,
            output_path=self._metadata_path,
            run_base_dir=self._metadata_path,
            checkpoints=Checkpoints(
                prev_checkpoint_path=internal_ctx().raw_data.path, checkpoint_path=internal_ctx().raw_data.path
            ),
        )  # type: ignore
        if err:
            native_err = convert_error_to_native(err)
            if native_err:
                raise native_err
        if obj.native_interface.outputs and len(obj.native_interface.outputs) > 0:
            if out is not None:
                return cast(R, await convert_outputs_to_native(obj.native_interface, out))
        return cast(R, None)

    async def run(self, task: TaskTemplate[P, Union[R, Run]], *args: P.args, **kwargs: P.kwargs) -> Union[R, Run]:
        """
        Run an async `@env.task` or `TaskTemplate` instance. The existing async context will be used.

        Example:
        ```python
        import flyte
        env = flyte.TaskEnvironment("example")

        @env.task
        async def example_task(x: int, y: str) -> str:
            return f"{x} {y}"

        if __name__ == "__main__":
            flyte.run(example_task, 1, y="hello")
        ```

        :param task: TaskTemplate instance `@env.task` or `TaskTemplate`
        :param args: Arguments to pass to the Task
        :param kwargs: Keyword arguments to pass to the Task
        :return: Run instance or the result of the task
        """
        if self._mode == "remote":
            return await self._run_remote(task, *args, **kwargs)
        if self._mode == "hybrid":
            return await self._run_hybrid(task, *args, **kwargs)

        # TODO We could use this for remote as well and users could simply pass flyte:// or s3:// or file://
        async with internal_ctx().new_raw_data_path(
            raw_data_path=RawDataPath.from_local_folder(local_folder=self._raw_data_path)
        ):
            return await self._run_local(task, *args, **kwargs)


def with_runcontext(
    mode: Mode | None = None,
    *,
    name: Optional[str] = None,
    service_account: Optional[str] = None,
    version: Optional[str] = None,
    copy_style: CopyFiles = "loaded_modules",
    dry_run: bool = False,
    copy_bundle_to: pathlib.Path | None = None,
    interactive_mode: bool | None = None,
    raw_data_path: str | None = None,
    run_base_dir: str | None = None,
) -> _Runner:
    """
    Launch a new run with the given parameters as the context.

    Example:
    ```python
    import flyte
    env = flyte.TaskEnvironment("example")

    @env.task
    async def example_task(x: int, y: str) -> str:
        return f"{x} {y}"

    if __name__ == "__main__":
        flyte.with_runcontext(name="example_run_id").run(example_task, 1, y="hello")
    ```

    :param mode: Optional The mode to use for the run, if not provided, it will be computed from flyte.init
    :param version: Optional The version to use for the run, if not provided, it will be computed from the code bundle
    :param name: Optional The name to use for the run
    :param service_account: Optional The service account to use for the run context
    :param copy_style: Optional The copy style to use for the run context
    :param dry_run: Optional If true, the run will not be executed, but the bundle will be created
    :param copy_bundle_to: When dry_run is True, the bundle will be copied to this location if specified
    :param interactive_mode: Optional, can be forced to True or False.
         If not provided, it will be set based on the current environment. For example Jupyter notebooks are considered
         interactive mode, while scripts are not. This is used to determine how the code bundle is created.
    :param raw_data_path: Use this path to store the raw data for the run. Currently only supported for local runs,
      and can be used to store raw data in specific locations. TODO coming soon for remote runs as well.
    :return: runner
    """
    if mode == "hybrid" and not name and not run_base_dir:
        raise ValueError("Run name and run base dir are required for hybrid mode")
    return _Runner(
        force_mode=mode,
        name=name,
        service_account=service_account,
        version=version,
        copy_style=copy_style,
        dry_run=dry_run,
        copy_bundle_to=copy_bundle_to,
        interactive_mode=interactive_mode,
        raw_data_path=raw_data_path,
        run_base_dir=run_base_dir,
    )


@syncer.wrap
async def run(task: TaskTemplate[P, R], *args: P.args, **kwargs: P.kwargs) -> Union[R, Run]:
    """
    Run a task with the given parameters
    :param task: task to run
    :param args: args to pass to the task
    :param kwargs: kwargs to pass to the task
    :return: Run | Result of the task
    """
    # using syncer causes problems
    return await _Runner().run.aio(task, *args, **kwargs)  # type: ignore
