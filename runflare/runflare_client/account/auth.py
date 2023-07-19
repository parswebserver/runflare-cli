from runflare import inquirer
from runflare.utils import clear
from runflare.runflare_client.requester import Requester
from runflare.settings import LOGIN_URL
from runflare.runflare_client.data_manager.adapter import Adapter

from colorama import Fore, Style


def save_token(email=None,password=None):
    clear()
    if not email and not password:
        credentials = [
            inquirer.Text("email", message="Please enter your email > "),
            inquirer.Password("password", message="Please enter your password > "),
        ]

        credentials = inquirer.prompt(credentials)
        if not credentials:
            exit()
        email = credentials['email']
        password = credentials['password']
    data = {'email': email, 'password': password}
    request = Requester("POST", LOGIN_URL, data=data)
    status, response = request.get_response
    if status:
        token = response.json().get("token",None)
        Adapter.save_token(token=token, email=email)
        return Fore.GREEN + " Successfully Logged In"
    else:
        print(Fore.RED + " Wrong Credentials")
        exit()

def del_token():
    clear()

    questions =[
        inquirer.Confirm("exit", message="Do you want to exit?"),
    ]

    questions = inquirer.prompt(questions)
    answer = questions['exit']
    if answer:
        status, message = Adapter.del_token()
        if status:
            return Fore.GREEN + message
        return Fore.RED + message
    else:
        return Fore.RED + "Choose Carefully"
