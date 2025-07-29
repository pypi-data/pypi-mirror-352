from __future__ import annotations

import functools
import threading
import typing
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Literal, Optional, TypeVar

from flyte.errors import InitializationError

from ._api_commons import syncer
from ._logging import initialize_logger
from ._tools import ipython_check

if TYPE_CHECKING:
    from flyte.config import Config
    from flyte.remote._client.auth import AuthType, ClientConfig
    from flyte.remote._client.controlplane import ClientSet
    from flyte.storage import Storage

Mode = Literal["local", "remote"]


@dataclass(init=True, repr=True, eq=True, frozen=True, kw_only=True)
class CommonInit:
    """
    Common initialization configuration for Flyte.
    """

    root_dir: Path
    org: str | None = None
    project: str | None = None
    domain: str | None = None


@dataclass(init=True, kw_only=True, repr=True, eq=True, frozen=True)
class _InitConfig(CommonInit):
    client: Optional[ClientSet] = None
    storage: Optional[Storage] = None

    def replace(self, **kwargs) -> _InitConfig:
        return replace(self, **kwargs)


# Global singleton to store initialization configuration
_init_config: _InitConfig | None = None
_init_lock = threading.RLock()  # Reentrant lock for thread safety


async def _initialize_client(
    api_key: str | None = None,
    auth_type: AuthType = "Pkce",
    endpoint: str | None = None,
    client_config: ClientConfig | None = None,
    headless: bool = False,
    insecure: bool = False,
    insecure_skip_verify: bool = False,
    ca_cert_file_path: str | None = None,
    command: List[str] | None = None,
    proxy_command: List[str] | None = None,
    client_id: str | None = None,
    client_credentials_secret: str | None = None,
    rpc_retries: int = 3,
    http_proxy_url: str | None = None,
) -> ClientSet:
    """
    Initialize the client based on the execution mode.
    :return: The initialized client
    """
    from flyte.remote._client.controlplane import ClientSet

    if endpoint:
        return await ClientSet.for_endpoint(
            endpoint,
            insecure=insecure,
            insecure_skip_verify=insecure_skip_verify,
            auth_type=auth_type,
            headless=headless,
            ca_cert_file_path=ca_cert_file_path,
            command=command,
            proxy_command=proxy_command,
            client_id=client_id,
            client_credentials_secret=client_credentials_secret,
            client_config=client_config,
            rpc_retries=rpc_retries,
            http_proxy_url=http_proxy_url,
        )
    elif api_key:
        return await ClientSet.for_api_key(
            api_key,
            insecure=insecure,
            insecure_skip_verify=insecure_skip_verify,
            auth_type=auth_type,
            headless=headless,
            ca_cert_file_path=ca_cert_file_path,
            command=command,
            proxy_command=proxy_command,
            client_id=client_id,
            client_credentials_secret=client_credentials_secret,
            client_config=client_config,
            rpc_retries=rpc_retries,
            http_proxy_url=http_proxy_url,
        )

    raise InitializationError(
        "MissingEndpointOrApiKeyError", "user", "Either endpoint or api_key must be provided to initialize the client."
    )


