import os

from cloudshell.cp.core.flows.prepare_sandbox_infra import (
    AbstractPrepareSandboxInfraFlow,
)
from cloudshell.cp.core.utils import generate_ssh_key_pair

from cloudshell.cp.maas.api.sandbox_api import CSAPIHelper


class MaasPrepareSandboxInfraFlow(AbstractPrepareSandboxInfraFlow):
    SSH_PRIVATE_KEY_NAME = "maas_rsa_priv_key"
    SSH_PRIVATE_KEY_ID = "maas_rsa_priv_key_id"

    def __init__(self, resource_config, reservation_info, cancellation_manager, maas_client, api, logger):
        super().__init__(logger)
        self._resource_config = resource_config
        self._reservation_info = reservation_info
        self._cancellation_manager = cancellation_manager
        self._api = api
        self._api_helper = CSAPIHelper(api, reservation_info.reservation_id)
        self._maas_client = maas_client

    @property
    def private_ssh_key_path(self):
        if self._reservation_info.reservation_id:
            return os.path.join(self._resource_config.ssh_keypair_path, self._reservation_info.reservation_id
        )

    @property
    def public_ssh_key_path(self):
        return os.path.join(
            self._resource_config.ssh_keypair_path, self.SSH_PUBLIC_KEY_FILE_NAME
        )

    def _save_ssh_key_pair(self, private_key: str):
        with open(self.private_ssh_key_path, "w+") as f:
            f.write(private_key)

    def _get_ssh_public_key(self):
        with open(self.public_ssh_key_path, "r") as f:
            return f.read()

    def _get_ssh_private_key(self):
        with open(self.private_ssh_key_path, "r") as f:
            return f.read()

    def prepare_subnets(self, request_actions):

        return {}

    def prepare_cloud_infra(self, request_actions):
        pass

    # ToDo check why keys are not created on maas
    def create_ssh_keys(self, request_actions):
        private_key = self._api_helper.get_sandbox_data_item(self.SSH_PRIVATE_KEY_NAME)
        if not private_key:
            private_key, public_key = generate_ssh_key_pair()
            self._maas_client.create_ssh_key(public_key)
            self._api_helper.add_sandbox_data_item(self.SSH_PRIVATE_KEY_NAME, private_key)
            self._api_helper.add_sandbox_data_item(self.SSH_PRIVATE_KEY_ID, private_key)

        return private_key
