from .entities.User import User

class ModelUser():

    @classmethod
    def register(self, db, user, mail, password, gender):
        try:
            cursor = db.connection.cursor()
            sql = """ INSERT INTO user (UserName, UserEMail, UserPassword, UserGender) VALUES ('%s','%s','%s','%s') """ % (user, mail, User.hash_password(password), gender)
            cursor.execute(sql)
            db.connection.commit()
            cursor.close()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def login(self, db, user, password):
        try:
            cursor = db.connection.cursor()
            sql = """ SELECT UserID, UserName, UserPassword, UserEMail, UserGender, UserPoints FROM user WHERE UserName = '%s' """ % (user)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                user = User(row[0], row[1], User.check_password(row[2], password), row[3], row[4], row[5])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = """ SELECT UserID, UserName, UserEMail, UserGender, UserPoints FROM user WHERE UserID = %s """ % (id)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                return User(row[0], row[1], None, row[2], row[3], row[4])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)