from runflare import inquirer
from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.runflare_client.service.projects import get_projects
from runflare.settings import FOLDER_NAME,DOC_URL
from colorama import init,Fore,Style
from runflare.utils import clear, check_required_files


class Cache_Manager:

    def __init__(self,root,type):
        self.root = root
        self.type = type
        self.selected_project = None
        self.selected_project_id = None
        self.selected_item = None
        self.selected_item_id = None
        self.local_db_path = self.root + f"/{FOLDER_NAME}/"


    def cache(self,y,email=None,password=None,namespace=None,app=None):
        required = True
        if not namespace and not app:
            required,data = self.get_cache(y)
        if required:
            data = self.update_cache(email,password,namespace=namespace,app=app,)
        return data



    def get_cache(self,y):
        status,data = Adapter.get_project_cache(self.local_db_path)

        if status == 3:
            if not y:
                questions = [
                    inquirer.Confirm("cache", message='Do you want to {} {}?'.format(self.type,data[0])),
                ]
                questions = inquirer.prompt(questions)
                if not questions:
                    exit()
                answer = questions['cache']
                if answer:
                    return False, self.update_item(data)
                else:
                    pass
            else:
                pass
        if status:
            try:
                self.selected_project,self.selected_project_id, self.selected_item, self.selected_item_id = data
            except:
                self.selected_project,self.selected_project_id = data
            if not y:
                if self.type == "Watch Events":
                    questions = [
                        inquirer.Confirm("cache", message='Do you want to Watch Events of {} ?'.format(self.selected_project)),
                    ]
                else:
                    questions = [
                        inquirer.Confirm("cache",
                                         message='Do you want to {} {} -> {} ?'.format(self.type, self.selected_project, self.selected_item)),
                    ]
                questions = inquirer.prompt(questions)
                if not questions:
                    exit()
                answer = questions['cache']
                if answer:
                    status = False
            if y:
                status = False
        else:
            return True,data
        return status,data

    def save_cache(self,project,project_id,service,service_id):
        Adapter.save_project_cache(self.local_db_path,project,project_id,service,service_id)


    def update_item(self,data):
        status, response = get_projects(data[1])
        if status:
            items = response.json()
            service = items.get("service", [])
            if self.type != "Deploy":
                database = items.get("database", [])

        else:
            return response
        if self.type != "Watch Events":
            if self.type != "Deploy":
                item_type_prompt = [
                    inquirer.List(
                        "item_type",
                        message='Services or Databases?',
                        choices=['Service', 'Database'],
                    ),
                ]
                answer = inquirer.prompt(item_type_prompt)
                if not answer:
                    exit()
                selected_item_type = answer["item_type"]
            else:
                selected_item_type = "Service"
            choices = []
            item_info = dict()
            if selected_item_type == "Service":
                if service:
                    for item in service:
                        choices.append(item["name"])
                        item_info[item["name"]] = item["id"]

                else:
                    print(Fore.RED + "This Project doesn't have any `Service`")
                    exit()

            elif selected_item_type == "Database":
                if database:
                    for item in database:
                        choices.append(item["name"])
                        item_info[item["name"]] = item["id"]
                else:
                    print(Fore.RED + "This Project doesn't have any `Database`")
                    exit()

            services_prompt = [
                inquirer.List(
                    "service",
                    message='Select an item?',
                    choices=choices,
                ),
            ]
            print()
            answer = inquirer.prompt(services_prompt)
            if not answer:
                exit()
            selected_service = answer["service"]
            selected_service_id = item_info[selected_service]
        else:
            selected_service = None
            selected_service_id = None
        self.save_cache(data[0], data[1], selected_service, selected_service_id)
        return data[0], data[1], selected_service, selected_service_id

    def update_cache(self,email=None,password=None,namespace=None,app=None):
        required_files = []
        status, response = get_projects(email=email,password=password)
        if status:
            projects = response.json()
        else:
            return Fore.RED + response

        if not projects:
            return Fore.RED + "Go To Runflare and Create Project First"

        choices = []

        for project in projects:
            choices.append(project["namespace"])

        if not namespace:
            projects_prompt = [
                inquirer.List(
                    "project",
                    message='Select a project?',
                    choices=choices,
                )]
            clear()
            answer = inquirer.prompt(projects_prompt)
            if not answer:
                exit()
            selected_project = answer["project"]
        else:
            selected_project = namespace

        for project in projects:
            if project["namespace"] == selected_project:
                selected_project_id = project["id"]
                items = project.get("items")
                service = items.get("service", [])
                if self.type != "Deploy":
                    database = items.get("database", [])

        if self.type != "Watch Events":

            if self.type != "Deploy":
                item_type_prompt = [
                    inquirer.List(
                        "item_type",
                        message='Services or Databases?',
                        choices=['Service', 'Database'],
                    )]
                answer = inquirer.prompt(item_type_prompt)
                if not answer:
                    exit()
                selected_item_type = answer["item_type"]
            else:
                selected_item_type = "Service"
            choices = []
            not_active = []
            item_info = dict()
            if selected_item_type == "Service":
                if service:
                    for item in service:
                        if item.get("status") != "ACTIVE":
                            not_active.append(item["name"])
                        choices.append(item["name"])
                        item_info[item["name"]] = {}
                        item_info[item["name"]]["id"] = item["id"]
                        item_info[item["name"]]["required_files"] = item["required_files"]

                else:
                    print(Fore.RED + "Selected Project doesn't have any `Service`")
                    print(Fore.RED + f"For more help please visit {DOC_URL}")
                    exit()

            elif selected_item_type == "Database":
                if database:
                    for item in database:
                        if item.get("status") != "ACTIVE":
                            not_active.append(item["name"])
                        choices.append(item["name"])
                        item_info[item["name"]] = item["id"]
                else:
                    print(Fore.RED + "This Project doesn't have any `Database`")
                    print(Fore.RED + f"For more help please visit {DOC_URL}")
                    exit()
            if not app:
                services_prompt = [
                    inquirer.List(
                        "service",
                        message='Select an item?',
                        choices=choices,
                    )]
                print()
                answer = inquirer.prompt(services_prompt)
                if not answer:
                    exit()
                selected_service = answer["service"]

                if selected_service in not_active:
                    if self.type != "Deploy":
                        print(Fore.RED + f"{selected_service} is not active")
                        print(Fore.RED + f"For more help please visit {DOC_URL}")
                        exit()

            else:
                selected_service = app
            selected_service_id = item_info[selected_service].get("id")
            required_files = item_info[selected_service].get("required_files")
        else:
            selected_service = None
            selected_service_id = None

        ok, files = check_required_files(required_files)

        if not ok:
            print(Fore.RED + f"For Your App You Must Have These Files/Directory!")
            for f in files:
                print(Fore.RED + f"  {f}")
            exit()

        self.save_cache(selected_project, selected_project_id, selected_service, selected_service_id)
        return selected_project, selected_project_id, selected_service, selected_service_id


