from canonical.maas.flows import BaseMaasFlow
from cloudshell.shell.core.driver_context import AutoLoadDetails


class MaasAutoloadFlow(BaseMaasFlow):
    def discover(self):
        """

        :return:
        """
        return AutoLoadDetails([], [])
