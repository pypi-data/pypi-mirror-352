from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

import rich.repr

from flyte._secret import SecretRequest

from ._image import Image
from ._resources import Resources

if TYPE_CHECKING:
    from kubernetes.client import V1PodTemplate


@rich.repr.auto
@dataclass(init=True, repr=True)
class Environment:
    """
    :param name: Name of the environment
    :param image: Docker image to use for the environment. If set to "auto", will use the default image.
    :param resources: Resources to allocate for the environment.
    :param env: Environment variables to set for the environment.
    :param secrets: Secrets to inject into the environment.
    :param env_dep_hints: Environment dependencies to hint, so when you deploy the environment, the dependencies are
        also deployed. This is useful when you have a set of environments that depend on each other.
    """

    name: str
    env_dep_hints: List[Environment] = field(default_factory=list)
    pod_template: Optional[Union[str, "V1PodTemplate"]] = None
    description: Optional[str] = None
    secrets: Optional[SecretRequest] = None
    env: Optional[Dict[str, str]] = None
    resources: Optional[Resources] = None
    image: Union[str, Image, Literal["auto"]] = "auto"

    def add_dependency(self, *env: Environment):
        """
        Add a dependency to the environment.
        """
        self.env_dep_hints.extend(env)
