import json
import os
from time import sleep
from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.runflare_client.service.projects import get_projects, get_project_items
from colorama import Fore, Style,init
from runflare.utils import clear, compare, make_tar, list_to_dict,dir_to_json,makedirs
from .cache import Cache_Manager
from .upload import upload, pre_upload_check, uploader_info

from ...settings import FOLDER_NAME, TAR_NAME, CHANGES_NAME, MAX_TRY


def deploy(y):
    project_root = Adapter.get_project_root()
    clear()
    cache_object = Cache_Manager(project_root, type="Deploy")
    data = cache_object.cache(y)
    selected_project, selected_service, selected_service_id = data[1],data[2],data[3]

    try_num = 1
    while try_num <= MAX_TRY:
        clear()
        print(Style.BRIGHT + f"Uploading Try ({try_num}/{MAX_TRY})")
        status, response = uploader_info(selected_service_id)
        if status:
            break
        try_num += 1
        sleep(2)
    if not status:
        return Fore.RED + response

    url = response.json().get("url")
    token = response.json().get("token")


    status, response = pre_upload_check(url,token)
    if not status:
        return Fore.RED + response
    clear()
    print(f"Scaning {project_root} ...")
    new, changed, deleted = compare(project_root)
    print(Style.BRIGHT + "Scan Finished")

    if not new and not deleted and not changed:
        print(Fore.RED + "No New Files\nDirectory already synced with server !")
        exit()

    makedirs(project_root + f"/{FOLDER_NAME}/")
    with open(project_root + f"/{FOLDER_NAME}/{CHANGES_NAME}", "w+") as changes:
        changes.write(json.dumps({
            "new": list_to_dict(new),
            "modify": list_to_dict(changed),
            "delete": list_to_dict(deleted)
        }, indent=4))


    print(Style.BRIGHT + "Start Compressing")
    make_tar(project_root,changed, new)
    print(Fore.GREEN + Style.BRIGHT + "Compressing Finished")

    size = os.path.getsize(project_root + f"/{FOLDER_NAME}/{TAR_NAME}") / 1048576
    status, response = upload(project_root,url,token)
    if status:
        Adapter.save_last_deploy(project_root + f"/{FOLDER_NAME}/",dir_to_json(project_root))
        os.remove(project_root + f"/{FOLDER_NAME}/{TAR_NAME}")
        os.remove(project_root + f"/{FOLDER_NAME}/{CHANGES_NAME}")
        result = "\n\n {}Files Successfully Uploaded {:.3f} MB".format(Fore.GREEN + Style.BRIGHT, size)
        result += "\n\n   {}New Files :{} \n   Changed Files :{} \n   Deleted Files :{}".format(Fore.GREEN,len(new),len(changed),len(deleted))
        result += "\nDeployment takes time, watch log with runflare log -f -y".format(Fore.GREEN)
        return result

    else:
        return Fore.RED + response


