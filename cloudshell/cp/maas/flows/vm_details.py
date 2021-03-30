from cloudshell.cp.core.flows.vm_details import AbstractVMDetailsFlow
from cloudshell.cp.core.request_actions.models import (
    VmDetailsData,
    VmDetailsNetworkInterface,
    VmDetailsProperty,
)


class MaasGetVMDetailsFlow(AbstractVMDetailsFlow):
    def __init__(self, resource_config, maas_client, cancellation_manager, logger):
        super().__init__(logger=logger)
        self._resource_config = resource_config
        self._maas_client = maas_client
        self._cancellation_manager = cancellation_manager

    def _get_vm_details(self, deployed_app):
        vm_network_data = []

        with self._cancellation_manager:
            machine = self._maas_client.get_machine(deployed_app.vmdetails.uid)

        data = [
            VmDetailsProperty(key="Architecture", value=machine.architecture),
            VmDetailsProperty(key="HWE Kernel", value=machine.hwe_kernel),
            VmDetailsProperty(key="CPU Cores", value=machine.cpus),
            VmDetailsProperty(key="RAM GiB", value=machine.memory // 1024),
            VmDetailsProperty(key="Disks", value=len(machine.block_devices)),
            VmDetailsProperty(key="Distro Series", value=machine.distro_series),
            VmDetailsProperty(key="Operation System", value=machine.osystem),
        ]

        for iface in machine.interfaces:
            network_data = [
                VmDetailsProperty(key="MAC Address", value=iface.mac_address),
            ]

            for link in iface.links:
                iface_id = hash(f"{iface.id}_{link.id}")
                interface = VmDetailsNetworkInterface(
                    interfaceId=iface_id,
                    networkId=iface_id,
                    isPredefined=True,
                    networkData=network_data,
                    privateIpAddress=link.ip_address,
                )
                if link.subnet == self._resource_config.default_subnet:
                    vm_network_data.append(interface)

        vm_details_data = VmDetailsData(
            vmInstanceData=data,
            vmNetworkData=vm_network_data,
            appName=deployed_app.name,
        )

        return vm_details_data
