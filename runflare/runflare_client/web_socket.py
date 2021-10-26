import asyncio
import json
import time
import ssl
from colorama import init, Fore,Style
import websockets
from runflare.settings import WEBSOCKET_URL
from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.utils import clear
class Socket:

    async def watch(self,url,id):
        clear()
        print(Style.BRIGHT + "Intialize Secure Session")
        url = WEBSOCKET_URL + "/ws/{}/{}/?token={}".format(url,id, self._get_token())
        try:
            ssl_context = ssl.SSLContext()
            ssl_context.verify_mode = ssl.CERT_NONE
            # ssl_context.check_hostname = False
            async with websockets.connect(url,ssl=ssl_context) as ws:
                print(Fore.GREEN + Style.BRIGHT + "Connected")
                # while ws.wait_closed():
                while True:
                    msg = await ws.recv()
                    print(msg)
                    # msg = json.loads(msg)
                    # message = msg["message"]
                    # error = msg["error"]
                    # output = "{}".format(message)
                    # if output != "" and not error:
                    #     print(Style.BRIGHT + output.rstrip("\n"))
                    # elif error == 1:
                    #     print(Fore.RED + Style.BRIGHT + message.rstrip("\n"))
                    #     exit()
                    # elif error == 2:
                    #     print(Fore.RED + Style.BRIGHT + message.rstrip("\n"))
        except Exception as e:
            print(Fore.BLUE + "-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_")
            print(Fore.RED + Style.BRIGHT + "Error On Connecting")
            print(Fore.RED + Style.BRIGHT + str(e))
            print(Fore.RED + Style.BRIGHT + "Send Ticket To Runflare Support")
            exit()


    async def interactive(self, url,id):
        print(Style.BRIGHT + "Intialize Secure Session")
        url = WEBSOCKET_URL + "/ws/{}/{}/?token={}".format(url,id, self._get_token())
        try:
            ssl_context = ssl.SSLContext()
            ssl_context.verify_mode = ssl.CERT_NONE
            print(url)
            async with websockets.connect(url,ssl=ssl_context) as ws:
                print(Fore.GREEN + Style.BRIGHT + "Connected")
                print(Fore.BLUE + Style.BRIGHT + "Enter exit or exit() to quit")
                await ws.send("pwd")
                pwd = (json.loads(await ws.recv())["message"]).rstrip("\n")
                while ws.wait_closed:
                    inp = input(f"[{pwd}]# ")
                    if inp.lower() == "exit()" or inp.lower() == "exit":
                        print()
                        print(Fore.BLUE + "-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_")
                        print(Style.BRIGHT + "EXIT, CODE 0")
                        print(Style.BRIGHT + "more help on runflare --help")
                        exit()
                    await ws.send(inp)
                    rc = await ws.recv()
                    rc = json.loads(rc)
                    message = rc["message"]
                    error = rc["error"]
                    output = "{}".format(message)
                    if output != "" and not error:
                        print(Style.BRIGHT + output.rstrip("\n"))
                    elif error == 1:
                        print(Fore.RED + Style.BRIGHT + message.rstrip("\n"))
                        exit()
                    elif error == 2:
                        print(Fore.RED + Style.BRIGHT + message.rstrip("\n"))
                    await ws.send("pwd")
                    pwd = (json.loads(await ws.recv())["message"]).rstrip("\n")
        except Exception as e:
            print(Fore.BLUE + "-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_")
            print(Fore.RED + Style.BRIGHT + "Error On Connecting")
            print(Fore.RED + Style.BRIGHT + str(e))
            print(Fore.RED + Style.BRIGHT + "Send Ticket To Runflare Support")
            exit()

    def run_loop(self,type,url,id):
        try:
            if type == "watch":
                print(id)
                asyncio.get_event_loop().run_until_complete(self.watch(url,id))
            elif type == "interactive":
                asyncio.get_event_loop().run_until_complete(self.interactive(url, id))

        except KeyboardInterrupt:
            print()
            print(Fore.BLUE + "-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_")
            print(Style.BRIGHT + "EXIT, CODE 0")
            print(Style.BRIGHT + "more help on runflare --help")
            exit()


    def _get_token(self):
        status, message = Adapter.get_token()
        if status:
            return message
        return None