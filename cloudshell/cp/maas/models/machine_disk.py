from functools import lru_cache

from cloudshell.cp.maas.models.machine_partition import MachinePartition


class MachineDisk:
    def __init__(self, request_str):
        self.disk_name, self._request_str = request_str.split(":")
        self._defined_partitions = []
        self._all_size_partitions = []

    @property
    def defined_partitions(self):
        self.load_partitions_configuration()
        return self._defined_partitions

    @property
    def all_size_partitions(self):
        self.load_partitions_configuration()
        return self._all_size_partitions

    @lru_cache()
    def load_partitions_configuration(self):
        for config_block in self._request_str.split(";"):
            partition = MachinePartition(config_block)
            if partition.size == -1:
                self._all_size_partitions.append(partition)
            else:
                self._defined_partitions.append(partition)
