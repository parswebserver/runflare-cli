from runflare.runflare_client.data_manager.adapter import Adapter

from runflare.runflare_client.requester import Requester
from runflare.settings import UPLOAD_URL, FOLDER_NAME, TAR_NAME, CHANGES_NAME
from requests_toolbelt.multipart import encoder
from colorama import Style
from halo import Halo


@Halo(text=Style.BRIGHT + "Uploading Files To Server...", color="magenta")
def upload(project_root,url,token):
    with open(project_root + f"/{FOLDER_NAME}/{TAR_NAME}", 'rb') as tar_file:
        with open(project_root + f"/{FOLDER_NAME}/{CHANGES_NAME}", 'rb') as change:
            form = encoder.MultipartEncoder({
                'files': ('workspace.tar', tar_file, "application/octet-stream"),
                'changes': (CHANGES_NAME, change,'application/json'),
            })

            request = Requester("POST", url, data=form,abs=True,headers={"Content-Type": form.content_type,'token':token})

    return request.get_response

def uploader_info(item_id):
    request = Requester("POST", UPLOAD_URL.format(item_id))
    return request.get_response

def pre_upload_check(url,token):
    request = Requester("GET", url, headers={'token':token},abs=True)
    return request.get_response