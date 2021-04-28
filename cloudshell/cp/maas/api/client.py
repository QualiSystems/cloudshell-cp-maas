import time
from datetime import datetime, timedelta
from http import HTTPStatus

from maas.client import login
from maas.client.viscera.machines import Machine
from maas.client.bones import CallError
from maas.client.enum import LinkMode, NodeStatus

from cloudshell.cp.maas import exceptions


class MaasAPIClient:
    MACHINE_INTERFACE_TPL = "Quali_{machine_name}"

    def __init__(self, address, user, password, port, scheme, pool, logger):
        self._address = address
        self._user = user
        self._password = password
        self._port = port
        self._scheme = scheme
        self._logger = logger
        self._pool = pool
        self._api = None

    @property
    def api(self):
        if self._api is None:
            self._api = self._initialize_api()

        return self._api

    def _initialize_api(self):
        self._logger.info("Initializing MAAS API client...")

        return login(
            f"{self._scheme}://{self._address}:{self._port}/MAAS/",
            username=self._user,
            password=self._password,
            insecure=True,
        )

    def get_machine(self, uuid: str, timeout=6, wait_time=5) -> Machine:
        """Get machine by its uuid."""
        timeout_time = datetime.now() + timedelta(seconds=timeout * 60)
        while datetime.now() <= timeout_time:
            try:
                machine = next((x for x in self.api.machines.list() if x.system_id == uuid
                                                                    and x.pool.name == self._pool),
                               None)
                self._logger.info(f"Machine: {repr(machine)} Status: {repr(machine.status)}")
                return machine
            except Exception:
                self._logger.warning("Error happened while waiting to response from MAAS", exc_info=True)

    def get_available_machine(
        self,
        cpus: int,
        memory: float,
        disks: int,
        storage: float
    ):
        """Get first available machine with given params."""
        available_machines = list(
            filter(
                lambda machine: all(
                    [
                        machine.status == NodeStatus.READY,
                        machine.pool.name == self._pool,
                        cpus <= machine.cpus,
                        memory <= machine.memory / 1024,
                        disks <= machine.block_devices,
                    ]
                ),
                self.api.machines.list(),
            )
        )

        available_machines = sorted(
            available_machines,
            key=lambda machine: (
                machine.cpus,
                machine.memory,
                len(machine.block_devices),
            ),
        )

        if not available_machines:
            raise exceptions.MachineNotFoundException(
                f"There are no free machine for the given params: "
                f"CPU Cores: {cpus}, "
                f"RAM GiB: {memory},"
                f"Disks: {disks}, "
                f"Storage GB: {storage}"
            )

        return available_machines[0]

    def get_fabric(self, name: str):
        """Get Fabric by name."""
        try:
            return self.api.fabrics.get(name)
        except CallError as e:
            if e.status == HTTPStatus.NOT_FOUND:
                raise exceptions.FabricNotFoundException(
                    f"Failed to find Fabric '{name}'"
                )
            raise

    def get_subnet(self, subnet_name: str, fabric_name: str):
        fabric = self.get_fabric(fabric_name)

        for subnet in self.api.subnets.list():
            if (
                any([subnet.name == subnet_name, subnet.cidr == subnet_name])
                and subnet.vlan.fabric.id == fabric.id
            ):
                return subnet

        raise exceptions.SubnetNotFoundException(
            f"Failed to find Subnet '{subnet_name}' under Fabric '{fabric_name}'"
        )

    def create_interface_link(self, interface, subnet, mode=LinkMode.DHCP):
        """Create Link for the given Interface."""
        return interface.links.create(subnet=subnet, mode=mode)

    def reconnect_machine_interface(self, interface, subnet):
        """Reconnect Machine interface to the provided subnet."""
        interface.vlan = subnet.vlan
        interface.save()

    def get_machine_ip(self, machine, subnet_name):
        """Get Machine IP address from the default subnet."""
        for iface in machine.interfaces:
            for link in iface.links:
                if link.subnet.name == subnet_name or link.subnet.cidr == subnet_name:
                    return link.ip_address

        raise exceptions.IPAddressNotFoundException(
            "Unable to find IP Address on the machine from the Sandbox subnet"
        )

    def create_ssh_key(self, public_key: str):
        return self.api.ssh_keys.create(key=public_key)

    def get_ssh_key(self, id: int):
        return self.api.ssh_keys.get(id=id)

    def remove_ssh_key(self, id: int):
        return self.api.ssh_keys.delete(id=id)
