from PyInquirer import prompt,style_from_dict,Token
from runflare.utils import clear
from runflare.runflare_client.requester import Requester
from runflare.settings import LOGIN_URL
from runflare.runflare_client.data_manager.adapter import Adapter

from colorama import Fore, Style


def save_token():
    clear()
    credentials = [
        {
            'type': 'input',
            'name': 'email',
            'message': 'Please enter your email > ',

        },
        {
            'type': 'password',
            'name': 'password',
            'message': 'Please enter your password > ',

        },
    ]

    credentials = prompt(credentials)
    email = credentials['email']
    password = credentials['password']
    data = {'email': email, 'password': password}

    request = Requester("POST",LOGIN_URL,data=data)
    status,response = request.get_response
    if status:
        token = response.json().get("token",None)
        Adapter.save_token(token=token, email=email)
        return Fore.GREEN + " Successfully Logged In"
    else:
        return Fore.RED + " Wrong Credentials"

def del_token():
    clear()
    questions = [
        {
            'type': 'confirm',
            'name': 'exit',
            'message': 'Do you want to exit?',
            'default': True,
        }]
    questions = prompt(questions)
    answer = questions['exit']
    if answer:
        status, message = Adapter.del_token()
        if status:
            return Fore.GREEN + message
        return Fore.RED + message
    else:
        return Fore.RED + "Choose Carefully"
