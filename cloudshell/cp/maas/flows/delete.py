import time
from datetime import datetime, timedelta

from maas.client.enum import NodeStatus
from maas.client.viscera.machines import Machine


class MaasDeleteFlow:
    def __init__(self, resource_config, maas_client, logger):
        self._resource_config = resource_config
        self._maas_client = maas_client
        self._logger = logger

    def delete_instance(self, deployed_app):
        wait_time = 5
        timeout = 30 * 60
        timeout_time = datetime.now() + timedelta(seconds=timeout)

        while datetime.now() <= timeout_time:
            machine = self._maas_client.get_machine(deployed_app.vmdetails.uid)
            self._logger.info(f"Machine: {repr(machine)} Status: {repr(machine.status)}")
            if machine.status == NodeStatus.READY:
                break
            elif machine.status == NodeStatus.DEPLOYED:
                machine.release(comment=f"Releasing {machine.fqdn}")

            time.sleep(wait_time)
