from cloudshell.cp.maas import constants


class MaasRemoteRefreshIPFlow:
    def __init__(
        self, resource_config, maas_client, cancellation_manager, cs_api, logger
    ):
        self._resource_config = resource_config
        self._maas_client = maas_client
        self._cancellation_manager = cancellation_manager
        self._cs_api = cs_api
        self._logger = logger

    def refresh_ip(self, deployed_app):
        with self._cancellation_manager:
            machine = self._maas_client.get_machine(deployed_app.vmdetails.uid)
            ip_address = self._maas_client.get_machine_ip(
                machine=machine, subnet_name=constants.DEFAULT_SUBNET_NAME
            )

        self._cs_api.UpdateResourceAddress(
            resourceFullPath=deployed_app.name,
            resourceAddress=ip_address,
        )

        return ip_address
