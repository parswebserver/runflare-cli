import requests
from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.settings import BASE_URL
from colorama import Fore
from runflare import inquirer

class Requester:

    def __init__(self,method,path,spinner=None,abs=False,extra=None,return_extra_response=False,**kwargs):

        assert method in ["HEAD", "GET", "POST", "PATCH", "PUT", "DELETE"],(f"{path} method is not allowed")
        assert path is not None,("Enter a valid Path")
        self.method = method
        self.return_extra_response = return_extra_response
        if not "headers" in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Token {self._get_token()}"
        if isinstance(extra,dict):
            self.extra = extra
        else:
            self.extra= {}
        self.kwargs = kwargs
        self.spinner = spinner
        if not abs:
            self.url = BASE_URL + path
        else:
            self.url = path
        try:
            self.response = requests.request(self.method,self.url,**self.kwargs)
        except Exception as e:
            print()
            print(Fore.RED + "Error in Making Request")
            print(Fore.RED + f"Detail : {str(e)}")
            exit()

    def __check(self):
        if self.response.status_code == 401:
            from runflare.runflare_client.account import save_token
            if self.spinner:
                self.spinner.stop()

            email = self.extra.get("email")
            password = self.extra.get("password")
            save_token(email,password)
            if self.spinner:
                self.spinner.start()
            self.kwargs["headers"]["Authorization"] = f"Token {self._get_token()}"
            self.response = requests.request(self.method, self.url, **self.kwargs)
            self.__check()
            if self.spinner:
                self.spinner.stop()
        elif self.response.status_code == 403:
            credentials = [
                inquirer.Text("totp", message="Please enter totp > ")
            ]
            credentials = inquirer.prompt(credentials)
            if not credentials:
                exit()
            totp = credentials['totp']
            self.kwargs["data"].update({
                "totp":totp
            })

            self.response = requests.request(self.method, self.url,**self.kwargs)
            self.__check()

        elif self.response.status_code != 200:
            return False,self.__Return_Error()
        self.json_data = self.response.json()
        if isinstance(self.json_data,dict):
            self.error_code = self.json_data.get("error",0)
            if self.error_code:
                if self.return_extra_response:
                    return False, self.response
                return False, self.json_data.get("message")
        return True,self.response


    def __Return_Error(self):
        if self.response.status_code == 400:
            print(Fore.RED + f"(400) - Please Contact Support")
            exit()
        if self.response.status_code == 500:
            print(Fore.RED + f"(500) - Please Contact Support")
            exit()
        else:
            print(Fore.RED + f"({self.response.status_code}) - Invalid Request")
            exit()



    def _get_token(self):
        status, message = Adapter.get_token()
        if status:
            return message
        return None


    @property
    def get_response(self):
        return self.__check()
