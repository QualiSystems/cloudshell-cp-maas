from datetime import datetime, timedelta

import time

from cloudshell.cp.core.flows.deploy import AbstractDeployFlow
from cloudshell.cp.core.request_actions.models import DeployAppResult
from cloudshell.cp.maas.exceptions import InterfaceNotFoundException, MachineNotFoundException
from maas.client.viscera.machines import NodeStatus

from cloudshell.cp.maas.models.machine_disk import MachineDisk


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

        if deploy_app.hostname:
            with self._cancellation_manager:
                machine = next((x for x in self._maas_client.api.machines.list()
                                if x.status == NodeStatus.READY and x.pool.name == self._resource_config.default_pool
                                and (x.hostname == deploy_app.hostname
                                     or x.fqdn == deploy_app.hostname)), None)
        else:
            with self._cancellation_manager:
                machine = self._maas_client.get_available_machine(
                    cpus=int(deploy_app.cpu_cores),
                    memory=float(deploy_app.ram),
                    disks=len(deploy_app.disks),
                    storage=float(deploy_app.storage),
                )

        if not machine:
            raise MachineNotFoundException("Unable to find requested machine. Please check Deployment Path Attributes")

        self._logger.info(f"Found available machine '{repr(machine)}'")
        uuid = machine.system_id
        vm_name = f"{deploy_app.app_name}_{uuid}"
        if deploy_app.disks:
            self._change_partitions_layout(machine, deploy_app)

        with self._cancellation_manager:
            try:
                self._logger.info(f"Deploying OS Distribution '{deploy_app.distribution}' on machine '{repr(machine)}'")
                machine.deploy(distro_series=deploy_app.distribution, wait=False)
            except Exception:
                self._logger.warning("Error happened during deployment", exc_info=True)

        time.sleep(180)
        wait_time = 5
        timeout = 30 * 60
        timeout_time = datetime.now() + timedelta(seconds=timeout)

        while datetime.now() <= timeout_time:
            machine = self._maas_client.get_machine(uuid)
            if not machine:
                continue
            self._logger.info(f"Machine: {repr(machine)} Status: {repr(machine.status)}")

            if machine.status == NodeStatus.DEPLOYED:
                break
            time.sleep(wait_time)

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

    def _change_partitions_layout(self, machine, deploy_app):
        partition_size_calibrate = []
        for requested_disk in deploy_app.disks:
            all_size_partition = None
            disk = machine.block_devices.by_name.get(requested_disk.disk_name, None)
            if not disk:
                continue

            for existing_partition in disk.partitions:
                keep = False
                for requested_partition in requested_disk.defined_partitions:
                    size = requested_partition.size
                    try:
                        if size == requested_partition.size \
                                and existing_partition.filesystem.mount_point \
                                and existing_partition.filesystem.mount_point == requested_partition.mount_name \
                                and existing_partition.filesystem.fstype == requested_partition.filesystem:
                            existing_partition.exists = True
                            keep = True
                            break
                    except:
                        self._logger.exception(f"Unable to remove {existing_partition.path.split('/')[-1]}")
                if not keep:
                    existing_partition.delete()
            if len(partition_size_calibrate) > 1:
                raise Exception("Disk Deployment Path Disk Attribute ")

            machine = self._maas_client.get_machine(machine.system_id)
            disk = machine.block_devices.by_name.get(requested_disk.disk_name, None)
            for new_partition in requested_disk.defined_partitions:
                if not new_partition.exists:
                    partition = disk.partitions.create(new_partition.size)
                    if new_partition.filesystem:
                        partition.format(new_partition.filesystem)
                    if new_partition.mount_name:
                        partition.mount(new_partition.mount_name)

            machine = self._maas_client.get_machine(machine.system_id)
            disk = machine.block_devices.by_name.get(requested_disk.disk_name, None)
            for new_all_size_partition in requested_disk.all_size_partitions:
                if not new_all_size_partition.exists:
                    if disk.available_size <= 0:
                        raise MachineNotFoundException(
                            f"Unable to create {all_size_partition.mount_name} inside {disk.name}")
                    partition = disk.partitions.create(disk.available_size-10000000)
                    if new_all_size_partition.filesystem:
                        partition.format(new_all_size_partition.filesystem)
                    if new_all_size_partition.mount_name:
                        partition.mount(new_all_size_partition.mount_name)
