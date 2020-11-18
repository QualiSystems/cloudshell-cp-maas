from cloudshell.shell.standards.core.resource_config_entities import (
    GenericResourceConfig,
    PasswordAttrRO,
    ResourceAttrRO,
    ResourceBoolAttrRO,
)

from cloudshell.cp.maas.constants import SHELL_NAME


class ResourceAttrROShellName(ResourceAttrRO):
    def __init__(self, name: str, namespace=ResourceAttrRO.NAMESPACE.SHELL_NAME):
        super().__init__(name, namespace)


class ResourceBoolAttrROShellName(ResourceBoolAttrRO):
    def __init__(
        self,
        name: str,
        namespace=ResourceBoolAttrRO.NAMESPACE.SHELL_NAME,
        *args,
        **kwargs
    ):
        super().__init__(name, namespace, *args, **kwargs)


class MaasAttributeNames:
    api_user = "User"
    api_password = "Password"
    api_scheme = "Scheme"
    api_port = "Port"
    default_subnet = "Default Subnet"
    default_gateway = "Default Gateway IP"
    managed_allocation = "Managed Allocation"
    ssh_keypair_path = "SSH Keypair Path"


class MaasResourceConfig(GenericResourceConfig):
    ATTR_NAMES = MaasAttributeNames

    api_user = ResourceAttrROShellName(ATTR_NAMES.api_user)
    api_password = PasswordAttrRO(
        ATTR_NAMES.api_password, PasswordAttrRO.NAMESPACE.SHELL_NAME
    )
    api_scheme = ResourceAttrROShellName(ATTR_NAMES.api_scheme)
    api_port = ResourceAttrROShellName(ATTR_NAMES.api_port)
    default_subnet = ResourceAttrROShellName(ATTR_NAMES.default_subnet)
    default_gateway = ResourceAttrROShellName(ATTR_NAMES.default_gateway)
    managed_allocation = ResourceBoolAttrROShellName(
        ATTR_NAMES.managed_allocation, default=True
    )
    ssh_keypair_path = ResourceAttrROShellName(ATTR_NAMES.ssh_keypair_path)

    @classmethod
    def from_context(cls, context, shell_name=SHELL_NAME, api=None, supported_os=None):
        """Creates an instance of a Resource by given context.

        :param str shell_name: Shell Name
        :param list supported_os: list of supported OS
        :param cloudshell.shell.core.driver_context.ResourceCommandContext context:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession api:
        :rtype: MaasResourceConfig
        """
        return super().from_context(
            context=context, shell_name=shell_name, api=api, supported_os=supported_os
        )
