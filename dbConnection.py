from getpass import getpass
from mysql.connector import connect, Error

def getIDTextQuestions():
    return getQByType(1)
def getIDBinaryGoodQuestions():
    return getQByType(2)
def getIDBinaryBadQuestions():
    return getQByType(3)
def getIDRatingAnxietyQuestions():
    return getQByType(4)
def getIDRatingFrustrationQuestions():
    return getQByType(5)
def getIDRatingAgressivnessQuestions():
    return getQByType(6)
def getIDRatingRigidityQuestions():
    return getQByType(7)

def getQByType(id_type):
    try:
        with connect(
                host="localhost",
                user="root",
                password="anek",
                database="aliceskill",
        ) as connection:
            query = "SELECT id_question FROM aliceskill.questions WHERE id_type ="+str(id_type)+" ;"
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