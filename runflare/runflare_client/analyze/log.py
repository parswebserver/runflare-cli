import asyncio

from runflare.runflare_client.requester import Requester
from runflare.settings import LOG_URL, NR_LOG_URL
from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.runflare_client.deploy.cache import Cache_Manager
from runflare.runflare_client.web_socket import Socket
from runflare.utils import clear
from colorama import Fore, Style


def log(y,f):
    project_root = Adapter.get_project_root()
    clear()
    cache_object = Cache_Manager(project_root, type="Watch Log")
    data = cache_object.cache(y)
    if f:
        Socket().run_loop("watch", LOG_URL, data[3])
    request = Requester("GET", NR_LOG_URL.format(data[3]))
    status, response = request.get_response
    if status:
        return response.json().get("data","")
    else:
        return Fore.RED + response
