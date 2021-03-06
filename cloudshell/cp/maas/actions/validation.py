from logging import Logger

from cloudshell.cp.maas import exceptions
from cloudshell.cp.maas.api.client import MaasAPIClient
from cloudshell.cp.maas.exceptions import InvalidAttributeException
from cloudshell.cp.maas.resource_config import MaasResourceConfig


class ValidationActions:
    def __init__(
        self,
        maas_client: MaasAPIClient,
        resource_config: MaasResourceConfig,
        logger: Logger,
    ):
        self._maas_client = maas_client
        self._resource_config = resource_config
        self._logger = logger

    def validate_resource_conf(self):
        conf = self._resource_config
        _is_not_empty(conf.address, "address")
        _is_not_empty(conf.api_user, conf.ATTR_NAMES.api_user)
        _is_not_empty(conf.api_password, conf.ATTR_NAMES.api_password)
        _is_not_empty(conf.api_scheme, conf.ATTR_NAMES.api_scheme)
        _is_not_empty(conf.api_port, conf.ATTR_NAMES.api_port)
        _is_not_empty(conf.default_fabric, conf.ATTR_NAMES.default_fabric)
        _is_not_empty(conf.default_subnet, conf.ATTR_NAMES.default_subnet)
        _is_not_empty(conf.ssh_keypair_path, conf.ATTR_NAMES.ssh_keypair_path)

    def validate_connection(self):
        try:
            _ = self._maas_client.api  # try to connect
        except Exception:
            self._logger.exception("Unable to initialize API:")
            raise exceptions.MaasApiConnectionError("Unable to connect to MAAS API. Sell logs for the details")

    def validate_default_fabric(self):
        self._maas_client.get_fabric(name=self._resource_config.default_fabric)

    def validate_default_subnet(self):
        self._maas_client.get_subnet(
            subnet_name=self._resource_config.default_subnet, fabric_name=self._resource_config.default_fabric
        )


def _is_not_empty(value: str, attr_name: str):
    if not value:
        raise InvalidAttributeException(f"'{attr_name}' cannot be empty")
