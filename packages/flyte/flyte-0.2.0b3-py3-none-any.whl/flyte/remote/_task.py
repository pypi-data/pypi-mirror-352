from __future__ import annotations

import functools
from dataclasses import dataclass
from threading import Lock
from typing import Any, Callable, Coroutine, Dict, Literal, Optional, Union

import rich.repr

import flyte
import flyte.errors
from flyte._api_commons import syncer
from flyte._context import internal_ctx
from flyte._initialize import get_client, get_common_config
from flyte._protos.workflow import task_definition_pb2, task_service_pb2
from flyte.models import NativeInterface


class LazyEntity:
    """
    Fetches the entity when the entity is called or when the entity is retrieved.
    The entity is derived from RemoteEntity so that it behaves exactly like the mimicked entity.
    """

    def __init__(self, name: str, getter: Callable[..., Coroutine[Any, Any, Task]], *args, **kwargs):
        self._task: Optional[Task] = None
        self._getter = getter
        self._name = name
        self._mutex = Lock()

    @property
    def name(self) -> str:
        return self._name

    @syncer.wrap
    async def fetch(self) -> Task:
        """
        Forwards all other attributes to task, causing the task to be fetched!
        """
        with self._mutex:
            if self._task is None:
                self._task = await self._getter()
            if self._task is None:
                raise RuntimeError(f"Error downloading the task {self._name}, (check original exception...)")
            return self._task

    async def __call__(self, *args, **kwargs):
        """
        Forwards the call to the underlying task. The entity will be fetched if not already present
        """
        tk = await self.fetch.aio(self)
        return await tk(*args, **kwargs)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"Future for task with name {self._name}"


AutoVersioning = Literal["latest", "current"]


@dataclass
class Task:
    pb2: task_definition_pb2.TaskDetails

    @classmethod
    def get(cls, name: str, version: str | None = None, auto_version: AutoVersioning | None = None) -> LazyEntity:
        """
        Get a task by its ID or name. If both are provided, the ID will take precedence.

        Either version or auto_version are required parameters.

        :param uri: The URI of the task. If provided, do not provide the rest of the parameters.
        :param name: The name of the task.
        :param version: The version of the task.
        :param auto_version: If set to "latest", the latest-by-time ordered from now, version of the task will be used.
         If set to "current", the version will be derived from the callee tasks context. This is useful if you are
         deploying all environments with the same version. If auto_version is current, you can only access the task from
         within a task context.
        """

        if version is None and auto_version is None:
            raise ValueError("Either version or auto_version must be provided.")

        if version is None and auto_version not in ["latest", "current"]:
            raise ValueError("auto_version must be either 'latest' or 'current'.")

        async def deferred_get(_version: str | None, _auto_version: AutoVersioning | None) -> Task:
            if _version is None:
                if _auto_version == "latest":
                    raise NotImplementedError("auto_version=latest is not yet implemented.")
                elif _auto_version == "current":
                    ctx = flyte.ctx()
                    if ctx is None:
                        raise ValueError("auto_version=current can only be used within a task context.")
                    _version = ctx.version
            cfg = get_common_config()
            task_id = task_definition_pb2.TaskIdentifier(
                org=cfg.org,
                project=cfg.project,
                domain=cfg.domain,
                name=name,
                version=_version,
            )
            resp = await get_client().task_service.GetTaskDetails(
                task_service_pb2.GetTaskDetailsRequest(
                    task_id=task_id,
                )
            )
            return cls(resp.details)

        return LazyEntity(
            name=name, getter=functools.partial(deferred_get, _version=version, _auto_version=auto_version)
        )

    @property
    def name(self) -> str:
        """
        The name of the task.
        """
        return self.pb2.task_id.name

    @property
    def version(self) -> str:
        """
        The version of the task.
        """
        return self.pb2.task_id.version

    @property
    def task_type(self) -> str:
        """
        The type of the task.
        """
        return self.pb2.spec.task_template.type

    @functools.cached_property
    def interface(self) -> NativeInterface:
        """
        The interface of the task.
        """
        import flyte.types as types

        return types.guess_interface(self.pb2.spec.task_template.interface)

    @property
    def cache(self) -> flyte.Cache:
        """
        The cache policy of the task.
        """
        return flyte.Cache(
            behavior="enabled" if self.pb2.spec.task_template.metadata.discoverable else "disable",
            version_override=self.pb2.spec.task_template.metadata.discovery_version,
            serialize=self.pb2.spec.task_template.metadata.cache_serializable,
            ignored_inputs=tuple(self.pb2.spec.task_template.metadata.cache_ignore_input_vars),
        )

    @property
    def secrets(self):
        """
        The secrets of the task.
        """
        return [s.key for s in self.pb2.spec.task_template.security_context.secrets]

    @property
    def resources(self):
        """
        The resources of the task.
        """
        if self.pb2.spec.task_template.container is None:
            return ()
        return (
            self.pb2.spec.task_template.container.resources.requests,
            self.pb2.spec.task_template.container.resources.limits,
        )

    async def __call__(self, *args, **kwargs):
        """
        Forwards the call to the underlying task. The entity will be fetched if not already present
        """
        ctx = internal_ctx()
        if ctx.is_task_context():
            # If we are in a task context, that implies we are executing a Run.
            # In this scenario, we should submit the task to the controller.
            # We will also check if we are not initialized, It is not expected to be not initialized
            from flyte._internal.controllers import get_controller

            controller = get_controller()
            if controller:
                return await controller.submit_task_ref(self.pb2, *args, **kwargs)
        raise flyte.errors

    def override(
        self,
        *,
        local: Optional[bool] = None,
        ref: Optional[bool] = None,
        resources: Optional[flyte.Resources] = None,
        cache: flyte.CacheRequest = "auto",
        retries: Union[int, flyte.RetryStrategy] = 0,
        timeout: Optional[flyte.TimeoutType] = None,
        reusable: Union[flyte.ReusePolicy, Literal["auto"], None] = None,
        env: Optional[Dict[str, str]] = None,
        secrets: Optional[flyte.SecretRequest] = None,
        **kwargs: Any,
    ) -> Task:
        raise NotImplementedError

    def __rich_repr__(self) -> rich.repr.Result:
        """
        Rich representation of the task.
        """
        yield "project", self.pb2.task_id.project
        yield "domain", self.pb2.task_id.domain
        yield "name", self.name
        yield "version", self.version
        yield "task_type", self.task_type
        yield "cache", self.cache
        yield "interface", self.name + str(self.interface)
        yield "secrets", self.secrets
        yield "resources", self.resources


if __name__ == "__main__":
    tk = Task.get(name="example_task")
