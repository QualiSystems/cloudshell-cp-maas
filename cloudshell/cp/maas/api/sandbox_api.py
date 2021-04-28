from cloudshell.api.cloudshell_api import SandboxDataKeyValue


class CSAPIHelper:
    def __init__(self, api, sandbox_id):
        self._api = api
        self._sandbox_id = sandbox_id

    def get_sandbox_data(self):
        return self._api.GetSandboxData(self._sandbox_id).SandboxDataKeyValues

    def get_sandbox_data_item(self, name):
        return next((x.Value for x in self.get_sandbox_data() if x.Key == name), None)

    def add_sandbox_data_item(self, key, value):
        self._api.SetSandboxData(self._sandbox_id,
                                 SandboxDataKeyValue(key, value))
