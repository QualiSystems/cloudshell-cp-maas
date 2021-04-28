import re
from functools import lru_cache


class MachinePartition:
    PARTITION_MATCH_PATTERN = re.compile(
        r"((?P<mount>/\w*),)*(?P<size>(\d+\wB|all))(,(?P<filesystem>\w+))*",
        re.IGNORECASE)

    def __init__(self, request_str):
        params_dict_match = self.PARTITION_MATCH_PATTERN.search(request_str)
        if not params_dict_match:
            raise Exception(f"Unable to parse Disk Attribute item: {request_str}")
        params_dict = params_dict_match.groupdict()
        self.mount_name = params_dict["mount"]
        self.filesystem = params_dict["filesystem"] or "ext4"
        self._size = params_dict["size"]
        self.exists = False
        self._final_size = None

    # ToDo: rewrite it properly.
    @property
    @lru_cache()
    def size(self):
        if not self._final_size:
            if "all" in self._size.lower():
                self._final_size = -1
            elif "mb" in self._size.lower():
                self._final_size = int(self._size.lower().replace("mb", "").strip()) * 1000000
            elif "gb" in self._size.lower():
                self._final_size = int(self._size.lower().replace("gb", "").strip()) * 1000000000
            elif "tb" in self._size.lower():
                self._final_size = int(self._size.lower().replace("tb", "").strip()) * 1000000000000
            else:
                self._final_size = int(re.sub(r"[\w\s]", "", self._size)) * 1000000000
        return self._final_size
