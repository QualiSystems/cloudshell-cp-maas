from cloudshell.cp.core.request_actions.models import DeployApp
from cloudshell.shell.standards.core.resource_config_entities import (
    ResourceAttrRO,
    ResourceBoolAttrRO,
)

from cloudshell.cp.maas import constants


class ResourceAttrRODeploymentPath(ResourceAttrRO):
    def __init__(self, name: str, namespace="DEPLOYMENT_PATH"):
        super().__init__(name, namespace)


class ResourceBoolAttrRODeploymentPath(ResourceBoolAttrRO):
    def __init__(self, name: str, namespace="DEPLOYMENT_PATH", *args, **kwargs):
        super().__init__(name, namespace, *args, **kwargs)


class MaasMachineAttributeNames:
    cpu_cores = "CPU Cores"
    ram = "RAM GiB"
    disks = "Disks"
    storage = "Storage GB"
    operation_system = "Operation System"


class MaasMachineDeployApp(DeployApp):
    ATTR_NAMES = MaasMachineAttributeNames
    DEPLOYMENT_PATH = constants.MAAS_MACHINE_DEPLOYMENT_PATH

    cpu_cores = ResourceAttrRODeploymentPath(ATTR_NAMES.cpu_cores)
    ram = ResourceAttrRODeploymentPath(ATTR_NAMES.ram)
    disks = ResourceAttrRODeploymentPath(ATTR_NAMES.disks)
    storage = ResourceAttrRODeploymentPath(ATTR_NAMES.storage)
    operation_system = ResourceAttrRODeploymentPath(ATTR_NAMES.operation_system)
