from module.logger import Logger
from CODE_SOURCE_CRM.Database.user import User
from random import randint
import mysql.connector


class DataBase:
    def __init__(self, host, user, password, database, logger: Logger = Logger("[DataBase]")):
        self.logger = logger
        self.connection_params = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }

    def add_to_database(self, user: User):
        data_user = {
            "id": randint(1, 999999),
            "name": user.name,
            "first_name": user.first_name,
            "email": user.email,
            "telephone": user.telephone,
            "password": user.password
        }
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                self.create_table()
                c.execute(f"select email from User where email='{data_user['email']}'")
                row = c.fetchall()
                if len(row) == 0:
                    c.execute(
                        f"insert into User (id, nom, prenom, email, telephone, password) values({data_user['id']}, '{data_user['name']}', '{data_user['first_name']}', '{data_user['email']}', {data_user['telephone']}, '{data_user['password']}')")
                    self.logger.great("The user created !")
                else:
                    self.logger.warning("The email is already used !")
                db.commit()

    def get_users_on_sql(self):
        self.create_table()
        data = None
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                c.execute("select id, nom, prenom, email, telephone from user")
                data = c.fetchall()
        return data

    def create_table(self):
        with mysql.connector.connect(**self.connection_params) as db:
            with db.cursor() as c:
                c.execute("""
                            create table if not exists User (
                                id int primary key not null,
                                nom varchar(100) default null,
                                prenom varchar(100) default null,
                                email varchar(100) default null,
                                telephone int(15) default null,
                                password varchar(1000) default null
                            );
                        """)

#bdd = DataBase()
#print(bdd.get_users_on_sql())
#add_user(bdd)
