import os
import tarfile
import hashlib
from runflare.gitignore_parser import parse_gitignore
from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.settings import FOLDER_NAME, TAR_NAME
from colorama import Style



def makedirs(path):
    os.makedirs(path,exist_ok=True)


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def get_current_path():
    return os.getcwd()

def get_file_sha(file):
    sha1_hash = hashlib.sha1()
    with open(file, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha1_hash.update(byte_block)
        return sha1_hash.hexdigest()

def get_folder_name_hash(path):
    result = hashlib.sha1(path.encode())
    return result.hexdigest()

def draw_box(root_path):
    clear()
    print(f"Scaning {root_path} ...")
    print()
    print("\t✅ Added      ❌ Ignored")
    print(" ---------------------------------------------------------")
    print("| ...")


def dir_to_json(root_path):
    relative_path = os.path.relpath(root_path, ".")
    current_path = []
    matches = parse_gitignore('.gitignore',base_dir=relative_path)
    draw_box(root_path)
    counter = 0
    for path, subdirs, files in os.walk(root_path):
        is_ignored = matches(path)
        if not is_ignored:
            for file in files:
                is_ignored = matches(os.path.join(path, file))
                file_path = os.path.join(path, file).replace(root_path, ".")
                if not is_ignored:
                    abs_file_path = os.path.join(path, file)
                    current_path.append((file_path,file,"file",get_file_sha(abs_file_path),file_path.replace(".\\", "").replace("\\", "/")))
                    print(f"| ✅   {file_path}")
                    counter +=1
                    if counter == 10:
                        draw_box(root_path)
                        counter = 0
                else:
                    print(f"| ❌   {file_path}")
                    counter += 1
                    if counter == 10:
                        draw_box(root_path)
                        counter = 0
            for subdir in subdirs:
                is_ignored = matches(os.path.join(path, subdir))
                dir_path = os.path.join(path, subdir).replace(root_path, ".")
                if not is_ignored:
                    abs_dir_path = os.path.join(path, subdir)
                    current_path.append((dir_path,os.path.basename(abs_dir_path),"folder",get_folder_name_hash(abs_dir_path),dir_path.replace(".\\", "").replace("\\", "/")))
                    print(f"| ✅   {dir_path}")
                    counter += 1
                    if counter == 10:
                        draw_box(root_path)
                        counter = 0
                else:
                    print(f"| ❌   {dir_path}")
                    counter += 1
                    if counter == 10:
                        draw_box(root_path)
                        counter = 0
    print(" ---------------------------------------------------------")
    return current_path

def compare(project_root):
    files = dir_to_json(project_root)
    found,last_deploy = Adapter.get_last_deploy(project_root + f"/{FOLDER_NAME}/")
    if not found:
        return files,[],[]
    changed = []
    new = []
    deleted = []


    for new_file in files:

        flag = False
        if new_file not in last_deploy:
            for old_file in last_deploy:
                if new_file[0] == old_file[0]:
                    changed.append(new_file)
                    flag = True
                    break
            if not flag:
                new.append(new_file)

    for old in last_deploy:
        if len(changed) != 0:
            for item in changed:
                if item[0] == old[0]:
                    continue
                if old not in files:
                    deleted.append(old)
        else:
            if old not in files:
                deleted.append(old)
    return new, changed, deleted


def make_tar(project_root,changed, new):
    with tarfile.open(project_root + f"/{FOLDER_NAME}/{TAR_NAME}", "w:gz") as tar:
        os.chdir(project_root)
        for name in changed:
            tar.add(name[0])
        for item in new:
            if item[2] == "file":
                tar.add(item[0])
            else:
                t = tarfile.TarInfo(item[4])
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
            "path": item[0],
            "name": item[1],
            "type": item[2],
            "sha": item[3],
            "path2": item[4],
        })
    return lst

def command_help(command, **kwargs):
    for key, value in kwargs.items():
        clear()
        print("runflare {} <option>\n\nOPTIONS".format(command))
        print("\t-{},--{} \t\t {}".format(key, key, value))