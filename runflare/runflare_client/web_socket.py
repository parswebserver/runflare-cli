import asyncio
import json
import sys
import time
import ssl
from colorama import init, Fore,Style
import websockets

from runflare.runflare_client.deploy.upload import cancel_deploy
from runflare.settings import WEBSOCKET_URL
from runflare.runflare_client.data_manager.adapter import Adapter
from runflare.utils import clear
import time
class Socket:

    async def watch(self,url,id,image_id=None):

        if url == "client-stream":
            socket_url = WEBSOCKET_URL + "/{}/?token={}".format(url, self._get_token())
        else:
            clear()
            print(Style.BRIGHT + "Initialize Secure Session")
            time.sleep(6)
            socket_url = WEBSOCKET_URL + "/{}/{}/?token={}".format(url,id, self._get_token())
        try:
            ssl_context = ssl.SSLContext()
            ssl_context.verify_mode = ssl.CERT_NONE
            ssl_context.check_hostname = False
            async with websockets.connect(socket_url) as ws:
            # async with websockets.connect(socket_url,ssl=ssl_context) as ws:
                if url != "client-stream":
                    print(Fore.GREEN + Style.BRIGHT + "Connected")
                else:
                    inp = {
                        "required_type": "k8s_deploy_log",
                        "item_id": id,
                        "image_id": image_id,
                        "client": "cli",
                    }
                    d = json.dumps(inp)
                    await ws.send(d)
                while True:
                    msg = await ws.recv()
                    if "401-unauthorized" in msg:
                        return "401-unauthorized"
                    else:
                        if url == "client-stream":
                            decoded_json_msg = json.loads(msg)
                            t = decoded_json_msg.get("type")
                            data = decoded_json_msg.get("data")
                            if t == "k8s_deploy_log":
                                sys.stdout.write(data)
                            elif t == "k8s_image_status":
                                status = data.get("status")
                                chagned_status_image_id = data.get("image_id")
                                if image_id == chagned_status_image_id:
                                    return "green" if status=="CP" else "red"
                        else:
                            print(msg)
        except Exception as e:
            print(Fore.BLUE + "-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_")
            print(Fore.RED + Style.BRIGHT + "Error On Connecting")
            print(Fore.RED + Style.BRIGHT + str(e))
            print(Fore.RED + Style.BRIGHT + "Send Ticket To Runflare Support")
            exit()


    async def interactive(self, url,id):
        print(Style.BRIGHT + "Initialize Secure Session")
        url = WEBSOCKET_URL + "/{}/{}/?token={}".format(url,id, self._get_token())
        try:
            ssl_context = ssl.SSLContext()
            ssl_context.verify_mode = ssl.CERT_NONE
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

    def run_loop(self,type,url,id=None,cancelable=False,log_identifier=False,image_id=None):
        try:
            if type == "watch":
                res = asyncio.get_event_loop().run_until_complete(self.watch(url,id,image_id))
                if res == "401-unauthorized":
                    from runflare.runflare_client.account import save_token
                    save_token()
                    asyncio.get_event_loop().run_until_complete(self.watch(url, id,image_id))
            elif type == "interactive":
                asyncio.get_event_loop().run_until_complete(self.interactive(url, id))
        except KeyboardInterrupt:
            if cancelable:
                response = cancel_deploy(data={"log_identifier": log_identifier})
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