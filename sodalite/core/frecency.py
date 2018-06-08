from typing import List


class Access:
    def __init__(self, timestamp):
        self.timestamp = timestamp


class AccessHistory:
    def __init__(self, access_list: List[Access]):
        self.access_list: List[Access] = access_list

    def append(self, access: Access):
        self.access_list.append(access)
