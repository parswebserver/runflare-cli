import platform
from pathlib import Path

WEBSOCKET_URL = 'wss://stream.runflare.com'
BASE_URL = "https://api.runflare.com"

FOLDER_NAME = ".cloud"
DATASTORE = {
    "BACKEND": "sqlite3",
    "NAME": "db.sqlite3",
}

TAR_NAME = "workspace.tar.gz"
CHANGES_NAME = "changes.json"
LOGIN_URL = '/account/login/'
PROJECT_LIST_URL = '/api/v1/projects/cli/'
UPLOAD_URL = "/project/{}/items/{}/deploy/"
START_URL = "/project/{}/items/{}/start/"
STOP_URL = "/project/{}/items/{}/stop/"
RESTART_URL = "/project/{}/items/{}/restart/"
VERSION_URL = "/version/"
CANCEL_DEPLOY_URL = "/project/deploy/cancel/"


NR_LOG_URL = "/project/{}/items/{}/logs/"
NR_EVENTS_URL = '/project/{}/events/'


DOC_URL = 'https://runflare.com/docs/get-started/'
MAX_TRY = 3

LOG_URL = "logs"
EVENTS_URL = "events"


OS_SYSTEM = platform.system()
OS_RELEASE = platform.release()
OS_VERSION = platform.version()
OS_PLATFORM = platform.platform()
USER_HOME_PATH = Path.home()

BASE_DIR = Path(__file__)

DEFAULT_IGNORE_FILE = ['/.cloud/','.cloud/','/.cloud']

