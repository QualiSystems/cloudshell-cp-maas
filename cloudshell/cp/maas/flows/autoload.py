from cloudshell.shell.core.driver_context import AutoLoadDetails

from cloudshell.cp.maas.actions.validation import ValidationActions


class MaasAutoloadFlow:
    def __init__(self, resource_config, maas_client, logger):
        self._resource_config = resource_config
        self._maas_client = maas_client
        self._logger = logger

    def discover(self):
        validation_actions = ValidationActions(
            maas_client=self._maas_client,
            resource_config=self._resource_config,
            logger=self._logger,
        )
        validation_actions.validate_resource_conf()
        validation_actions.validate_connection()
        validation_actions.validate_default_fabric()
        validation_actions.validate_default_subnet()

        return AutoLoadDetails([], [])
