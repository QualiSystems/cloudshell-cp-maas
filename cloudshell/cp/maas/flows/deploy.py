from datetime import datetime, timedelta

import time

from maas.client.enum import NodeStatus

from cloudshell.cp.core.flows.deploy import AbstractDeployFlow
from cloudshell.cp.core.request_actions.models import DeployAppResult
from cloudshell.cp.maas.exceptions import InterfaceNotFoundException


class MaasDeployFlow(AbstractDeployFlow):
    def __init__(self, resource_config, maas_client, cancellation_manager, logger):
        super().__init__(logger=logger)
        self._resource_config = resource_config
        self._maas_client = maas_client
        self._cancellation_manager = cancellation_manager

    def _reconnect_machine_to_sandbox_subnet(self, machine):
        """Reconnect machine to the Sandbox subnet."""
        try:
            iface = machine.interfaces[0]
        except IndexError:
            raise InterfaceNotFoundException(
                "Unable to connect machine to default subnet. No interface on machine"
            )
        subnet = self._maas_client.get_subnet(
            subnet_name=self._resource_config.default_subnet,
            fabric_name=self._resource_config.default_fabric,
        )

        self._logger.info(f"Reconnecting machine interface '{iface}' to subnet '{subnet}'...")
        # self._maas_client.reconnect_machine_interface(interface=iface, subnet=subnet)

        self._logger.info(f"Creating link on the interface '{iface}'...")
        # self._maas_client.create_interface_link(interface=iface, subnet=subnet)

    def _prepare_deploy_app_result(self, deployed_machine, deploy_app, vm_name):
        """Prepare Deploy App result for the CloudShell."""
        return DeployAppResult(
            actionId=deploy_app.actionId,
            vmUuid=deployed_machine.system_id,
            deployedAppAddress=self._maas_client.get_machine_ip(
                machine=deployed_machine, subnet_name=self._resource_config.default_subnet
            ),
            vmName=vm_name,
            vmDetailsData=None,  # todo: add VM details here (user, password, IP)
            deployedAppAdditionalData={},
        )

    def _deploy(self, request_actions):
        deploy_app = request_actions.deploy_app
        self._logger.info("Searching for available machine...")

        with self._cancellation_manager:
            machine = self._maas_client.get_available_machine(
                cpus=int(deploy_app.cpu_cores),
                memory=float(deploy_app.ram),
                disks=int(deploy_app.disks),
                storage=float(deploy_app.storage),
            )

        self._logger.info(f"Found available machine '{repr(machine)}'")
        uuid = machine.system_id
        vm_name = f"{deploy_app.app_name}_{uuid}"

        with self._cancellation_manager:
            try:
                self._logger.info(f"Deploying OS Distribution '{deploy_app.distribution}' on machine '{repr(machine)}'")
                machine.deploy(distro_series=deploy_app.distribution, wait=False)
            except Exception:
                self._logger.warning("Error happened during deployment", exc_info=True)

        wait_time = 5
        timeout = 30 * 60
        timeout_time = datetime.now() + timedelta(seconds=timeout)

        while datetime.now() <= timeout_time:
            try:
                machine = self._maas_client.get_machine(uuid)
                self._logger.info(f"Machine: {repr(machine)} Status: {repr(machine.status)}")

                if machine.status == NodeStatus.DEPLOYED:
                    break

                time.sleep(wait_time)
            except Exception:
                self._logger.warning("Error happened while waiting for machine to be deployed", exc_info=True)

            if machine.status == NodeStatus.FAILED_DEPLOYMENT:
                raise Exception(f"Failed to deploy Machine. Machine status: {repr(machine.status)}")

        if machine.status != NodeStatus.DEPLOYED:
            raise Exception(f"Failed to deploy Machine. Machine status: {repr(machine.status)}")

        # with self._cancellation_manager:
        #     self._logger.info(f"Reconnecting machine '{repr(machine)}' to the Sandbox subnet")
            # self._reconnect_machine_to_sandbox_subnet(machine=machine)

        return self._prepare_deploy_app_result(
            deployed_machine=machine,
            deploy_app=deploy_app,
            vm_name=vm_name,
        )
