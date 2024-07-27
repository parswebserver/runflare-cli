from runflare.runflare_client.data_manager.adapter import Adapter

from runflare.runflare_client.requester import Requester
from runflare import VERSION
from runflare.settings import UPLOAD_URL, FOLDER_NAME, TAR_NAME, CHANGES_NAME,CANCEL_DEPLOY_URL
from requests_toolbelt.multipart import encoder
from colorama import Fore, Style
from halo import Halo
import requests
import os
import sys
import time
import json
import platform
import datetime
from runflare.utils import clear

def upload(project_root,url,token):
    color = "green"
    with open(project_root + f"/{FOLDER_NAME}/{TAR_NAME}", 'rb') as tar_file:
        file_path = project_root + f"/{FOLDER_NAME}/{TAR_NAME}"
        content_path = os.path.abspath(file_path)
        content_size = os.stat(content_path).st_size
        CHUNK_SIZE = 102400

        headers = {
            'token': token,
        }
        def print_the_box(text):
            sys.stdout.write(text)

        def read_in_chunks(file_object, CHUNK_SIZE):
            transfered = 0
            time_start = time.time()
            while True:
                secs = time.time() - time_start or 0.00000001
                speed = round((transfered/1024.0**2) / secs,3)
                per = round(transfered /content_size * 100,2)
                cp = int(per//2)
                block = cp * "="
                space = (50 - cp) * ' '
                print_the_box(f'\r    Uploading [{block}{space}] {per}% ({speed} Mbp/s)')
                data = file_object.read(CHUNK_SIZE)
                if not data:
                    break
                yield data
                transfered += len(data)
            space = 70 * ' '
            print_the_box(f'\r √  Uploaded ({speed} Mbp/s){space}\n')
        try:
            r = requests.post(url,headers=headers,stream=True, data=read_in_chunks(tar_file, CHUNK_SIZE))
        except requests.exceptions.ConnectionError as e:
            print(Fore.RED + Style.BRIGHT + f"\n\n X  ERORR - Connection Closed, You may have another in progress deploy")
            exit()


        word = ""
        try:
            for letter in r.iter_content(1, decode_unicode=True):
                if letter != ";":
                    word += letter
                else:

                    if word.startswith("{") and word.endswith("}"):
                            res = json.loads(word)
                            msg = res.get("message",None)
                            type_res = res.get("type",None)
                            error = res.get("error",None)
                            color = res.get("color","green")
                            if error:
                                print(Fore.RED + Style.BRIGHT + f"\n X  ERORR - {msg}")
                                exit()
                            start = True if type_res == "start" else False
                            if start:
                                spinner = Halo(msg, color="magenta")
                                spinner.start()
                            else:
                                spinner.stop()
                                print(msg)
                    word = ""
        except json.decoder.JSONDecodeError as e:
            print(word)
            exit()
        except requests.exceptions.ChunkedEncodingError as e:
            print(Fore.RED + Style.BRIGHT + f"\n X  ERORR - Connection Closed, Please Deploy Again")
            exit()
        except Exception as e:
            print(type(e))
            print(e)
            exit()

    return color


def uploader_info(project_id,item_id,any_change=True,spinner=None):
    try:
        operating_system = platform.platform()
    except:
        operating_system = None
    try:
        device_name = platform.node()
    except:
        device_name = None
    data = {
        "operating_system" : operating_system,
        "device_name" : device_name,
        "cli_version" : VERSION,
        "any_change" : any_change,
    }
    request = Requester("POST", UPLOAD_URL.format(project_id,item_id), data=data, spinner=spinner,return_extra_response=True)

    return request.get_response


def pre_upload_check(url, token):
    request = Requester("GET", url, headers={'token': token}, abs=True)
    return request.get_response

def cancel_deploy(data):
    for _ in range(3):
        try:
            request = Requester("POST", CANCEL_DEPLOY_URL, data=data)
            return request.get_response
        except:
            continue