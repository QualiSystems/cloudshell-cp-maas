from http import HTTPStatus

from cloudshell.cp.core.flows.cleanup_sandbox_infra import (
    AbstractCleanupSandboxInfraFlow,
)

from cloudshell.cp.maas.models.cs_maas_ssh_key import CSSSHKey
from maas.client.bones import CallError

from cloudshell.cp.maas.api.sandbox_api import CSAPIHelper
from cloudshell.cp.maas.flows.prepare_sandbox_infra import MaasPrepareSandboxInfraFlow


class MaasCleanupSandboxInfraFlow(AbstractCleanupSandboxInfraFlow):
    def __init__(self, resource_config, reservation_info, maas_client, api, logger):
        super().__init__(logger=logger)
        self._resource_config = resource_config
        self._reservation_info = reservation_info
        self._api_helper = CSAPIHelper(api, reservation_info.reservation_id)
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
        id = self._api_helper.get_sandbox_data_item(MaasPrepareSandboxInfraFlow.SSH_PRIVATE_KEY_ID)  # noqa: E800
        key = self._maas_client.get_ssh_key(id)
        CSSSHKey(key).delete()
        # self._delete_subnet(name=self.DEFAULT_SUBNET_NAME)  # noqa: E800
        # self._delete_fabric(name=self.DEFAULT_FABRIC_NAME)  # noqa: E800
