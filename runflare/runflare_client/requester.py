import urllib
import requests
from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.settings import BASE_URL
from colorama import init, Fore

class Requester:

    def __init__(self,method,path,abs=False,**kwargs):

        assert method in ["HEAD", "GET", "POST", "PATCH", "PUT", "DELETE"],(f"{path} method is not allowed")
        assert path is not None,("Enter a valid Path")

        if not "headers" in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Authorization"] = f"Token {self._get_token()}"
        if not abs:
            url = BASE_URL + path
        else:
            url = path
        try:
            self.response = requests.request(method,url,**kwargs)
        except Exception as e:
            print()
            print(Fore.RED + "Error in Making Request")
            print(Fore.RED + f"Detail : {str(e)}")
            exit()

    def __check(self):
        if self.response.status_code != 200:
            return False,self.__Return_Error()
        self.json_data = self.response.json()
        if isinstance(self.json_data,dict):
            self.error_code = self.json_data.get("error",0)
            if self.error_code:
                return False, self.json_data.get("message")
        return True,self.response


    def __Return_Error(self):
        if self.response.status_code == 401:
            return Fore.RED + f"(401) - Please Login To Your Runflare Account"
        if self.response.status_code == 400:
            return Fore.RED + f"(400) - Please Contact Support"
        if self.response.status_code == 500:
            return Fore.RED + f"(500) - Please Contact Support"
        else:
            return Fore.RED + f"({self.response.status_code}) - Invalid Request"


    def _get_token(self):
        status, message = Adapter.get_token()
        if status:
            return message
        return None


    @property
    def get_response(self):
        return self.__check()

