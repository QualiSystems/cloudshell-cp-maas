from cloudshell.cp.core.flows.deploy import AbstractDeployFlow
from cloudshell.cp.core.request_actions.models import DeployAppResult

from cloudshell.cp.maas import constants
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
        subnet = self._maas_client.get_subnet(constants.DEFAULT_SUBNET_NAME)

        self._maas_client.reconnect_machine_interface(interface=iface, subnet=subnet)
        self._maas_client.create_interface_link(interface=iface, subnet=subnet)

    def _prepare_deploy_app_result(self, deployed_machine, deploy_app):
        """Prepare Deploy App result for the CloudShell."""
        return DeployAppResult(
            actionId=deploy_app.actionId,
            vmUuid=deployed_machine.system_id,
            vmName=deploy_app.name,
            vmDetailsData=None,  # todo: add VM details here (user, password, IP)
            deployedAppAdditionalData={},
        )

    def _deploy(self, request_actions):
        deploy_app = request_actions.deploy_app

        with self._cancellation_manager:
            machine = self._maas_client.get_available_machine(
                cpus=int(deploy_app.cpu_cores),
                memory=float(deploy_app.ram),
                disks=int(deploy_app.disks),
                storage=float(deploy_app.storage),
            )

        with self._cancellation_manager:
            machine.deploy(distro_series=deploy_app.operation_system, wait=True)

        with self._cancellation_manager:
            self._reconnect_machine_to_sandbox_subnet(machine=machine)

        return self._prepare_deploy_app_result(
            deployed_machine=machine,
            deploy_app=deploy_app,
        )
