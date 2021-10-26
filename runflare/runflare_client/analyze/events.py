
from runflare.settings import EVENTS_URL,NR_EVENTS_URL
from runflare.runflare_client.requester import Requester
from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.runflare_client.deploy.cache import Cache_Manager
from runflare.runflare_client.web_socket import Socket
from runflare.utils import clear
from colorama import Fore, Style

def events(y,f):
    project_root = Adapter.get_project_root()
    clear()
    cache_object = Cache_Manager(project_root, type="Watch Events")
    data = cache_object.cache(y)
    if f:
        Socket().run_loop("watch", EVENTS_URL, data[1])
    request = Requester("GET", NR_EVENTS_URL.format(data[1]))
    status, response = request.get_response
    if status:
        return response.json().get("data", "")
    else:
        return Fore.RED + response