@syncer.wrap
async def init(
    org: str | None = None,
    project: str | None = None,
    domain: str | None = None,
    root_dir: Path | None = None,
    log_level: int | None = None,
    endpoint: str | None = None,
    headless: bool = False,
    insecure: bool = False,
    insecure_skip_verify: bool = False,
    ca_cert_file_path: str | None = None,
    auth_type: AuthType = "Pkce",
    command: List[str] | None = None,
    proxy_command: List[str] | None = None,
    api_key: str | None = None,
    client_id: str | None = None,
    client_credentials_secret: str | None = None,
    auth_client_config: ClientConfig | None = None,
    rpc_retries: int = 3,
    http_proxy_url: str | None = None,
    storage: Storage | None = None,
    config: Config | None = None,
) -> None:
    """
    Initialize the Flyte system with the given configuration. This method should be called before any other Flyte
    remote API methods are called. Thread-safe implementation.

    :param project: Optional project name (not used in this implementation)
    :param domain: Optional domain name (not used in this implementation)
    :param root_dir: Optional root directory from which to determine how to load files, and find paths to files.
      defaults to the editable install directory if the cwd is in a Python editable install, else just the cwd.
    :param log_level: Optional logging level for the logger, default is set using the default initialization policies
    :param api_key: Optional API key for authentication
    :param endpoint: Optional API endpoint URL
    :param headless: Optional Whether to run in headless mode
    :param mode: Optional execution model (local, remote). Default is local. When local is used,
           the execution will be done locally. When remote is used, the execution will be sent to a remote server,
           In the remote case, the endpoint or api_key must be set.
    :param insecure_skip_verify: Whether to skip SSL certificate verification
    :param auth_client_config: Optional client configuration for authentication
    :param auth_type: The authentication type to use (Pkce, ClientSecret, ExternalCommand, DeviceFlow)
    :param command: This command is executed to return a token using an external process
    :param proxy_command: This command is executed to return a token for proxy authorization using an external process
    :param client_id: This is the public identifier for the app which handles authorization for a Flyte deployment.
      More details here: https://www.oauth.com/oauth2-servers/client-registration/client-id-secret/.
    :param client_credentials_secret: Used for service auth, which is automatically called during pyflyte. This will
      allow the Flyte engine to read the password directly from the environment variable. Note that this is
      less secure! Please only use this if mounting the secret as a file is impossible
    :param ca_cert_file_path: [optional] str Root Cert to be loaded and used to verify admin
    :param http_proxy_url: [optional] HTTP Proxy to be used for OAuth requests
    :param rpc_retries: [optional] int Number of times to retry the platform calls
    :param audience: oauth2 audience for the token request. This is used to validate the token
    :param insecure: insecure flag for the client
    :param storage: Optional blob store (S3, GCS, Azure) configuration if needed to access (i.e. using Minio)
    :param org: Optional organization override for the client. Should be set by auth instead.
    :param config: Optional config to override the init parameters

    :return: None
    """
    from flyte._utils import get_cwd_editable_install

    interactive_mode = ipython_check()

    initialize_logger(enable_rich=interactive_mode)
    if log_level:
        initialize_logger(log_level=log_level, enable_rich=interactive_mode)

    global _init_config  # noqa: PLW0603

    with _init_lock:
        if config is None:
            import flyte.config as _f_cfg

            config = _f_cfg.Config()
        platform_cfg = config.platform
        task_cfg = config.task
        client = None
        if endpoint or platform_cfg.endpoint or api_key:
            client = await _initialize_client(
                api_key=api_key,
                auth_type=auth_type or platform_cfg.auth_mode,
                endpoint=endpoint or platform_cfg.endpoint,
                headless=headless,
                insecure=insecure or platform_cfg.insecure,
                insecure_skip_verify=insecure_skip_verify or platform_cfg.insecure_skip_verify,
                ca_cert_file_path=ca_cert_file_path or platform_cfg.ca_cert_file_path,
                command=command or platform_cfg.command,
                proxy_command=proxy_command or platform_cfg.proxy_command,
                client_id=client_id or platform_cfg.client_id,
                client_credentials_secret=client_credentials_secret or platform_cfg.client_credentials_secret,
                client_config=auth_client_config,
                rpc_retries=rpc_retries or platform_cfg.rpc_retries,
                http_proxy_url=http_proxy_url or platform_cfg.http_proxy_url,
            )

        root_dir = root_dir or get_cwd_editable_install() or Path.cwd()
        _init_config = _InitConfig(
            root_dir=root_dir,
            project=project or task_cfg.project,
            domain=domain or task_cfg.domain,
            client=client,
            storage=storage,
            org=org or task_cfg.org,
        )


def _get_init_config() -> Optional[_InitConfig]:
    """
    Get the current initialization configuration. Thread-safe implementation.

    :return: The current InitData if initialized, None otherwise
    """
    with _init_lock:
        return _init_config


def get_common_config() -> CommonInit:
    """
    Get the current initialization configuration. Thread-safe implementation.

    :return: The current InitData if initialized, None otherwise
    """
    cfg = _get_init_config()
    if cfg is None:
        raise InitializationError(
            "StorageNotInitializedError",
            "user",
            "Configuration has not been initialized. Call flyte.init() with a valid endpoint or",
            " api-key before using this function.",
        )
    return cfg


