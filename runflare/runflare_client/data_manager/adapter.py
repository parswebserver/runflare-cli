from .sqlite_manager import Sqllite_Manager

class Adapter:

    @staticmethod
    def save_token(token,email):
        Sqllite_Manager().save_token(token,email)

    @staticmethod
    def del_token():
        return Sqllite_Manager().del_token()

    @staticmethod
    def get_token():
        return Sqllite_Manager().get_token()

    @staticmethod
    def get_last_deploy(local_db_path):
        return Sqllite_Manager().get_last_deploy(local_db_path)

    @staticmethod
    def save_last_deploy(local_db_path,data):
        return Sqllite_Manager().save_last_deploy(local_db_path,data)

    @staticmethod
    def get_project_root():
        return Sqllite_Manager().get_project_root

    @staticmethod
    def get_project_cache(local_db_path):
        return Sqllite_Manager().get_project_cache(local_db_path)

    @staticmethod
    def save_project_cache(local_db_path,project,project_id,service,service_id):
        return Sqllite_Manager().save_project_cache(local_db_path,project,project_id,service,service_id)
