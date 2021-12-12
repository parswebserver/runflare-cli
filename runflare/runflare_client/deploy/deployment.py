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
from ...settings import FOLDER_NAME, TAR_NAME, CHANGES_NAME, MAX_TRY, USER_HOME_PATH, RESTART_URL,LOG_URL
import sys
from halo import Halo

def deploy(y):
    project_root = Adapter.get_project_root()
    clear()
    cache_object = Cache_Manager(project_root, type="Deploy")
    data = cache_object.cache(y)
    selected_project, selected_service, selected_service_id = data[1], data[2], data[3]

    sp = Halo(text=Style.BRIGHT + f"Scaning Directory {project_root}", color="magenta")
    sp.start()
    new, changed, deleted, scaned_files = compare(project_root)
    sp.stop()
    space = " " * len(project_root)
    sys.stdout.write(f"\r √  Scaned {scaned_files} item(s)    {space}\n")

    if not new and not deleted and not changed:
        print(Fore.RED + "No New Files\nDirectory already synced with server !")
        exit()
    try_num = 1
    sp = Halo(text=Style.BRIGHT + f"Checking Upload Conditions", color="magenta")
    sp.start()
    while try_num <= MAX_TRY:
        status, response = uploader_info(selected_service_id)
        if "401" in response:
            return Fore.RED + response
        if status:
            break
        try_num += 1
        sleep(2)
    if not status:
        return Fore.RED + response
    sp.stop()
    sys.stdout.write(f"\r √  Upload Conditions Verified\n")



    url = response.json().get("url")
    token = response.json().get("token")
    free_disk = response.json().get("free_disk")
    restart_value = response.json().get("restart")

    status, response = pre_upload_check(url, token)
    if not status:
        return Fore.RED + response



    makedirs(project_root + f"/{FOLDER_NAME}/")
    changes_file_path = project_root + f"/{FOLDER_NAME}/{CHANGES_NAME}"
    with open(changes_file_path, "w+") as changes:
        changes.write(json.dumps({
            "new": list_to_dict(new),
            "modify": list_to_dict(changed),
            "delete": list_to_dict(deleted)
        }, indent=4))

    number_of_files = len(changed) + len(new)
    sp = Halo(text=Style.BRIGHT + f"Compressing 0 of {number_of_files} item(s)", color="magenta")
    sp.start()
    i = 0
    for i in make_tar(project_root, changed, new,changes_file_path=changes_file_path):
        sp.text = (Style.BRIGHT + f"Compressing {str(i)} of {number_of_files} items")
    sp.stop()
    space = " " * len(str(number_of_files) + str(i))
    sys.stdout.write(f"\r √  Compressed {number_of_files} item(s)    {space}\n")

    size = os.path.getsize(project_root + f"/{FOLDER_NAME}/{TAR_NAME}") / 1048576
    if free_disk < size:
        print(Fore.RED + Style.BRIGHT + "Not Enough Disk,Please Upgrade Your Plan")
        exit()

    upload(project_root, url, token)
    if status:
        Adapter.save_last_deploy(project_root + f"/{FOLDER_NAME}/")
        os.remove(project_root + f"/{FOLDER_NAME}/{TAR_NAME}")
        os.remove(project_root + f"/{FOLDER_NAME}/{CHANGES_NAME}")
        result = "\n\n {}Files Successfully Uploaded {:.3f} MB".format(Fore.GREEN + Style.BRIGHT, size)
        result += "\n\n  Scaned Files :{} \n   {}New Files :{} \n   Changed Files :{} \n   Deleted Files :{}\n".format(
            scaned_files, Fore.GREEN, len(new), len(changed), len(deleted))
        print(result)
        action = "ON" if restart_value else "OFF"
        print(f"{Fore.GREEN}Auto Restart is {action}")
        print(f"{Fore.GREEN}You Can Change Auto Restart After Deploy Feature, From Runflare.com")
        if restart_value:
            Requester("PATCH", RESTART_URL.format(data[3]))
        questions = [
            inquirer.Confirm("log", message="Deployment takes time,Do you want to Watch log?"),
        ]

        questions = inquirer.prompt(questions)
        answer = questions["log"]
        if answer:
            from runflare.runflare_client.web_socket import Socket
            Socket().run_loop("watch", LOG_URL, data[3])


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