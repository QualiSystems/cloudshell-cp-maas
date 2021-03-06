class MaasDeleteFlow:
    def __init__(self, resource_config, maas_client, logger):
        self._resource_config = resource_config
        self._maas_client = maas_client
        self._logger = logger

    def delete_instance(self, deployed_app):
        machine = self._maas_client.get_machine(deployed_app.vmdetails.uid)
        machine.release()
        # delete link to default fabric and subnet
        # try:
        #     iface = machine.interfaces[0]
        #     iface.disconnect()
        # except IndexError:
        #     pass
