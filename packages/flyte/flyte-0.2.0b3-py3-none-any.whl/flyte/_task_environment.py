from __future__ import annotations

import asyncio
import weakref
from dataclasses import dataclass, field, replace
from datetime import timedelta
from functools import wraps
from typing import TYPE_CHECKING, Awaitable, Callable, Dict, List, Literal, Optional, ParamSpec, TypeVar, Union, cast

import rich.repr

from ._cache import CacheRequest
from ._doc import Documentation
from ._environment import Environment
from ._image import Image
from ._resources import Resources
from ._retry import RetryStrategy
from ._reusable_environment import ReusePolicy
from ._secret import SecretRequest
from ._task import AsyncFunctionTaskTemplate, TaskTemplate
from .models import NativeInterface

if TYPE_CHECKING:
    from kubernetes.client import V1PodTemplate

P = ParamSpec("P")  # capture the function's parameters
R = TypeVar("R")  # return type


@rich.repr.auto
@dataclass(init=True, repr=True)
class TaskEnvironment(Environment):
    """
    Environment class to define a new environment for a set of tasks.

    Example usage:
    ```python
    env = flyte.TaskEnvironment(name="my_env", image="my_image", resources=Resources(cpu="1", memory="1Gi"))

    @env.task
    async def my_task():
        pass
    ```

    :param name: Name of the environment
    :param image: Docker image to use for the environment. If set to "auto", will use the default image.
    :param resources: Resources to allocate for the environment.
    :param env: Environment variables to set for the environment.
    :param secrets: Secrets to inject into the environment.
    :param env_dep_hints: Environment dependencies to hint, so when you deploy the environment, the dependencies are
        also deployed. This is useful when you have a set of environments that depend on each other.
    :param cache: Cache policy for the environment.
    :param reusable: Reuse policy for the environment, if set, a python process may be reused for multiple tasks.
    """

    cache: Union[CacheRequest] = "auto"
    reusable: Union[ReusePolicy, Literal["auto"], None] = None
    # TODO Shall we make this union of string or env? This way we can lookup the env by module/file:name
    # TODO also we could add list of files that are used by this environment

    _tasks: Dict[str, TaskTemplate] = field(default_factory=dict, init=False)

    def clone_with(
        self,
        name: str,
        image: Optional[Union[str, Image, Literal["auto"]]] = None,
        resources: Optional[Resources] = None,
        cache: Union[CacheRequest, None] = None,
        env: Optional[Dict[str, str]] = None,
        reusable: Union[ReusePolicy, None] = None,
        secrets: Optional[SecretRequest] = None,
        env_dep_hints: Optional[List[Environment]] = None,
    ) -> TaskEnvironment:
        """
        Clone the environment with new settings.
        """
        if image is None:
            image = self.image
        else:
            image = "auto"
        return replace(
            self,
            cache=cache if cache else "auto",
            reusable=reusable,
            name=name,
            image=image,
            resources=resources,
            env=env,
            secrets=secrets,
            env_dep_hints=env_dep_hints if env_dep_hints else [],
        )

    def _task(
        self,
        _func=None,
        *,
        name: Optional[str] = None,
        cache: Union[CacheRequest] | None = None,
        retries: Union[int, RetryStrategy] = 0,
        timeout: Union[timedelta, int] = 0,
        docs: Optional[Documentation] = None,
        secrets: Optional[SecretRequest] = None,
        pod_template: Optional[Union[str, "V1PodTemplate"]] = None,
        report: bool = False,
    ) -> Union[AsyncFunctionTaskTemplate, Callable[P, R]]:
        """
        :param name: Optional The name of the task (defaults to the function name)
        :param cache: Optional The cache policy for the task, defaults to auto, which will cache the results of the
        task.
        :param retries: Optional The number of retries for the task, defaults to 0, which means no retries.
        :param docs: Optional The documentation for the task, if not provided the function docstring will be used.
        :param secrets: Optional The secrets that will be injected into the task at runtime.
        :param timeout: Optional The timeout for the task.
        :param pod_template: Optional The pod template for the task, if not provided the default pod template will be
        used.
        :param report: Optional Whether to generate the html report for the task, defaults to False.
        """
        if self.reusable is not None:
            if pod_template is not None:
                raise ValueError("Cannot set pod_template when environment is reusable.")

        def decorator(func: Callable[P, Awaitable[R]]) -> AsyncFunctionTaskTemplate[P, R]:
            task_name = name or func.__name__
            task_name = self.name + "." + task_name
            if len(task_name) > 30:
                # delete this if we can remove the restriction that task names must be <= 30 characters
                task_name = task_name[-30:]

            @wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return await func(*args, **kwargs)

            if not asyncio.iscoroutinefunction(func):
                raise TypeError(
                    f"Function {func.__name__} is not a coroutine function. Use @env.task decorator for async tasks."
                    f"You can simply mark your function as async def {func.__name__} to make it a coroutine function, "
                    f"it is ok to write sync code in async functions, but not the other way around."
                )
            tmpl = AsyncFunctionTaskTemplate(
                func=wrapper,
                name=task_name,
                image=self.image,
                resources=self.resources,
                cache=cache or self.cache,
                retries=retries,
                timeout=timeout,
                reusable=self.reusable,
                docs=docs,
                env=self.env,
                secrets=secrets or self.secrets,
                pod_template=pod_template or self.pod_template,
                parent_env=weakref.ref(self),
                interface=NativeInterface.from_callable(func),
                report=report,
            )
            self._tasks[task_name] = tmpl
            return tmpl

        if _func is None:
            return cast(AsyncFunctionTaskTemplate, decorator)
        return cast(AsyncFunctionTaskTemplate, decorator(_func))

    @property
    def task(self) -> Callable:
        """
        Decorator to create a new task with the environment settings.
        The task will be executed in its own container with the specified image, resources, and environment variables,
        unless reusePolicy is set, in which case the same container will be reused for all tasks with the same
        environment settings.

        :param name: Optional The name of the task (defaults to the function name)
        :param cache: Optional The cache policy for the task, defaults to auto, which will cache the results of the
         task.
        :param retries: Optional The number of retries for the task, defaults to 0, which means no retries.
        :param docs: Optional The documentation for the task, if not provided the function docstring will be used.
        :param secrets: Optional The secrets that will be injected into the task at runtime.
        :param timeout: Optional The timeout for the task.
        :param pod_template: Optional The pod template for the task, if not provided the default pod template will be
         used.
        :param report: Optional Whether to generate the html report for the task, defaults to False.

        :return: New Task instance or Task decorator
        """
        return self._task

    @property
    def tasks(self) -> Dict[str, TaskTemplate]:
        """
        Get all tasks defined in the environment.
        """
        return self._tasks

    def add_task(self, task: TaskTemplate) -> TaskTemplate:
        """
        Add a task to the environment.
        """
        if task.name in self._tasks:
            raise ValueError(f"Task {task.name} already exists in the environment. Task names should be unique.")
        self._tasks[task.name] = task
        return task
