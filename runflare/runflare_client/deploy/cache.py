from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.runflare_client.service.projects import get_projects, get_project_items
from runflare.settings import FOLDER_NAME
from PyInquirer import prompt,style_from_dict,Token,Separator
from colorama import init,Fore,Style
from runflare.utils import clear


class Cache_Manager:

    def __init__(self,root,type):
        self.root = root
        self.type = type
        self.selected_project = None
        self.selected_project_id = None
        self.selected_item = None
        self.selected_item_id = None
        self.local_db_path = self.root + f"/{FOLDER_NAME}/"


    def cache(self,y):
        required,data = self.get_cache(y)
        if required:
            data = self.update_cache()
        return data



    def get_cache(self,y):
        status,data = Adapter.get_project_cache(self.local_db_path)

        if status == 3:
            if not y:
                questions = [
                            {
                                'type': 'confirm',
                                'name': 'cache',
                                'message': 'Do you want to {} {}?'.format(self.type,data[0]),
                                'default': False,
                            }]
                questions = prompt(questions)
                answer = questions['cache']
                if answer:
                    return False, self.update_item(data)
                else:
                    pass
            else:
                pass
        if status:
            self.selected_project,self.selected_project_id, self.selected_item, self.selected_item_id = data
            if not y:
                if self.type == "Watch Events":
                    questions = [
                        {
                            'type': 'confirm',
                            'name': 'cache',
                            'message': 'Do you want to Watch Events of {} ?'.format(self.selected_project),
                            'default': False,
                        }]
                else:
                    questions = [
                                {
                                    'type': 'confirm',
                                    'name': 'cache',
                                    'message': 'Do you want to {} {} -> {} ?'.format(self.type, self.selected_project, self.selected_item),
                                    'default': False,
                                }]
                questions = prompt(questions)
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
        status, response = get_project_items(data[1])
        if status:
            items = response.json()
            service = items.get("service", [])
            if self.type != "Deploy":
                database = items.get("database", [])

        else:
            return response
        if self.type != "Watch Events":

            if self.type != "Deploy":
                item_type_prompt = [{
                    'type': 'list',
                    'name': 'item_type',
                    'message': 'Services or Databases?',
                    'choices': ['Service', 'Database'],
                }]
            else:
                item_type_prompt = [{
                    'type': 'list',
                    'name': 'item_type',
                    'message': 'Services?',
                    'choices': ['Service'],
                }]
            answer = prompt(item_type_prompt)
            selected_item_type = answer["item_type"]

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

            services_prompt = [{
                'type': 'list',
                'name': 'service',
                'message': 'Select an item?',
                'choices': choices
            }]
            print()
            answer = prompt(services_prompt)
            selected_service = answer["service"]
            selected_service_id = item_info[selected_service]
        else:
            selected_service = None
            selected_service_id = None
        self.save_cache(data[0], data[1], selected_service, selected_service_id)
        return data[0], data[1], selected_service, selected_service_id

    def update_cache(self):
        status, response = get_projects()
        if status:
            projects = response.json()
        else:
            return Fore.RED + response

        if not projects:
            return Fore.RED + "Go To Runflare and Create Project First"

        choices = []

        for project in projects:
            choices.append(project["namespace"])

        projects_prompt = [{
            'type': 'list',
            'name': 'project',
            'message': 'Select a project?',
            'choices': choices
        }]
        clear()
        answer = prompt(projects_prompt)
        selected_project = answer["project"]

        for project in projects:
            if project["namespace"] == selected_project:
                selected_project_id = project["id"]
                status, response = get_project_items(selected_project_id)
                if status:
                    items = response.json()
                    service = items.get("service", [])
                    if self.type != "Deploy":
                        database = items.get("database", [])

                else:
                    return response

        if self.type != "Watch Events":

            if self.type != "Deploy":
                item_type_prompt = [{
                    'type': 'list',
                    'name': 'item_type',
                    'message': 'Services or Databases?',
                    'choices': ['Service', 'Database'],
                }]
            else:
                item_type_prompt = [{
                    'type': 'list',
                    'name': 'item_type',
                    'message': 'Services?',
                    'choices': ['Service'],
                }]
            print()
            answer = prompt(item_type_prompt)
            selected_item_type = answer["item_type"]

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

            services_prompt = [{
                'type': 'list',
                'name': 'service',
                'message': 'Select an item?',
                'choices': choices
            }]
            print()
            answer = prompt(services_prompt)
            selected_service = answer["service"]
            selected_service_id = item_info[selected_service]
        else:
            selected_service = None
            selected_service_id = None
        self.save_cache(selected_project,selected_project_id,selected_service,selected_service_id)
        return selected_project,selected_project_id,selected_service,selected_service_id


