import json
import os
import shutil
from time import sleep
from runflare import inquirer
import requests

from runflare.runflare_client.requester import Requester

from runflare.runflare_client.data_manager.adapter import Adapter
from pprint import pprint
from runflare.runflare_client.service.projects import get_projects
from colorama import Fore, Style, init
from runflare.utils import clear, compare, make_tar, list_to_dict, makedirs
from .cache import Cache_Manager
from .upload import upload, pre_upload_check, uploader_info,cancel_deploy
import platform
from runflare.runflare_client.service.manage import restart
from ...settings import FOLDER_NAME, TAR_NAME, CHANGES_NAME, MAX_TRY, USER_HOME_PATH, LOG_URL
import sys
from halo import Halo


def deploy(y,email=None,password=None,namespace=None,app=None):
    try:
        log_identifier = None
        project_root = Adapter.get_project_root()
        clear()
        cache_object = Cache_Manager(project_root, type="Deploy")
        data = cache_object.cache(y,email=email,password=password,namespace=namespace,app=app)
        selected_project, selected_service, selected_service_id = data[1], data[2], data[3]

        new, changed, deleted, _ = compare(project_root, send_all_files=False)
        any_change = any((new,changed,deleted))
        try_num = 1
        sp = Halo(text=Style.BRIGHT + f"Checking Upload Conditions", color="magenta")
        sp.start()
        has_another_deploy = False
        image_id = 0
        while try_num <= MAX_TRY:
            status, response = uploader_info(selected_project,selected_service_id, any_change=any_change, spinner=sp)
            if not status:
                response = response.json().get("message")
            if "Another Deploy is In Progress" in response:
                has_another_deploy = True
                break
            if "401" in response:
                return "\n" + Fore.RED + response
            if status:
                break
            try_num += 1
            sleep(2)
        if not has_another_deploy and not status:
            return "\n" + Fore.RED + response
        sp.stop()
        if not has_another_deploy:
            sys.stdout.write(f"\r √  Upload Conditions Verified\n")

            url = response.json().get("url")
            url_mirror = response.json().get("url_mirror")
            token = response.json().get("token")
            free_disk = response.json().get("free_disk")
            restart_value = response.json().get("restart")
            log_identifier = response.json().get("log_identifier")
            send_all_files = response.json().get("send_all_files")
            image_id = response.json().get("image_id")

            if send_all_files:
                sp = Halo(text=Style.BRIGHT + f"Scaning All Directory {project_root}", color="magenta")
            else:
                sp = Halo(text=Style.BRIGHT + f"Scaning Directory {project_root}", color="magenta")
            sp.start()
            new, changed, deleted, scaned_files = compare(project_root,send_all_files=send_all_files)
            sp.stop()
            space = " " * len(project_root)
            sys.stdout.write(f"\r √  Scaned {scaned_files} item(s)    {space}\n")


            if not new and not deleted and not changed:
                print(Fore.RED + "No New Files\nDirectory already synced with server !")
                exit()

            compressed = False
            for uploader_url in [url, url_mirror]:

                if not uploader_url:
                    continue

                status, response = pre_upload_check(uploader_url, token)
                if not status:
                    return Fore.RED + response

                if not compressed:
                    makedirs(project_root + f"/{FOLDER_NAME}/")
                    changes_file_path = project_root + f"/{FOLDER_NAME}/{CHANGES_NAME}"
                    with open(changes_file_path, "w+") as changes:
                        changes.write(json.dumps({
                            "new": list_to_dict(new),
                            "count_of_new": len(new),
                            "modify": list_to_dict(changed),
                            "count_of_modify": len(changed),
                            "delete": list_to_dict(deleted),
                            "count_of_delete": len(deleted),
                            "log_identifier": log_identifier,
                        }, indent=4))
                    number_of_files = len(changed) + len(new)
                    sp = Halo(text=Style.BRIGHT + f"Compressing 0 of {number_of_files} item(s)", color="magenta")
                    sp.start()
                    i = 0
                    for i in make_tar(project_root, changed, new, changes_file_path=changes_file_path):
                        sp.text = (Style.BRIGHT + f"Compressing {str(i)} of {number_of_files} items")
                    sp.stop()
                    space = " " * len(str(number_of_files) + str(i))
                    sys.stdout.write(f"\r √  {number_of_files} item(s) Compressed  {space}\n")

                    size = os.path.getsize(project_root + f"/{FOLDER_NAME}/{TAR_NAME}") / 1048576
                    if free_disk < size:
                        print(Fore.RED + Style.BRIGHT + "Not Enough Disk,Please Upgrade Your Plan")
                        exit()
                    compressed = True

                color = upload(project_root, uploader_url, token)

                if color == "green":
                    color = Fore.GREEN
                    break
                else:
                    color = Fore.RED
        else:
            print(f"\n{Fore.RED} Another Deploy is In progress you are watching its logs!\n")

        from runflare.runflare_client.web_socket import Socket
        Socket().run_loop("watch", "client-stream", id=data[3],cancelable=True,log_identifier=log_identifier,image_id=image_id)

        if has_another_deploy:
            return Fore.GREEN + ""
        elif status:
            Adapter.save_last_deploy(project_root + f"/{FOLDER_NAME}/")
            os.remove(project_root + f"/{FOLDER_NAME}/{TAR_NAME}")
            os.remove(project_root + f"/{FOLDER_NAME}/{CHANGES_NAME}")
            if color == Fore.GREEN:
                result = "\n\n {}Files Successfully Uploaded {:.3f} MB".format(color + Style.BRIGHT, size)
                result += "\n\n  Scaned Files :{} \n   {}New Files :{} \n   Changed Files :{} \n   Deleted Files :{}\n".format(
                    scaned_files, color, len(new), len(changed), len(deleted))
                print(result)
                action = "ON" if restart_value else "OFF"
                print(f"{color}Auto Restart is {action}")
                print(f"{color}You Can Change Auto Restart After Deploy, From Runflare.com")
                if not email and not password and not namespace and not app:
                    questions = [
                        inquirer.Confirm("log", message="Deployment takes time,Do you want to Watch log?"),
                    ]

                    questions = inquirer.prompt(questions)
                    answer = questions["log"]
                    if answer:
                        from runflare.runflare_client.web_socket import Socket
                        print("Your Files Successfully uploaded To Server.")
                        sleep(6)
                        print("New Version will be replaced soon ...")
                        sleep(6)
                        print("Trying to watch logs ...")
                        sleep(6)
                        Socket().run_loop("watch", LOG_URL, data[3])
            return
        else:
            return Fore.RED + response
    except KeyboardInterrupt:
        if log_identifier:
            response = cancel_deploy(data={"log_identifier": log_identifier})
        print(Fore.RED + Style.BRIGHT + f"\n\n X  ERORR - Cancelled By User")
        exit()


def reset():
    status, roots = Adapter.get_roots()
    if not status:
        return Fore.RED + "Deploy root not Found"
    root_lst = []
    for i, root in roots:
        root_lst.append(root)

    questions = [
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
    status, roots = Adapter.get_roots()
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
        main_root = str(USER_HOME_PATH) + f"/{FOLDER_NAME}/"
        shutil.rmtree(main_root)
        print(Fore.GREEN + "Successfully Cleaned")
    else:
        print(Fore.RED + "Choose Carefully")

