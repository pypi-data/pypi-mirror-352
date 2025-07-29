from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncGenerator, Iterator, Literal, Union

import rich.repr

from flyte._api_commons import syncer
from flyte._initialize import get_client, get_common_config, requires_client
from flyte._protos.secret import definition_pb2, payload_pb2

SecretTypes = Literal["regular", "image_pull"]


@dataclass
class Secret:
    pb2: definition_pb2.Secret

    @classmethod
    @requires_client
    @syncer.wrap
    async def create(cls, name: str, value: Union[str, bytes], type: SecretTypes = "regular"):
        cfg = get_common_config()
        secret_type = (
            definition_pb2.SecretType.SECRET_TYPE_GENERIC
            if type == "regular"
            else definition_pb2.SecretType.SECRET_TYPE_IMAGE_PULL_SECRET
        )

        if isinstance(value, str):
            secret = definition_pb2.SecretSpec(
                type=secret_type,
                string_value=value,
            )
        else:
            secret = definition_pb2.SecretSpec(
                type=secret_type,
                binary_value=value,
            )
        await get_client().secrets_service.CreateSecret(  # type: ignore
            request=payload_pb2.CreateSecretRequest(
                id=definition_pb2.SecretIdentifier(
                    organization=cfg.org,
                    project=cfg.project,
                    domain=cfg.domain,
                    name=name,
                ),
                secret_spec=secret,
            ),
        )

    @classmethod
    @requires_client
    @syncer.wrap
    async def get(cls, name: str) -> Secret:
        cfg = get_common_config()
        resp = await get_client().secrets_service.GetSecret(
            request=payload_pb2.GetSecretRequest(
                id=definition_pb2.SecretIdentifier(
                    organization=cfg.org,
                    project=cfg.project,
                    domain=cfg.domain,
                    name=name,
                )
            )
        )
        return Secret(pb2=resp.secret)

    @classmethod
    @requires_client
    @syncer.wrap
    async def listall(cls, limit: int = 100) -> Union[Iterator[Secret], AsyncGenerator[Secret, None]]:
        cfg = get_common_config()
        token = None
        while True:
            resp = await get_client().secrets_service.ListSecrets(  # type: ignore
                request=payload_pb2.ListSecretsRequest(
                    organization=cfg.org,
                    project=cfg.project,
                    domain=cfg.domain,
                    token=token,
                    limit=limit,
                ),
            )
            token = resp.token
            for r in resp.secrets:
                yield cls(r)
            if not token:
                break

    @classmethod
    @requires_client
    @syncer.wrap
    async def delete(cls, name):
        cfg = get_common_config()
        await get_client().secrets_service.DeleteSecret(  # type: ignore
            request=payload_pb2.DeleteSecretRequest(
                id=definition_pb2.SecretIdentifier(
                    organization=cfg.org,
                    project=cfg.project,
                    domain=cfg.domain,
                    name=name,
                )
            )
        )

    @property
    def name(self) -> str:
        return self.pb2.id.name

    @property
    def type(self) -> str:
        if self.pb2.secret_metadata.type == definition_pb2.SecretType.SECRET_TYPE_GENERIC:
            return "regular"
        elif self.pb2.secret_metadata.type == definition_pb2.SecretType.SECRET_TYPE_IMAGE_PULL_SECRET:
            return "image_pull"
        raise ValueError("unknown type")

    def __rich_repr__(self) -> rich.repr.Result:
        yield "project", self.pb2.id.project or "-"
        yield "domain", self.pb2.id.domain or "-"
        yield "name", self.name
        yield "type", self.type
        yield "created_time", self.pb2.secret_metadata.created_time.ToDatetime().isoformat()
        yield "status", definition_pb2.OverallStatus.Name(self.pb2.secret_metadata.secret_status.overall_status)
        yield (
            "cluster_status",
            {
                s.cluster.name: definition_pb2.SecretPresenceStatus.Name(s.presence_status)
                for s in self.pb2.secret_metadata.secret_status.cluster_status
            },
        )
