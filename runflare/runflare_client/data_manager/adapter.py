from .sqlite_manager import Sqllite_Manager

class Adapter:

    @staticmethod
    def create_connection(path,db_name):
        return Sqllite_Manager().create_connection(path,db_name)

    @staticmethod
    def close_connection(conn):
        return Sqllite_Manager().close_connection(conn)


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
    def save_last_deploy(local_db_path):
        return Sqllite_Manager().save_last_deploy(local_db_path)

    @staticmethod
    def get_project_root():
        return Sqllite_Manager().get_project_root

    @staticmethod
    def get_timestamp(local_db_path,**kwargs):
        return Sqllite_Manager().get_timestamp(local_db_path,**kwargs)


    @staticmethod
    def get_project_cache(local_db_path):
        return Sqllite_Manager().get_project_cache(local_db_path)

    @staticmethod
    def save_project_cache(local_db_path,project,project_id,service,service_id):
        return Sqllite_Manager().save_project_cache(local_db_path,project,project_id,service,service_id)

    @staticmethod
    def save_current_dir(conn,data):
        return Sqllite_Manager().save_current_dir(conn,data)

    @staticmethod
    def compare(local_db_path):
        return Sqllite_Manager().compare(local_db_path)

    @staticmethod
    def insert_into(conn,table_name,**fields):
        return Sqllite_Manager().insert_into(conn,table_name,**fields)

    @staticmethod
    def drop_table(conn,table_name):
        return Sqllite_Manager().drop_table(conn,table_name)

    @staticmethod
    def get_roots():
        return Sqllite_Manager().get_roots()

    @staticmethod
    def delete_roots(roots):
        return Sqllite_Manager().delete_roots(roots)

    @staticmethod
    def create_table(conn,table_name,**fields):
        return Sqllite_Manager().create_table(conn,table_name,**fields)

    @staticmethod
    def execute(conn,query):
        return Sqllite_Manager().execute(conn,query)