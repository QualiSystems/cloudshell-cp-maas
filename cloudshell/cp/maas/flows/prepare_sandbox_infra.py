import os

from cloudshell.cp.core.flows.prepare_sandbox_infra import (
    AbstractPrepareSandboxInfraFlow,
)
from cloudshell.cp.core.utils import generate_ssh_key_pair


class MaasPrepareSandboxInfraFlow(AbstractPrepareSandboxInfraFlow):
    SSH_PRIVATE_KEY_FILE_NAME = "maas_id_rsa.ppk"
    SSH_PUBLIC_KEY_FILE_NAME = "maas_id_rsa.ppubk"

    def __init__(
        self,
        resource_config,
        reservation_info,
        cancellation_manager,
        maas_client,
        logger,
    ):
        self._resource_config = resource_config
        self._reservation_info = reservation_info
        self._cancellation_manager = cancellation_manager
        self._maas_client = maas_client
        self._logger = logger

    @property
    def private_ssh_key_path(self):
        return os.path.join(
            self._resource_config.ssh_keypair_path, self.SSH_PRIVATE_KEY_FILE_NAME
        )

    @property
    def public_shh_key_path(self):
        return os.path.join(
            self._resource_config.ssh_keypair_path, self.SSH_PUBLIC_KEY_FILE_NAME
        )

    def _save_ssh_key_pair(self, private_key: str, public_key: str):
        with open(self.private_ssh_key_path, "w+") as f:
            f.write(private_key)

        with open(self.public_shh_key_path, "w+") as f:
            f.write(public_key)

    def _ssh_keys_exists(self):
        return all(
            [
                os.path.exists(self.private_ssh_key_path),
                os.path.exists(self.public_shh_key_path),
            ]
        )

    def _get_ssh_public_key(self):
        with open(self.public_shh_key_path, "r") as f:
            return f.read()

    def prepare_subnets(self):
        pass

    def create_ssh_keys(self):
        if self._ssh_keys_exists():
            public_key = self._get_ssh_public_key()
        else:
            private_key, public_key = generate_ssh_key_pair()
            self._save_ssh_key_pair(private_key=private_key, public_key=public_key)
            # send to MAAS only public key
            self._maas_client.create_ssh_key(public_key)

        return public_key
