import json
import os
import shutil
from time import sleep
from runflare import inquirer

from runflare.runflare_client.requester import Requester

from runflare.runflare_client.data_manager.adapter import Adapter
from pprint import pprint
from runflare.runflare_client.service.projects import get_projects, get_project_items
from colorama import Fore, Style, init
from runflare.utils import clear, compare, make_tar, list_to_dict, makedirs
from .cache import Cache_Manager
from .upload import upload, pre_upload_check, uploader_info
from runflare.runflare_client.service.manage import restart
from ...settings import FOLDER_NAME, TAR_NAME, CHANGES_NAME, MAX_TRY, USER_HOME_PATH, RESTART_URL


def deploy(y):
    project_root = Adapter.get_project_root()
    clear()
    cache_object = Cache_Manager(project_root, type="Deploy")
    data = cache_object.cache(y)
    selected_project, selected_service, selected_service_id = data[1], data[2], data[3]

    try_num = 1
    while try_num <= MAX_TRY:
        clear()
        print(Style.BRIGHT + f"Uploading Try ({try_num}/{MAX_TRY})")
        status, response = uploader_info(selected_service_id)
        if "401" in response:
            return Fore.RED + response
        if status:
            break
        try_num += 1
        sleep(2)
    if not status:
        return Fore.RED + response

    url = response.json().get("url")
    token = response.json().get("token")
    free_disk = response.json().get("free_disk")
    restart = response.json().get("restart")

    status, response = pre_upload_check(url, token)
    if not status:
        return Fore.RED + response
    clear()
    print(Style.BRIGHT + f"Scaning {project_root} ...")
    new, changed, deleted, scaned_files = compare(project_root)
    print(Fore.GREEN + Style.BRIGHT + "Scan Finished")
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
    make_tar(project_root, changed, new)
    print(Fore.GREEN + Style.BRIGHT + "Compressing Finished")
    size = os.path.getsize(project_root + f"/{FOLDER_NAME}/{TAR_NAME}") / 1048576
    if free_disk < size:
        print(Fore.RED + Style.BRIGHT + "Not Enough Disk,Please Upgrade Your Plan")
        exit()

    status, response = upload(project_root, url, token)
    if status:
        Adapter.save_last_deploy(project_root + f"/{FOLDER_NAME}/")
        os.remove(project_root + f"/{FOLDER_NAME}/{TAR_NAME}")
        os.remove(project_root + f"/{FOLDER_NAME}/{CHANGES_NAME}")
        result = "\n\n {}Files Successfully Uploaded {:.3f} MB".format(Fore.GREEN + Style.BRIGHT, size)
        result += "\n\n  Scaned Files :{} \n   {}New Files :{} \n   Changed Files :{} \n   Deleted Files :{}\n".format(
            scaned_files, Fore.GREEN, len(new), len(changed), len(deleted))
        print(result)
        action = "ON" if restart else "OFF"
        print(f"{Fore.GREEN}Auto Restart is {action}")
        print(f"{Fore.GREEN}You Can Change Auto Restart After Deploy Feature, From Runflare.com")
        print(f"{Fore.GREEN}Deployment takes time, watch log with runflare log -f -y")
        if restart:
            request = Requester("PATCH", RESTART_URL.format(data[3]))
            status, response = request.get_response
            if not status:
                return Fore.RED + response

    else:
        return Fore.RED + response


def reset():
    status,roots = Adapter.get_roots()
    if not status:
        return Fore.RED + "Deploy root not Found"
    root_lst = []
    for i,root in roots:
        root_lst.append(root)

    questions =[
        inquirer.Checkbox(
            "delete_roots",
            message='Select path to delete (Use Space to Select , Enter to Submit)',
            choices=root_lst,
        ),
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        exit()
    delete_roots = answers['delete_roots']
    if not delete_roots:
        return Fore.RED + "No Item Selected ,Use Space to Select , Enter to Submit !"
    Adapter.delete_roots(delete_roots)
    return "Deploy Root Deleted Successfully"

def reset_all():
    status,roots = Adapter.get_roots()
    if not status:
        print(Fore.RED + "Deploy root not Found")
        exit()
    questions = [
        inquirer.Confirm("delete", message="Do you want to Delete all Data??"),
    ]
    questions = inquirer.prompt(questions)
    if not questions:
        exit()
    answer = questions['delete']

    if answer:
        for root in roots:
            path = f"{root[1]}\\{FOLDER_NAME}"
            if os.path.exists(path):
                shutil.rmtree(path)
        main_root=str(USER_HOME_PATH) + f"/{FOLDER_NAME}/"
        shutil.rmtree(main_root)
        print(Fore.RED + "Successfully Cleaned")
    else:
        print(Fore.RED + "Choose Carefully")