class BaseMaasException(Exception):
    pass


class MachineNotFoundException(BaseMaasException):
    """Machine not found."""


class InterfaceNotFoundException(BaseMaasException):
    """Interface on the machine was not found."""


class IPAddressNotFoundException(BaseMaasException):
    """IP Address on the machine was not found."""
