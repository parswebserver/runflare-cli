from runflare.runflare_client.data_manager.adapter import Adapter

from runflare.runflare_client.requester import Requester
from runflare.settings import UPLOAD_URL, FOLDER_NAME, TAR_NAME, CHANGES_NAME
from requests_toolbelt.multipart import encoder
from colorama import Style
from halo import Halo
import requests
import os
import sys
import time
import json
import datetime
from runflare.utils import clear

def upload(project_root,url,token):

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

        r = requests.post(url,headers=headers,stream=True, data=read_in_chunks(tar_file, CHUNK_SIZE))
        word = ""
        for letter in r.iter_content(1, decode_unicode=True):
            if letter != ";":
                word += letter
            else:
                if word.startswith("{") and word.endswith("}"):
                        res = json.loads(word)
                        msg = res.get("message",None)
                        type_res = res.get("type",None)
                        error = res.get("error",None)
                        if error:
                            print("ERORR")
                            exit()
                        start = True if type_res == "start" else False
                        if start:
                            spinner = Halo(msg, color="magenta")
                            spinner.start()
                        else:
                            spinner.stop()
                            print(msg)
                            # sys.stdout.write(f"\r{word}")
                word = ""



def uploader_info(item_id):
    request = Requester("POST", UPLOAD_URL.format(item_id))
    return request.get_response

def pre_upload_check(url,token):
    request = Requester("GET", url, headers={'token':token},abs=True)
    return request.get_response