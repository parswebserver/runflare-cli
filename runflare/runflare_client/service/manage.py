from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.runflare_client.requester import Requester
from runflare.settings import START_URL,STOP_URL,RESTART_URL

from runflare.runflare_client.deploy.cache import Cache_Manager

from colorama import Fore, Style
from halo import Halo

from runflare.utils import clear


# @Halo(text=Style.BRIGHT + "Starting ... ", color="magenta")
def start(y):
    clear()
    project_root = Adapter.get_project_root()
    cache_object = Cache_Manager(project_root, type="Start")
    data = cache_object.cache(y)
    request = Requester("PATCH", START_URL.format(data[3]))
    status,response = request.get_response
    if status:
        return Fore.GREEN + "Started Successfully"
    else:
        return Fore.RED + response

# @Halo(text=Style.BRIGHT + "Stoping ...", color="magenta")
def stop(y):
    clear()
    project_root = Adapter.get_project_root()
    cache_object = Cache_Manager(project_root, type="Stop")
    data = cache_object.cache(y)
    request = Requester("PATCH", STOP_URL.format(data[3]))
    status, response = request.get_response
    if status:
        return Fore.GREEN + "Stoped Successfully"
    else:
        return Fore.RED + response

# @Halo(text=Style.BRIGHT + "Restarting ...", color="magenta")
def restart(y):
    clear()
    project_root = Adapter.get_project_root()
    cache_object = Cache_Manager(project_root, type="Restart")
    data = cache_object.cache(y)
    request = Requester("PATCH", RESTART_URL.format(data[3]))
    status, response = request.get_response
    if status:
        return Fore.GREEN + "Restarted Successfully"
    else:
        return Fore.RED + response