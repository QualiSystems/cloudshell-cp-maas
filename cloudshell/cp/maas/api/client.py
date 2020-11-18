from http import HTTPStatus

from maas.client import login
from maas.client.bones import CallError
from maas.client.enum import LinkMode, NodeStatus

from cloudshell.cp.maas import exceptions


class MaasAPIClient:
    MACHINE_INTERFACE_TPL = "Quali_{machine_name}"

    def __init__(self, address, user, password, port, scheme, logger):
        self._address = address
        self._user = user
        self._password = password
        self._port = port
        self._scheme = scheme
        self._logger = logger
        self._api = self._get_api()

    def _get_api(self):
        self._logger.info("Initializing MAAS API client...")

        return login(
            f"{self._scheme}://{self._address}:{self._port}/MAAS/",
            username=self._user,
            password=self._password,
            insecure=True,
        )

    def get_machine(self, uuid: str):
        """Get machine by its uuid."""
        return self._api.machines.get(uuid)

    def get_available_machine(
        self, cpus: int, memory: float, disks: int, storage: float
    ):
        """Get first available machine with given params."""
        available_machines = list(
            filter(
                lambda machine: all(
                    [
                        machine.status == NodeStatus.READY,
                        cpus <= machine.cpus,
                        memory <= machine.memory / 1024,
                        disks <= len(machine.block_devices),
                    ]
                ),
                self._api.machines.list(),
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

    def get_or_create_fabric(self, name: str):
        """Get or create fabric by name."""
        try:
            return self._api.fabrics.get(name)
        except CallError as e:
            if e.status == HTTPStatus.NOT_FOUND:
                return self._api.fabrics.create(name=name)
            raise

    def get_or_create_subnet(self, name, cidr, gateway_ip, vlan, managed):
        """Get or create subnet."""
        try:
            return self.get_subnet(name)
        except CallError as e:
            if e.status == HTTPStatus.NOT_FOUND:
                return self._api.subnets.create(
                    cidr=cidr,
                    name=name,
                    vlan=vlan,
                    gateway_ip=gateway_ip or None,
                    managed=managed,
                )
            raise

    def get_subnet(self, name: str):
        """Get Subnet by name."""
        return self._api.subnets.get(name)

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
                if link.subnet.name == subnet_name:
                    return link.ip_address

        raise exceptions.IPAddressNotFoundException(
            "Unable to find IP Address on the machine from the Sandbox subnet"
        )

    def create_ssh_key(self, public_key: str):
        self._api.ssh_keys.create(key=public_key)
