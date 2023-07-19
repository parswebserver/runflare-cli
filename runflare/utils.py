import fnmatch
import os
import tarfile
import hashlib
from runflare.gitignore_parser import parse_gitignore
from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.settings import FOLDER_NAME, TAR_NAME,DATASTORE,DEFAULT_IGNORE_FILE
from colorama import Style

from pathlib import Path
import copy
import pathspec
import time

def makedirs(path):
    os.makedirs(path,exist_ok=True)


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def get_current_path():
    return os.getcwd()

def get_text_hash(text):
    result = hashlib.sha1(text.encode())
    return result.hexdigest()




def save_current_dir(root_path,spec,send_all_files=False):
    conn = Adapter.create_connection(root_path + f"/{FOLDER_NAME}/",DATASTORE.get("NAME"))
    Adapter.drop_table(conn,"Current_Dir")
    Adapter.create_table(conn,"Current_Dir", path="VARCHAR(255)",type="VARCHAR(255)",sha="VARCHAR(255)",path2="VARCHAR(255)")
    if send_all_files:
        Adapter.drop_table(conn, "last_deploy")
    for path, subdirs, files in os.walk(root_path):
        matches = spec.match_files(subdirs)

        for pattern_matched in matches:
            subdirs.remove(pattern_matched)
        matches = spec.match_files(files)
        for pattern_matched in matches:
            files.remove(pattern_matched)

        for file in files:
            file_path = os.path.join(path, file).replace(root_path, ".")
            abs_file_path = os.path.join(path, file)
            status = os.stat(abs_file_path)
            Adapter.insert_into(conn,"Current_Dir",path=file_path, type="file",sha=get_text_hash(str(abs_file_path) + str(status.st_size) + str(status.st_ctime) + str(status.st_mtime)), path2=file_path.replace(".\\", "").replace("\\", "/"))

        for subdir in subdirs:
            dir_path = os.path.join(path, subdir).replace(root_path, ".")
            abs_dir_path = os.path.join(path, subdir)
            status = os.stat(abs_dir_path)
            Adapter.insert_into(conn,"Current_Dir",path=dir_path, type="folder",sha=get_text_hash(str(abs_dir_path) + str(status.st_size) + str(status.st_ctime) + str(status.st_mtime)), path2=dir_path.replace(".\\", "").replace("\\", "/"))

    file_number = Adapter.execute(conn,'SELECT Count(*) FROM Current_Dir;')
    Adapter.close_connection(conn)
    return file_number[0][0]






def compare(project_root,send_all_files=False):
    ignore_path = get_ignore_path(project_root)
    fh = open(ignore_path, 'r')
    spec = pathspec.PathSpec.from_lines('gitwildmatch', fh)
    file_number = save_current_dir(project_root,spec,send_all_files)
    new,change,delete = Adapter.compare(project_root + f"/{FOLDER_NAME}/")
    tmp = copy.copy(delete)
    items = [x[0] for x in delete]
    matches = spec.match_files(items)
    for pattern_matched in matches:
        try:
            tmp.remove((pattern_matched,"file"))
        except:
            try:
                tmp.remove((pattern_matched,"folder"))
            except:
                pass
    fh.close()
    return new,change,tmp,file_number

def set_file_permissions(tarinfo):
    try:
        perm = str(oct(tarinfo.mode))[-4:]
        if perm == "0666":
            tarinfo.mode = 0o644
    except:
        pass
    return tarinfo

def add_changes_file_path(tarinfo):
    try:
        perm = str(oct(tarinfo.mode))[-4:]
        if perm == "0666":
            tarinfo.mode = 0o644
    except:
        pass
    return tarinfo



def make_tar(project_root,changed, new,changes_file_path=None):
    with tarfile.open(project_root + f"/{FOLDER_NAME}/{TAR_NAME}", "w:gz") as tar:
        os.chdir(project_root)
        if changes_file_path:
            change_path = os.path.relpath(changes_file_path, start = project_root)
            tar.add(change_path, filter=set_file_permissions)
        i = 0
        for name in changed:
            tar.add(name[0])
            i += 1
            yield i
        for item in new:
            if item[1] == "file":
                tar.add(item[0], filter=set_file_permissions)
            else:
                t = tarfile.TarInfo(item[0])
                t.type = tarfile.DIRTYPE
                status = os.stat(item[0])
                t.mode = status.st_mode
                try:
                    perm = str(oct(status.st_mode))[-4:]
                    if perm == "0777":
                        t.mode = 0o755
                except:
                    t.mode = status.st_mode
                t.mtime = status.st_mtime
                t.gid = status.st_gid
                t.uid = status.st_uid
                tar.addfile(t)
            i += 1
            yield i

def list_to_dict(data):
    lst = []
    for item in data:
        lst.append({
            "path2": item[0],
        })
    return lst

def command_help(command, **kwargs):
    for key, value in kwargs.items():
        clear()
        print("runflare {} <option>\n\nOPTIONS".format(command))
        print("\t-{},--{} \t\t {}".format(key, key, value))

def get_ignore_path(project_root):
    if not os.path.exists(project_root + "/.gitignore"):
        full_path = str(Path(__file__).resolve().parent / ".runflare_ignore")
    else:
        full_path = project_root + "/.gitignore"
        with open(full_path, "r+") as default_ignored:
            lst = list(map(lambda x: x.strip("\n"), default_ignored.readlines()))
            for item in DEFAULT_IGNORE_FILE:
                if item not in lst:
                    default_ignored.write(f"\n{item}")
    return full_path

def check_required_files(required_files):
    not_exists = []
    for f in required_files:
        if not os.path.exists(f):
            not_exists.append(f)
    if not_exists:
        return False, not_exists
    return True, []
