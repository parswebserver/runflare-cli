import sqlite3
from .base_manager import Data_Manager
from runflare.settings import USER_HOME_PATH,DATASTORE,FOLDER_NAME
from runflare.runflare_client.custom_pathlib import Path
import shutil
import os

class Sqllite_Manager(Data_Manager):

    def __init__(self):
        self.DATASTORE_NAME = DATASTORE.get("NAME")
        self.DATASTORE_BACKEND = DATASTORE.get("BACKEND")
        assert self.DATASTORE_BACKEND == "sqlite3", "Invalid Backend"
        self.cursor = None
        self.main_db_path = str(USER_HOME_PATH) + f"/{FOLDER_NAME}/"
        self.db_name = f"{self.DATASTORE_NAME}"


    def create_connection(self,path,db_name):
        try:
            if not self.mkdirs(path):
                exit(1)
            conn = sqlite3.connect(path+db_name)
            return conn
        except sqlite3.Error as e:
            print(e)
            exit(1)

    def close_connection(self, connection):
        connection.commit()
        connection.close()


    def check_table_exists(self,conn,table_name):
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        if not result:
            return False
        return True

    def create_table(self,conn,table_name,**fields):
        incomming = list(fields.keys())
        query = self.create_table_query(table_name,**fields)
        cursor = conn.cursor()
        cursor.execute(query)

        check_column = f"SELECT * FROM '{table_name}'"
        data = cursor.execute(check_column)

        db_column = []

        for column in data.description:
            if column[0] != "id":
                db_column.append(column[0])
        if db_column != incomming:
            print("Error in Database, Recreating Table")
            query = self.drop_table_query(table_name)
            cursor.execute(query)

            query = self.create_table_query(table_name, **fields)
            cursor.execute(query)

    def insert_into(self,conn,table_name,**fields):
        query,params = self.insert_into_query(table_name, **fields)
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return True
        except:
            return False

    def delete_row(self,conn,table_name,**fields):
        query,params = self.delete_query(table_name, **fields)
        cursor = conn.cursor()
        cursor.execute(query, params)

    def drop_table(self,conn,table_name):
        query = self.drop_table_query(table_name)
        cursor = conn.cursor()
        cursor.execute(query)


    def save_token(self,token,email):
        self.conn = self.create_connection(self.main_db_path,self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table(self.conn,"Token", token="VARCHAR(255)", email="VARCHAR(255)")
        self.insert_into(self.conn,"Token", token=token, email=email)
        self.close_connection(self.conn)

    def del_token(self):
        if os.path.exists(self.main_db_path+self.db_name):

            self.conn = self.create_connection(self.main_db_path, self.db_name)
            self.cursor = self.conn.cursor()

            if not self.check_table_exists(self.conn,"Token"):
                return False, "You'r Not logged in"
            self.drop_table(self.conn, "Token")
            self.close_connection(self.conn)
            return True, "Successfully Logged Out"
        else:
            return False, "You'r Not logged in"

    def get_token(self):
        if os.path.exists(self.main_db_path+self.db_name):
            self.conn = self.create_connection(self.main_db_path, self.db_name)
            self.cursor = self.conn.cursor()

            if not self.check_table_exists(self.conn, "Token"):
                return False, "You'r Not logged in"

            query = "SELECT * FROM Token WHERE id=(SELECT max(id) FROM Token);"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            self.close_connection(self.conn)
            if not result:
                return False,"Please Login First"
            return True,result[0][1]
        else:
            return False,"Please Login First"

    @property
    def get_project_root(self):
        current_path = Path(os.getcwd())
        _,roots = self.get_project_roots
        root_path_object = (Path(root[1]) for root in roots)
        for root in root_path_object:
            if current_path.is_relative_to(root):
                return str(root)
        current_path = str(current_path)
        self.save_project_root(current_path)
        return current_path

    def get_roots(self):
        if os.path.exists(self.main_db_path + self.db_name):
            self.conn = self.create_connection(self.main_db_path, self.db_name)
            self.cursor = self.conn.cursor()

            if not self.check_table_exists(self.conn, "Roots"):
                return False, []
            query = "SELECT * FROM Roots;"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            self.close_connection(self.conn)
            return True, result
        else:
            return False, []

    def delete_roots(self,roots):
        self.conn = self.create_connection(self.main_db_path, self.db_name)
        self.cursor = self.conn.cursor()
        query = 'DELETE FROM `Roots` WHERE `root` IN ('
        for i,root in enumerate(roots):
            try:
                path = f"{root}/{FOLDER_NAME}"
                if os.path.exists(path):
                    shutil.rmtree(path)
            except Exception as e:
                print(e)
            if not i:
                query += f"'{root}'"
            else:
                query += f" ,'{root}'"

        query += ");"
        self.cursor.execute(query)
        self.close_connection(self.conn)

    def save_project_root(self,root):
        self.conn = self.create_connection(self.main_db_path, self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table(self.conn, "Roots", root="VARCHAR(255)")
        self.insert_into(self.conn, "Roots",root=root)
        self.close_connection(self.conn)

    @property
    def get_project_roots(self):
        if os.path.exists(self.main_db_path + self.db_name):
            self.conn = self.create_connection(self.main_db_path, self.db_name)
            self.cursor = self.conn.cursor()

            if not self.check_table_exists(self.conn, "Roots"):
                return False, []
            query = "SELECT * FROM Roots;"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            self.close_connection(self.conn)
            return True, result
        else:
            return False, []

    def get_project_cache(self,local_db_path):
        if os.path.exists(local_db_path + self.db_name):
            self.conn = self.create_connection(local_db_path, self.db_name)
            self.cursor = self.conn.cursor()

            if not self.check_table_exists(self.conn, "Cache"):
                return 0, []
            query = "SELECT project,project_id,item,item_id FROM Cache WHERE id=(SELECT max(id) FROM Cache);"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            result = result[0]
            if None in result[0:2]:
                return 0, []
            if None in result[2:4]:
                return 3, result[0:2]
            self.close_connection(self.conn)
            return True, result
        else:
            return 0, []

    def execute(self,conn,query):
        self.cursor = conn.cursor()
        self.cursor.execute(query)
        return self.cursor.fetchall()
    def save_project_cache(self,local_db_path,project,project_id,item,item_id):

        self.conn = self.create_connection(local_db_path, self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table(self.conn, "Cache", project="VARCHAR(255)",project_id="INT(10)", item="VARCHAR(255)",item_id="INT(10)")
        self.insert_into(self.conn, "Cache", project=project, project_id=project_id,item=item,item_id=item_id)
        self.close_connection(self.conn)


    def get_last_deploy(self,local_db_path):
        if os.path.exists(local_db_path + self.db_name):
            self.conn = self.create_connection(local_db_path, self.db_name)
            self.cursor = self.conn.cursor()

            if not self.check_table_exists(self.conn, "Last_Deploy"):
                return False, []

            query = "SELECT `path`,`name`,`item_type`,`sha`,`path2`, FROM last_deploy;"

            self.cursor.execute(query)
            result = self.cursor.fetchall()
            self.close_connection(self.conn)
            return True,result
        else:
            return False, []

    def get_timestamp(self,local_db_path,**kwargs):
        if os.path.exists(local_db_path + self.db_name):
            self.conn = self.create_connection(local_db_path, self.db_name)
            self.cursor = self.conn.cursor()

            if not self.check_table_exists(self.conn, "Last_Deploy"):
                return None

            query = self.filtered_query("Last_Deploy",**kwargs)
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            if not result:
                return None
            self.close_connection(self.conn)
            return result[0][-1],result[0][4]
        else:

            return None

    def save_last_deploy(self,local_db_path):
        self.conn = self.create_connection(local_db_path, self.db_name)
        self.cursor = self.conn.cursor()
        self.drop_table(self.conn, "last_deploy")
        query = "ALTER TABLE Current_Dir RENAME TO last_deploy;"
        self.cursor.execute(query)
        self.close_connection(self.conn)

    def save_current_dir(self,conn,data):
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.drop_table(self.conn, "Current_Dir")
        self.create_table(self.conn, "Current_Dir", path="VARCHAR(255)", name="VARCHAR(255)",sha="VARCHAR(255)",path2="VARCHAR(255)")
        self.insert_into(self.conn, "Current_Dir", path=data[0], name=data[1],sha=data[2],path2=data[3])

    def compare(self,local_db_path):
        self.conn = self.create_connection(local_db_path, self.db_name)
        self.cursor = self.conn.cursor()
        if not self.check_table_exists(self.conn, "last_deploy"):
            query = "SELECT DISTINCT path2,type FROM Current_Dir"
            self.cursor.execute(query)
            new = self.cursor.fetchall()
            return new,[],[]
        try:
            query = "SELECT DISTINCT path2,type FROM Current_Dir WHERE path NOT IN (SELECT DISTINCT path FROM last_deploy)"
            self.cursor.execute(query)
            new = self.cursor.fetchall()
            query = "SELECT DISTINCT path2,type FROM last_deploy WHERE path NOT IN (SELECT DISTINCT path FROM Current_Dir)"
            self.cursor.execute(query)
            delete = self.cursor.fetchall()
            query = "SELECT DISTINCT path2,type FROM Current_Dir WHERE path IN (SELECT DISTINCT path FROM last_deploy) AND sha NOT IN (SELECT DISTINCT sha FROM last_deploy)"
            self.cursor.execute(query)
            change = self.cursor.fetchall()
        except:
            print("Error in Database resending all files")
            query = "SELECT DISTINCT path2,type FROM Current_Dir"
            self.cursor.execute(query)
            new = self.cursor.fetchall()
            return new, [], []

        self.close_connection(self.conn)

        return new, change, delete

    def filtered_query(self,table_name,**filter):
        query = f'SELECT * FROM `{table_name}` '
        for index,(key,value) in enumerate(filter.items()):
            if index == 0:
                query += f"WHERE ({key}='{value}' "
            else:
                query += f"AND {key}='{value}' "
        query += ");"
        return query

    def create_table_query(self,table_name,**fields):
        query = f'CREATE TABLE IF NOT EXISTS `{table_name}` (id INTEGER PRIMARY KEY AUTOINCREMENT'
        for (key,value) in fields.items():
            query += f", {key} '{value}' "
        query += ");"
        return query

    def drop_table_query(self,table_name):
        return f"DROP TABLE IF EXISTS {table_name};"

    def insert_into_query(self,table_name,**fields):
        a = "INSERT INTO Token VALUES (Null,?,?);", ("124","test@test.com")
        "INSERT INTO table_name (column1, column2, column3, ...) VALUES (value1, value2, value3, ...);"

        parameters = []
        columns = "(id"
        values = "(Null"
        query = f'INSERT INTO `{table_name}`'


        for (key,value) in fields.items():
            parameters.append(value)
            columns += f",{key}"
            values += ",?"
        columns += ")"
        values += ");"

        query += columns + " VALUES " + values

        return query,tuple(parameters)

    def mkdirs(self,path):
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(e)
            return False

    def rm_file(self,path):
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except Exception as e:
                print(e)
                return False
        return False