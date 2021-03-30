class BaseMaasException(Exception):
    pass


class MaasApiConnectionError(BaseMaasException):
    """Unable to connect to MAAS API."""


class InvalidAttributeException(BaseMaasException):
    """Attribute is not valid."""


class FabricNotFoundException(BaseMaasException):
    """Fabric not found."""


class SubnetNotFoundException(BaseMaasException):
    """Subnet not found."""


class MachineNotFoundException(BaseMaasException):
    """Machine not found."""


class InterfaceNotFoundException(BaseMaasException):
    """Interface on the machine was not found."""


class IPAddressNotFoundException(BaseMaasException):
    """IP Address on the machine was not found."""
