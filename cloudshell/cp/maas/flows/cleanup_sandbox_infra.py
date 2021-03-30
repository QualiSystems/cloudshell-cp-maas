from http import HTTPStatus

from cloudshell.cp.core.flows.cleanup_sandbox_infra import (
    AbstractCleanupSandboxInfraFlow,
)
from maas.client.bones import CallError


class MaasCleanupSandboxInfraFlow(AbstractCleanupSandboxInfraFlow):
    def __init__(self, resource_config, reservation_info, maas_client, logger):
        super().__init__(logger=logger)
        self._resource_config = resource_config
        self._reservation_info = reservation_info
        self._maas_client = maas_client

    # todo: check if we need this code
    def _delete_fabric(self, name):
        try:
            fabric = self._maas_client.fabrics.get(name)
        except CallError as e:
            if e.status == HTTPStatus.NOT_FOUND:
                return
            raise

        fabric.delete()

    # todo: check if we need this code
    def _delete_subnet(self, name):
        try:
            subnet = self._maas_client.subnets.get(name)
        except CallError as e:
            if e.status == HTTPStatus.NOT_FOUND:
                return
            raise

        subnet.delete()

    def cleanup_sandbox_infra(self, request_actions):
        # self._delete_subnet(name=self.DEFAULT_SUBNET_NAME)  # noqa: E800
        # self._delete_fabric(name=self.DEFAULT_FABRIC_NAME)  # noqa: E800
        pass
