from getpass import getpass
from mysql.connector import connect, Error

def getIDTextQuestions():
    try:
        with connect(
                host="localhost",
                user="root",
                password="anek",
                database="aliceskill",
        ) as connection:
            query = "SELECT id_question FROM aliceskill.questions WHERE id_type = 1;"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)

def getQuestion(id):
    try:
        with connect(
                host="localhost",
                user="root",
                password="anek",
                database="aliceskill",
        ) as connection:
            query = "SELECT text FROM aliceskill.questions WHERE id_question="+str(id)+";"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)

def getIDBinaryGoodQuestions():
    try:
        with connect(
                host="localhost",
                user="root",
                password="anek",
                database="aliceskill",
        ) as connection:
            query = "SELECT id_question FROM aliceskill.questions WHERE id_type = 2;"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)

def getIDBinaryBadQuestions():
    try:
        with connect(
                host="localhost",
                user="root",
                password="anek",
                database="aliceskill",
        ) as connection:
            query = "SELECT id_question FROM aliceskill.questions WHERE id_type = 3;"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)