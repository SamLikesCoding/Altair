'''
    Altair : Database Helper
'''

# Required Libraries
import sqlite3
import hashlib
import datetime

# Poetry


def b2hasher(A, B):
    return hashlib.sha256(str(A).encode()+str(B).encode()).digest()


class Database:

    def __init__(self):

        try:
            self.agent = sqlite3.connect("ALTAIR.sqlite")
            self.cursor = self.agent.cursor()
        except Exception as e:
            print("Error : {}".format(e))

    def register_user(self, data):
        try:
            hash = b2hasher(data["USR_ID"], data['PWD'])
            self.cursor.execute(
                "SELECT * FROM USERS WHERE USR_ID = ?", (data['USR_ID']))
            if len(cursor.fetchall()) == 0:
                self.cursor.execute("INSERT INTO USERS VALUES(? ? ? ?)",
                                    (data['USR_ID'], data["USER"],
                                     hash, "MAINTAINER")
                                    )
                return True
            else:
                print("User Exists!")
                return False
        except Exception as e:
            print("Error: {}".format(e))
            return False

    def auth_user(self, data):
        try:
            hash = b2hasher(data["USR_ID"], data["PWD"])
            self.cursor.execute(
                "SELECT * FROM USERS WHERE USR_ID = ?", (data['USR_ID'],)
            )
            rsp = self.cursor.fetchall()
            if rsp[0][2] == hash:
                print("Good Auth")
                return True
            else:
                print("Bad Auth")
                return False
        except Exception as e:
            print("Error: {}".format(e))
            return False

    def seed_project(self, data):
        date_today = datetime.date.today()
        try:
            self.cursor.execute(
                "SELECT * FROM PROJECTS WHERE PROJECT_ID = ?", (
                    data["PROJECT_ID"],)
            )
            rsp = self.cursor.fetchall()
            if len(rsp) == 0:
                self.cursor.execute("""
                    INSERT INTO PROJECTS(
                        PROJECT_ID, PROJECT_CREATOR,
                        DATE_CREATED, DESCRIPTION
                    ) VALUES(?, ?, ?, ?)
                """, (
                    data["PROJECT_ID"],
                    data["PROJECT_CREATOR"],
                    date_today,
                    data["DESCRIPTION"]
                )
                )
            else:
                upd_date = datetime.datetime.now()
                self.cursor.execute("""
                    UPDATE PROJECTS 
                    SET DATE_UPDATED = ?
                    WHERE PROJECT_ID = ?
                """, (date_today, data["PROJECT_ID"]))
        except Exception as e:
            print("Error: {}".format(e))
