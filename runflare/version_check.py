from runflare import VERSION
from runflare.runflare_client.requester import Requester
from runflare.settings import VERSION_URL,BASE_URL
from halo import Halo
from colorama import Style
import requests
class Version:
    def __init__(self, version_str):
        self.version_tuple = self._parse_version(version_str)


    def _parse_version(self, version_str):
        try:
            version = list(map(int, version_str.split('.')))
            if len(version) == 0:
                return [0, ]
            version.extend([0] * (3 - len(version)))
            return version
        except Exception:
            return [0]

    def __len__(self):
        return len(self.version_tuple)

    def __gt__(self, other):

        this, that = self._make_same_length(self.version_tuple, other.version_tuple)
        for index, version_part in enumerate(this):
            if version_part > that[index]:
                return True
            elif version_part < that[index]:
                return False
        return False

    def _make_same_length(self, first, second):
        max_length = max(len(first), len(second))
        the_first = first + [0] * (max_length - len(first))
        the_second = second + [0] * (max_length - len(second))
        return the_first, the_second

    def compare(self, other):
        assert isinstance(other, Version)
        this, that = self._make_same_length(self.version_tuple, other.version_tuple)
        for index, version in enumerate(this):
            if version > that[index]:
                return index + 1
            elif version < that[index]:
                return -1 * (index + 1)
        return 0

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return not self > other

    def __lt__(self, other):
        if self > other or self == other:
            return False
        return True

    def __eq__(self, other):
        assert isinstance(other, Version)
        this, that = self._make_same_length(self.version_tuple, other.version_tuple)
        return this == that

    def __str__(self):
        return ".".join(map(str, self.version_tuple))

    def __repr__(self):
        return str(self)

    @staticmethod
    def get_latest_version():
        try:
            request = requests.request("GET", BASE_URL + VERSION_URL)
        except:
            return Version("0")
        if request.status_code != 200:
            return Version("0")
        ok,response = request.ok,request.json()
        if ok:
            return Version(response.get("version"))
        else:
            return Version.get_current_version()


    @staticmethod
    def get_current_version():
        return Version(VERSION)

    @staticmethod
    @Halo(text=Style.BRIGHT + "Preparing ...", color="magenta")
    def has_new_version():
        current_version = Version.get_current_version()
        latest_version = Version.get_latest_version()
        if latest_version == Version("0"):
            return 0
        if latest_version > current_version:
            return 2
        else:
            return 1
