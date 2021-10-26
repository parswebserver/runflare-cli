import fire
from .utils import clear
from runflare.runflare_client.account import save_token,del_token
from runflare.runflare_client.deploy import deploy
from runflare.runflare_client.analyze import log,events
from runflare.runflare_client.service import stop,start,restart
from runflare.utils import command_help
from runflare import VERSION
from colorama import init,Fore,Style
from runflare.version_check import Version
init()

class RunFlare():
    """
    Runflare Paas Cli

        Deploy Only With One Command!

        Make Your Dreams On Clouds ...
         _______             _         _______   _         _______   _______   _______
        (  ____ ) |\     /| ( (    /| (  ____ \ ( \       (  ___  ) (  ____ ) (  ____ \\
        | (    )| | )   ( | |  \  ( | | (    \/ | (       | (   ) | | (    )| | (    \/
        | (____)| | |   | | |   \ | | | (__     | |       | (___) | | (____)| | (__
        |     __) | |   | | | (\ \) | |  __)    | |       |  ___  | |     __) |  __)
        | (\ (    | |   | | | | \   | | (       | |       | (   ) | | (\ (    | (
        | ) \ \__ | (___) | | )  \  | | )       | (____/\ | )   ( | | ) \ \__ | (____/\\
        |/   \__/ (_______) |/    )_) |/        (_______/ |/     \| |/   \__/ (_______/


    """

    def _help(self):
        """for more help"""
        return """
        Runflare Paas Cli@{VERSION}   

        Deploy Only With One Command!
    
        Make Your Dreams On Clouds ...\n
         _______             _         _______   _         _______   _______   _______ 
        (  ____ ) |\     /| ( (    /| (  ____ \ ( \       (  ___  ) (  ____ ) (  ____ \\
        | (    )| | )   ( | |  \  ( | | (    \/ | (       | (   ) | | (    )| | (    \/
        | (____)| | |   | | |   \ | | | (__     | |       | (___) | | (____)| | (__    
        |     __) | |   | | | (\ \) | |  __)    | |       |  ___  | |     __) |  __)   
        | (\ (    | |   | | | | \   | | (       | |       | (   ) | | (\ (    | (      
        | ) \ \__ | (___) | | )  \  | | )       | (____/\ | )   ( | | ) \ \__ | (____/\\
        |/   \__/ (_______) |/    )_) |/        (_______/ |/     \| |/   \__/ (_______/

    runflare COMMAND [OPTION]
    
   
{bold_start}Enter Your Username and Password To login Securly:{bold_stop}
   runflare login
{bold_start}Logout From This Device:{bold_stop}
   runflare logout
{bold_start}Deploy Your Project Form Local to Cloud:{bold_stop}
   runflare deploy
   runflare deploy -y Use previous item id to deploy files
{bold_start}Watch Logs:{bold_stop}
   runflare logs 
   runflare logs -f\tWatch realtime log
   runflare logs -y\tUse previous item id to watch logs
{bold_start}Watch Events:{bold_stop}
   runflare events
   runflare events -f\tWatch realtime events
   runflare events -y\tUse previous item id to watch events
{bold_start}Start Project:{bold_stop}
   runflare start
   runflare start -y\tUse previous item id to Start project
{bold_start}Restart Project:{bold_stop} 
   runflare restart
   runflare restart -y\tUse previous item id to Restart project
{bold_start}Stop Project:{bold_stop}
   runflare stop
   runflare stop -y\tUse previous item id to Stop project
    
For More Help Enter
    runflare COMMAND help    
    
        """.format(bold_stop=Style.RESET_ALL,bold_start=Style.BRIGHT,VERSION=VERSION)

    def help(self):
        """for more help"""
        return self._help()

    @staticmethod
    def login():
        """

        Enter Your Username and Password To login Securly

        """

        return save_token()

    @staticmethod
    def logout():
        """Logout From This Device
        """

        return del_token()

    @staticmethod
    def deploy(y=False,help=False):
        """Deploy your project form local to cloud

        runflare deploy
        runflare deploy -y    Use previous item id to deploy files

        """
        if help:
            command_help(command="deploy", y="use cached service id to deploy project")
            exit()
        return deploy(y=y)

    @staticmethod
    def logs(f=False, y=False, help=False):

        """Watch logs interactively

        -f      Watch realtime log
        -y      Use cached service id to watch log

        """
        if help:
            command_help(command="log", f="Watch realtime log", y="Use cached service id to watch log")
            exit()
        return log(f=f,y=y)

    @staticmethod
    def events(f=False, y=False, help=False):

        """Watch events interactively

        -f      Watch realtime events
        -y      Use cached service id to watch events

        """
        if help:
            command_help(command="log", f="Watch realtime log", y="Use cached service id to watch log")
            exit()
        return events(f=f,y=y)

    @staticmethod
    def start(y=False, help=False):
        """Start project

                -y      Use cached service id to Start project

        """
        if help:
            command_help(command="start", y="Use cached service id to Start project")
            exit()
        return start(y)

    @staticmethod
    def restart(y=False, help=False):
        """Restart project

                -y      Use cached service id to Restart project

        """
        if help:
            command_help(command="restart", y="Use cached service id to Restart project")
            exit()
        return restart(y)

    @staticmethod
    def stop(y=False, help=False):
        """Stop project

            -y      Use cached service id to Stop project

        """
        if help:
            command_help(command="stop", y="Use cached service id to Stop project")
            exit()
        return stop(y)

    @staticmethod
    def version():
        """

        Runflare Cli Version

        """
        return VERSION

    def __str__(self):
        return self._help()


def run():

    clear()
    checker = Version.has_new_version()
    if checker:
        try:
            fire.Fire(RunFlare)
        except KeyError:
            raise SystemExit
        if checker == 2:
            print()
            print("""                     ╭──────────────────────────────────────╮
                     │           Update available           │
                     │ Run `pip install --upgrade runflare` │
                     ╰──────────────────────────────────────╯""")
    else:
        print(Fore.RED + " ## Please Check Your Internet Connection ##")
        exit(1)





if __name__ == '__main__':
    run()