def get_storage() -> Storage | None:
    """
    Get the current storage configuration. Thread-safe implementation.

    :return: The current storage configuration
    """
    cfg = _get_init_config()
    if cfg is None:
        raise InitializationError(
            "StorageNotInitializedError",
            "user",
            "Configuration has not been initialized. Call flyte.init() with a valid endpoint or",
            " api-key before using this function.",
        )
    return cfg.storage


def get_client() -> ClientSet:
    """
    Get the current client. Thread-safe implementation.

    :return: The current client
    """
    cfg = _get_init_config()
    if cfg is None or cfg.client is None:
        raise InitializationError(
            "ClientNotInitializedError",
            "user",
            "Client has not been initialized. Call flyte.init() with a valid endpoint or"
            " api-key before using this function.",
        )
    return cfg.client


def is_initialized() -> bool:
    """
    Check if the system has been initialized.

    :return: True if initialized, False otherwise
    """
    return _get_init_config() is not None


def initialize_in_cluster() -> None:
    """
    Initialize the system for in-cluster execution. This is a placeholder function and does not perform any actions.

    :return: None
    """
    init()


# Define a generic type variable for the decorated function
T = TypeVar("T", bound=Callable)


def requires_client(func: T) -> T:
    """
    Decorator that checks if the client has been initialized before executing the function.
    Raises InitializationError if the client is not initialized.

    :param func: Function to decorate
    :return: Decorated function that checks for initialization
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        init_config = _get_init_config()
        if init_config is None or init_config.client is None:
            raise InitializationError(
                "ClientNotInitializedError",
                "user",
                f"Function '{func.__name__}' requires client to be initialized. "
                f"Call flyte.init() with a valid endpoint or api-key before using this function.",
            )
        return func(*args, **kwargs)

    return typing.cast(T, wrapper)


def requires_storage(func: T) -> T:
    """
    Decorator that checks if the storage has been initialized before executing the function.
    Raises InitializationError if the storage is not initialized.

    :param func: Function to decorate
    :return: Decorated function that checks for initialization
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if _get_init_config() is None or _get_init_config().storage is None:
            raise InitializationError(
                "StorageNotInitializedError",
                "user",
                f"Function '{func.__name__}' requires storage to be initialized. "
                f"Call flyte.init() with a valid storage configuration before using this function.",
            )
        return func(*args, **kwargs)

    return typing.cast(T, wrapper)


def requires_upload_location(func: T) -> T:
    """
    Decorator that checks if the storage has been initialized before executing the function.
    Raises InitializationError if the storage is not initialized.

    :param func: Function to decorate
    :return: Decorated function that checks for initialization
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        from ._context import internal_ctx

        ctx = internal_ctx()
        if not ctx.raw_data:
            raise InitializationError(
                "No upload path configured",
                "user",
                f"Function '{func.__name__}' requires client to be initialized. "
                f"Call flyte.init() with storage configuration before using this function.",
            )
        return func(*args, **kwargs)

    return typing.cast(T, wrapper)


def requires_initialization(func: T) -> T:
    """
    Decorator that checks if the system has been initialized before executing the function.
    Raises InitializationError if the system is not initialized.

    :param func: Function to decorate
    :return: Decorated function that checks for initialization
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        if not is_initialized():
            raise InitializationError(
                "NotInitConfiguredError",
                "user",
                f"Function '{func.__name__}' requires initialization. Call flyte.init() before using this function.",
            )
        return func(*args, **kwargs)

    return typing.cast(T, wrapper)


async def _init_for_testing(
    project: str | None = None,
    domain: str | None = None,
    root_dir: Path | None = None,
    log_level: int | None = None,
    client: ClientSet | None = None,
):
    from flyte._utils.helpers import get_cwd_editable_install

    global _init_config  # noqa: PLW0603

    if log_level:
        initialize_logger(log_level=log_level)

    with _init_lock:
        root_dir = root_dir or get_cwd_editable_install() or Path.cwd()
        _init_config = _InitConfig(
            root_dir=root_dir,
            project=project,
            domain=domain,
            client=client,
        )


def replace_client(client):
    global _init_config  # noqa: PLW0603

    with _init_lock:
        _init_config = _init_config.replace(client=client)
