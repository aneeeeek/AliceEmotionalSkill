import datetime
import random
from flask import Flask, request
import answers
import dbConnection
import enum

from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel

answerNumber = 0

app = Flask(__name__)

goodScore, neutralScore, badScore = 0, 0, 0
anxiety, frustration, aggressiveness, rigidity = 0,0,0,0
session = 0

@app.route("/alice", methods=["POST"])
def main():
    #todo update session
    global session
    global answerNumber

    session = request.json.get('session', {}).get('session_id')
    if request.json.get('session', {}).get('new'):
        addSession(session)


    text = request.json.get('request', {}).get('original_utterance').lower()

    if isExitText(text):
        updateSession(session, 0, 1, answerNumber)
        return response("До встречи!", True)

    # диалог с пользователем начался
    if request.json.get('session', {}).get('new'):
        return response(answers.getGreeting(random.randint(0, answers.getGreetingsSize() - 1)), False)

    # диалог с пользователем продолжается
    else:
        # ответ на вопрос о прохождении навыка, вопрос 1
        if answerNumber == 0:
            if text == 'давай':
                answerNumber += 1
                text = getTextQuestion()
                updateSession(session, 0, 0, answerNumber)
                return response(text, False)
            else:
                return response("Ну и пока", True)

        # ответ на текстовый вопрос 1, вопрос 2
        elif answerNumber == 1:
            addScore(text)
            answerNumber += 1
            return response(getBinaryQuestion(), False)

        # ответ на вопрос да/нет 1, вопрос 3
        elif answerNumber == 2:
            isAdded = addScore(text)
            if isAdded == 0:
                return response("Ответьте только словом да или нет", False)
            else:
                answerNumber += 1
                updateSession(session, 0, 0, answerNumber)
                return response(getRatingQuestion(), False)

        # ответ на вопрос числом 1, вопрос 4
        elif answerNumber == 3:
            isAdded = addScore(text)
            if isAdded == 0:
                return response("Ответьте только числом от 1 до 5", False)
            else:
                answerNumber += 1
                updateSession(session, 0, 0, answerNumber)
                return response(getTextQuestion(), False)

        # ответ на текстовый вопрос 2, вопрос 5
        elif answerNumber == 4:
            addScore(text)
            answerNumber += 1
            updateSession(session, 0, 0, answerNumber)
            return response(getBinaryQuestion(), False)

        # ответ на вопрос да/нет 2, вопрос 6
        elif answerNumber == 5:
            isAdded = addScore(text)
            if isAdded == 0:
                return response("Ответьте только словом да или нет", False)
            else:
                answerNumber += 1
                updateSession(session, 0, 0, answerNumber)
                return response(getRatingQuestion(), False)

        # ответ на вопрос числом 2, вопрос 7
        elif answerNumber == 6:
            isAdded = addScore(text)
            if isAdded == 0:
                return response("Ответьте только числом от 1 до 5", False)
            else:
                answerNumber += 1
                updateSession(session, 0, 0, answerNumber)
                return response(getTextQuestion(), False)

        # ответ на вопрос текстом 3, вопрос 8
        elif answerNumber == 7:
            addScore(text)
            answerNumber += 1
            updateSession(session, 0, 0, answerNumber)
            return response(getBinaryQuestion(), False)

        # ответ на вопрос да/нет 3, вопрос 9
        elif answerNumber == 8:
            isAdded = addScore(text)
            if isAdded == 0:
                return response("Ответьте только словом да или нет", False)
            else:
                answerNumber += 1
                updateSession(session, 0, 0, answerNumber)
                return response(getRatingQuestion(), False)

        # ответ на вопрос числом 3, вопрос 10
        elif answerNumber == 9:
            isAdded = addScore(text)
            if isAdded == 0:
                return response("Ответьте только числом от 1 до 5", False)
            else:
                answerNumber += 1
                updateSession(session, 0, 0, answerNumber)
                return response(getRatingQuestion(), False)

        # ответ на вопрос числом 4, результат
        else:
            isAdded = addScore(text)
            if isAdded == 0:
                return response("Ответьте только числом от 1 до 5", False)
            else:
                updateSession(session, 0, 1, answerNumber)
                result = getMaxScore(goodScore, neutralScore, badScore)
                allScore = "На основе анализа вашего настроения " #"Вы набрали " + str(goodScore) + " положительных баллов, " + str(neutralScore) + " нейтральных баллов, " + str(badScore) + " негативных баллов, "
                if result == "goodScore":
                    return response(
                        allScore + "можно сделать вывод, что Вы чувствуете себя хорошо! Сохраняйте позитивный настрой!",
                        True)  # закончить сессию
                elif result == "neutralScore":
                    return response(
                        allScore + "можно сделать вывод, что Вы чувствуете себя не так уж плохо! Все наладится, главное оставаться сильным!",
                        True)  # закончить сессию
                else:
                    return response(
                        allScore + "можно сделать вывод, что Вы чувствуете себя плохо! Не бойтесь, черные полосы всегда проходят!",
                        True)  # закончить сессию


# === Получить текстовый вопрос, который ранее не задавался пользователю ===
def getTextQuestion():
    # Получить индексы всех вопросов текстового типа
    idList = dbConnection.getIDTextQuestions()
    return returnQuestionText(idList)

# === Получить вопрос с ответом ДА/НЕТ, который ранее не задавался пользователю ===
def getBinaryQuestion():
    result = getMaxScore(goodScore,neutralScore,badScore)
    # Получить индексы всех вопросов в зависимости от результата
    if result == "goodScore":
        idList = dbConnection.getIDBinaryGoodQuestions()
    elif result == "badScore":
        idList = dbConnection.getIDBinaryBadQuestions()
    else:
        if random.randint(0,1):
            idList = dbConnection.getIDBinaryGoodQuestions()
        else:
            idList = dbConnection.getIDBinaryBadQuestions()

    return returnQuestionText(idList)

