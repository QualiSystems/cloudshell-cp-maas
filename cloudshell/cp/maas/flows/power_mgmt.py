import time
from datetime import datetime, timedelta

from maas.client.enum import PowerState


class MaasPowerManagementFlow:
    def __init__(self, resource_config, maas_client, logger):
        self._resource_config = resource_config
        self._maas_client = maas_client
        self._logger = logger

    def power_on(self, deployed_app):
        machine = self._maas_client.get_machine(deployed_app.vmdetails.uid)

        if machine.power_state == PowerState.ON:
            return

        try:
            self._logger.info(f"Powering On machine '{repr(machine)}'")
            machine.power_on(wait=False)
        except Exception:
            self._logger.warning("Error happened during Powering On", exc_info=True)
        finally:
            self._maas_client.api.machines.list()

        wait_time = 5
        timeout = 5 * 60
        timeout_time = datetime.now() + timedelta(seconds=timeout)

        while datetime.now() <= timeout_time:
            machine = self._maas_client.get_machine(deployed_app.vmdetails.uid)
            self._logger.info(f"Machine: {repr(machine)} power state: {repr(machine.power_state)}")

            if machine.power_state == PowerState.ON:
                break

            time.sleep(wait_time)

            if machine.power_state == PowerState.ERROR:
                raise Exception(f"Failed to power on machine. Machine power state: {repr(machine.power_state)}")

        if machine.power_state != PowerState.ON:
            raise Exception(f"Failed to power on machine. Machine power state: {repr(machine.power_state)}")

    def power_off(self, deployed_app):
        machine = self._maas_client.get_machine(deployed_app.vmdetails.uid)

        if machine.power_state == PowerState.OFF:
            return

        try:
            self._logger.info(f"Powering Off machine '{repr(machine)}'")
            machine.power_off(wait=False)
        except Exception:
            self._logger.warning("Error happened during Powering Off", exc_info=True)
        finally:
            self._maas_client.api.machines.list()

        wait_time = 5
        timeout = 5 * 60
        timeout_time = datetime.now() + timedelta(seconds=timeout)

        while datetime.now() <= timeout_time:

            machine = self._maas_client.get_machine(deployed_app.vmdetails.uid)
            self._logger.info(f"Machine: {repr(machine)} power state: {repr(machine.power_state)}")

            if machine.power_state == PowerState.OFF:
                break

            time.sleep(wait_time)

            if machine.power_state == PowerState.ERROR:
                raise Exception(f"Failed to power off machine. Machine power state: {repr(machine.power_state)}")

        if machine.power_state != PowerState.OFF:
            raise Exception(f"Failed to power off machine. Machine power state: {repr(machine.power_state)}")
