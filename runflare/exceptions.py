from colorama import init, Fore
init()


class RunflareException(Exception):
    pass



class Unauthorized_Exception(RunflareException):

    def __str__(self):
        return Fore.RED + "You'r Not Logged in"

class Server_Exception(RunflareException):
    pass


class Message_Exception(RunflareException):

    def __init__(self,message,status):
        super().__init__()
        self.__message = message
        self.__status = status

    def __str__(self):
        return "{status} {message}".format(status=self.__status, message=self.__message)



class Unknown_Exception():
    def __str__(self):
        return Fore.RED + "You'r Unknown_Exception"