# === Получить числовой вопрос, который ранее не задавался пользователю ===
def getRatingQuestion():
    if answerNumber == 3:
        idList = dbConnection.getIDRatingAnxietyQuestions()
    elif answerNumber == 6:
        idList = dbConnection.getIDRatingFrustrationQuestions()
    elif answerNumber == 9:
        idList = dbConnection.getIDRatingAgressivnessQuestions()
    else:
        idList = dbConnection.getIDRatingRigidityQuestions()

    return returnQuestionText(idList)

def returnQuestionText(idList):
    # Выбрать случайный неповторяющийся индекс вопроса и записать его
    idRandom = random.choice(idList)
    usedIDs = dbConnection.getUsedQuestionIDs(session)
    if usedIDs != None:
        while idRandom in usedIDs:
            idRandom = random.choice(idList)

    dbConnection.addUsedQuestion(session,int(idRandom[0]))
    dbConnection.updateLastQuestionID(session,int(idRandom[0]))
    # Получить текст вопроса по индексу
    textList = dbConnection.getQuestion(int(idRandom[0]))
    question = textList[0]
    return str(question[0])

def addScore(answer):
    global goodScore, neutralScore, badScore, anxiety, frustration, aggressiveness, rigidity

    lastQ = dbConnection.getLastQuestion(session)
    type = dbConnection.getQuestionType(int(lastQ[0][0]))
    type = int(type[0][0])
    if type == 1:
        result = getSentiment(answer)
        if result == 'positive':
            goodScore += 1
        elif result == 'neutral':
            neutralScore += 1
        elif result == 'negative':
            badScore += 1
        else:
            neutralScore += 0.5
    elif type == 2:
        if answer == "да":
            goodScore+=1
        elif answer == "нет":
            badScore+=1
        else:
            return 0
    elif type == 3:
        if answer == "да":
            badScore+=1
        elif answer == "нет":
            goodScore+=1
        else:
            return 0
    elif type == 4:
        if answer.isnumeric():
            if 5 >= int(answer) >= 1:
                anxiety+=int(answer)
                if int(answer) == 1:
                    goodScore += 2
                elif int(answer) == 2:
                    goodScore += 1
                elif int(answer) == 3:
                    neutralScore+=1
                elif int(answer) == 4:
                    badScore += 1
                else:
                    badScore += 2
            else: return 0
        else: return 0
    elif type == 5:
        if answer.isnumeric():
            if 5 >= int(answer) >= 1:
                frustration+=int(answer)
                if int(answer) == 1:
                    goodScore += 2
                elif int(answer) == 2:
                    goodScore += 1
                elif int(answer) == 3:
                    neutralScore+=1
                elif int(answer) == 4:
                    badScore += 1
                else:
                    badScore += 2
            else: return 0
        else: return 0
    elif type == 6:
        if answer.isnumeric():
            if 5 >= int(answer) >= 1:
                aggressiveness+=int(answer)
                if int(answer) == 1:
                    goodScore += 2
                elif int(answer) == 2:
                    goodScore += 1
                elif int(answer) == 3:
                    neutralScore+=1
                elif int(answer) == 4:
                    badScore += 1
                else:
                    badScore += 2
            else: return 0
        else: return 0
    else:
        if answer.isnumeric():
            if 5 >= int(answer) >= 1:
                rigidity+=int(answer)
                if int(answer) == 1:
                    goodScore += 2
                elif int(answer) == 2:
                    goodScore += 1
                elif int(answer) == 3:
                    neutralScore+=1
                elif int(answer) == 4:
                    badScore += 1
                else:
                    badScore += 2
            else: return 0
        else: return 0

    updateResult()

def addSession(session):
    user = request.json.get('session', {}).get('user',{}).get('user_id')
    user_tuple=(user,)
    userIDs = dbConnection.getUsers()
    if user_tuple not in userIDs:
        dbConnection.addUser(user)

    dbConnection.addResult(0,0,0,0,0,0,0)
    from datetime import datetime
    date = datetime.now()
    id_res = str(dbConnection.getLastResult()[0][0])
    dbConnection.addSession(session, 1, date, user, id_res,0,0,0)


def updateSession(session,isNew,isFinished,answerNumber):
    dbConnection.updateSession(session,isNew,isFinished,answerNumber)

def updateResult():
    id_result = str(dbConnection.getResult(session)[0][0])
    dbConnection.updateResult(id_result, goodScore, neutralScore, badScore,
                              anxiety, frustration, aggressiveness, rigidity)

def response(text, end_session):
    return {
        'response':
            {
                'text': text,
                'end_session': end_session
            },
        'version': '1.0'
    }


def isExitText(text):
    return text == 'выход'


def getMaxScore(goodScore, neutralScore, badScore):
    maxScore = max(goodScore, neutralScore, badScore)
    if maxScore == goodScore == neutralScore == badScore:
        return "neutralScore"
    elif maxScore == goodScore:
        if maxScore == neutralScore:
            return "goodScore"
        elif maxScore == badScore:
            return "neutralScore"
        else:
            return "goodScore"
    elif maxScore == neutralScore:
        if maxScore == badScore:
            return "badScore"
        else:
            return "neutralScore"
    elif maxScore == badScore:
        return "badScore"


def getSentiment(text):
    tokenizer = RegexTokenizer()
    model = FastTextSocialNetworkModel(tokenizer=tokenizer)
    result = model.predict([text.lower()], k=1)
    return list(result[0].keys()).pop(0)


app.run('0.0.0.0', port=5000, debug=True)
