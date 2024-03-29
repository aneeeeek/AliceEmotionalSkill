from getpass import getpass
from mysql.connector import connect, Error


def connectDB():
    return connect(
        host="localhost",
        user="root",
        password="anek",
        database="aliceskill",
    )


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
        with connectDB() as connection:
            query = "SELECT id_question FROM aliceskill.questions WHERE id_type =" + str(id_type) + " ;"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def getQuestion(id):
    try:
        with connectDB() as connection:
            query = "SELECT text FROM aliceskill.questions WHERE id_question=" + str(id) + ";"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def getUsedQuestionIDs(id_session):
    try:
        with connectDB() as connection:
            query = "SELECT id_question FROM aliceskill.sessionstoquestions WHERE id_session='" + str(id_session) + "';"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def getQuestionType(id):
    try:
        with connectDB() as connection:
            query = "SELECT id_type FROM aliceskill.questions WHERE id_question=" + str(id) + ";"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def getUsers():
    try:
        with connectDB() as connection:
            query = "SELECT id_user FROM aliceskill.users;"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def addUser(id_user):
    try:
        with connectDB() as connection:
            query = "INSERT into aliceskill.users (id_user) VALUES ('" + str(id_user) + "');"
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
    except Error as e:
        print(e)


def addResult(good, neutral, bad, anx, fr, aggr, rig):
    try:
        with connectDB() as connection:
            query = "INSERT into aliceskill.results (goodScore, neutralScore, badScore, anxiety, frustration," \
                    "aggressiveness, rigidity) " \
                    "VALUES (" + str(good) + "," + str(neutral) + "," + str(bad) + "," + str(anx) + "," + str(
                fr) + "," + str(aggr) + "," + str(rig) + ");"
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
    except Error as e:
        print(e)


def updateResult(id_res, good, neutral, bad, anx, fr, aggr, rig):
    try:
        with connectDB() as connection:
            query = "UPDATE aliceskill.results SET goodScore=" + str(good) + ",neutralScore=" + str(neutral) + \
                    ",badScore=" + str(bad) + ",anxiety=" + str(anx) + ",frustration=" + str(fr) + \
                    ",aggressiveness=" + str(aggr) + ", rigidity=" + str(rig) + " WHERE id_result=" + str(id_res) + ";"
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
    except Error as e:
        print(e)


def getResult(id_session):
    try:
        with connectDB() as connection:
            query = "SELECT id_result FROM aliceskill.sessions WHERE id_session='" + id_session + "';"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def getLastResult():
    try:
        with connectDB() as connection:
            query = "SELECT id_result FROM aliceskill.results ORDER BY id_result DESC LIMIT 1;"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def addSession(id_session, new, datetime, id_user, id_result, isFinished, id_lastQuestion, answerNumber):
    try:
        with connectDB() as connection:
            query = "INSERT into aliceskill.sessions (id_session, new, dateTime, id_user, id_result,isFinished, id_lastQuestion, answerNumber) " \
                    "VALUES ('" + str(id_session) + "'," + str(new) + ",'" + str(datetime) + "','" + str(
                id_user) + "'," + str(id_result) + "," + str(isFinished) + "," + str(id_lastQuestion) + "," + str(
                answerNumber) + ");"
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
    except Error as e:
        print(e)


def updateSession(id_session, new, isFinished, answerNumber):
    try:
        with connectDB() as connection:
            query = "UPDATE aliceskill.sessions SET new=" + str(new) + ",isFinished=" + str(
                isFinished) + ",answerNumber=" + str(answerNumber) + \
                    " WHERE id_session='" + str(id_session) + "';"
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
    except Error as e:
        print(e)


def addUsedQuestion(id_session, id_question):
    try:
        with connectDB() as connection:
            query = "INSERT into aliceskill.sessionstoquestions (id_session,id_question) VALUES ('" + str(
                id_session) + "'," + str(id_question) + ");"
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
    except Error as e:
        print(e)


def updateLastQuestionID(session, id):
    try:
        with connectDB() as connection:
            query = "UPDATE aliceskill.sessions SET id_lastQuestion=" + str(id) + \
                    " WHERE id_session='" + str(session) + "';"
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
    except Error as e:
        print(e)


def getLastQuestion(session):
    try:
        with connectDB() as connection:
            query = "SELECT id_lastQuestion FROM aliceskill.sessions WHERE id_session='" + str(session) + "';"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def getAnswerNumber(session):
    try:
        with connectDB() as connection:
            query = "SELECT answerNumber FROM aliceskill.sessions WHERE id_session='" + str(session) + "';"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def getResults(session):
    try:
        with connectDB() as connection:
            query = "SELECT goodScore, neutralScore, badScore, anxiety, frustration, aggressiveness, rigidity FROM aliceskill.results WHERE id_result='" + str(
                int(getResult(session)[0][0])) + "';"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def addFinalResult(session, finalResult):
    try:
        with connectDB() as connection:
            query = "UPDATE aliceskill.sessions SET finalResult='" + str(finalResult) + \
                    "' WHERE id_session='" + str(session) + "';"
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
    except Error as e:
        print(e)


def getGreetings():
    return getAnswerByType(1)


def getGoodbye():
    return getAnswerByType(14)


def getConclusion():
    return getAnswerByType(2)


def getGoodResult():
    return getAnswerByType(5)


def getNeutralResult():
    return getAnswerByType(6)


def getNegativeResult():
    return getAnswerByType(7)


def getMethodic():
    return getAnswerByType(15)


def getEnd():
    return getAnswerByType(17)


def getAnswerByType(id_type):
    try:
        with connectDB() as connection:
            query = "SELECT id_answer FROM aliceskill.answers WHERE id_type =" + str(id_type) + " ;"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def getAnswer(id):
    try:
        with connectDB() as connection:
            query = "SELECT text FROM aliceskill.answers WHERE id_answer=" + str(id) + ";"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)


def getStatistic(id_user):
    try:
        with connectDB() as connection:
            query = "SELECT dateTime, finalResult FROM aliceskill.sessions WHERE isFinished=1 AND finalResult IS NOT NULL AND id_user='" + str(
                id_user) + "'ORDER BY id_result;"
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)
