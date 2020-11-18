class MaasPowerManagementFlow:
    def __init__(self, resource_config, maas_client, logger):
        self._resource_config = resource_config
        self._maas_client = maas_client
        self._logger = logger

    def power_on(self, deployed_app):
        machine = self._maas_client.get_machine(deployed_app.vmdetails.uid)
        machine.power_on(wait=True)

    def power_off(self, deployed_app):
        machine = self._maas_client.get_machine(deployed_app.vmdetails.uid)
        machine.power_off(wait=True)
