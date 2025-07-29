"""
Flyte SDK for authoring Compound AI applications, services and workflows.

## Environments

TaskEnvironment class to define a new environment for a set of tasks.

Example usage:

```python
env = flyte.TaskEnvironment(name="my_env", image="my_image", resources=Resources(cpu="1", memory="1Gi"))

@env.task
async def my_task():
    pass
```
"""

__all__ = [
    "GPU",
    "TPU",
    "Cache",
    "CachePolicy",
    "CacheRequest",
    "Device",
    "Environment",
    "Image",
    "Resources",
    "RetryStrategy",
    "ReusePolicy",
    "Secret",
    "SecretRequest",
    "TaskEnvironment",
    "Timeout",
    "TimeoutType",
    "__version__",
    "ctx",
    "deploy",
    "group",
    "init",
    "run",
    "trace",
    "with_runcontext",
]

from ._cache import Cache, CachePolicy, CacheRequest
from ._context import ctx
from ._deploy import deploy
from ._environment import Environment
from ._group import group
from ._image import Image
from ._initialize import init
from ._resources import GPU, TPU, Device, Resources
from ._retry import RetryStrategy
from ._reusable_environment import ReusePolicy
from ._run import run, with_runcontext
from ._secret import Secret, SecretRequest
from ._task_environment import TaskEnvironment
from ._timeout import Timeout, TimeoutType
from ._trace import trace
from ._version import __version__
