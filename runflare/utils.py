import fnmatch
import os
import tarfile
import hashlib
from runflare.gitignore_parser import parse_gitignore
from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.settings import FOLDER_NAME, TAR_NAME,DATASTORE,DEFAULT_IGNORE_FILE
from colorama import Style
from halo import Halo
from pathlib import Path
import copy


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

@Halo(text=Style.BRIGHT + "Scaning Directory", color="magenta")
def save_current_dir(root_path,file_exclude,folder_exclude):
    conn = Adapter.create_connection(root_path + f"/{FOLDER_NAME}/",DATASTORE.get("NAME"))
    Adapter.drop_table(conn,"Current_Dir")
    Adapter.create_table(conn,"Current_Dir", path="VARCHAR(255)",type="VARCHAR(255)",sha="VARCHAR(255)",path2="VARCHAR(255)")
    for path, subdirs, files in os.walk(root_path):
        subdirs[:] = [d for d in subdirs if d not in folder_exclude]
        for file in files:
            is_ignored = False
            for e in file_exclude:
                if fnmatch.fnmatch(file, e):
                    is_ignored = True
                    break
            if not is_ignored:
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

def compare(project_root):
    file_exclude, folder_exclude = get_ignore(project_root)
    file_number = save_current_dir(project_root,file_exclude, folder_exclude)
    new,change,delete = Adapter.compare(project_root + f"/{FOLDER_NAME}/")

    tmp = copy.copy(delete)
    for e in file_exclude:
        for item in delete:
            if "/" in item[0]:
                name = item[0].split("/")[-1]
            else:
                name = item[0]
            if item[1] == 'file' and fnmatch.fnmatch(name, e):
                tmp.remove(item)
    for e in folder_exclude:
        for item in delete:
            if item[1] == 'folder' and e in item[0]:
                tmp.remove(item)
    return new,change,tmp,file_number


def make_tar(project_root,changed, new):
    with tarfile.open(project_root + f"/{FOLDER_NAME}/{TAR_NAME}", "w:gz") as tar:
        os.chdir(project_root)
        for name in changed:
            tar.add(name[0])
        for item in new:
            if item[1] == "file":
                tar.add(item[0])
            else:
                t = tarfile.TarInfo(item[0])
                t.type = tarfile.DIRTYPE
                status = os.stat(item[0])
                t.mtime = status.st_mtime
                t.gid = status.st_gid
                t.uid = status.st_uid
                tar.addfile(t)

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

def stripn(n):
    n = n.strip("\n")
    if not n.startswith("#"):
        return n

def ignore_parser(ig_list):
    lst = set(map(stripn,ig_list))
    file = []
    folder = []
    for i in lst:
        if i:
            if i.endswith("/"):
                if not "*" in i:
                    folder.append(i.rstrip("/"))
            else:
                file.append(i)

    return file,folder

def get_ignore(project_root):
    if not os.path.exists(project_root + "/.gitignore"):
        full_path = str(Path(__file__).resolve().parent / ".runflare_ignore")
    else:
        full_path = project_root + "/.gitignore"
        with open(full_path, "r+") as default_ignored:
            lst = list(map(lambda x: x.strip("\n"),default_ignored.readlines()))
            for item in DEFAULT_IGNORE_FILE:
                if item not in lst:
                    default_ignored.write(f"{item}\n")

    with open(full_path) as ignored:
        ig = ignored.readlines()
    return ignore_parser(ig)