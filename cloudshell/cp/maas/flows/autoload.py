from cloudshell.shell.core.driver_context import AutoLoadDetails


class MaasAutoloadFlow:
    def __init__(self, resource_config, maas_client, logger):
        self._resource_config = resource_config
        self._maas_client = maas_client
        self._logger = logger

    def discover(self):
        return AutoLoadDetails([], [])
