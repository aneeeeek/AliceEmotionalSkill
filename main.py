import random
import re

from flask import Flask, request
import dbConnection
import synonyms

from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel

app = Flask(__name__)


@app.route("/alice", methods=["POST"])
def main():
    # получить id сессии из запроса
    session = request.json.get('session', {}).get('session_id')
    # получить статус сессии из запроса
    isNewSession = request.json.get('session', {}).get('new')

    # если сессия новая - добавить ее в базу данных
    if isNewSession:
        addSession(session)

    # получить текущее состояние ответов из базы данных
    answerNumber = getAnswerNumber(session)
    results = getResultsDict(session)

    # получить текст пользователя из запроса
    text = request.json.get('request', {}).get('original_utterance').lower()
    textWithoutPunctuation = re.sub(r'[^\w\s]', '', text)

    # пользователь хочет выйти
    if synonyms.isExitText(textWithoutPunctuation):
        updateSession(session, 0, 1, answerNumber)
        return response(getGoodbye(), True)

    # пользователь просит повторить вопрос
    if synonyms.isRepeatQuestion(textWithoutPunctuation):
        return response(getLastQuestionText(session), False)

    # пользователь просит помощь
    if synonyms.isHelp(textWithoutPunctuation):
        return response(getHelp(), False)

    # пользователь спрашивает что умеет навык
    if synonyms.isWhatCanDo(textWithoutPunctuation):
        return response(getWhatCanYouDo(), False)

    # пользователь просит запустить навык заново
    if synonyms.isRepeatSkill(textWithoutPunctuation):
        updateSession(session, 0, 0, 0)
        results['goodScore'] = 0
        results['neutralScore'] = 0
        results['badScore'] = 0
        results['anxiety'] = 0
        results['frustration'] = 0
        results['aggressiveness'] = 0
        results['rigidity'] = 0
        updateResult(session, results)
        return response(getGreeting(), False)

    # ----------------------- диалог с пользователем начался, сказать приветствие -------------------------------------
    if isNewSession:
        # todo кнопка помощь, выход
        return response(getGreeting(), False)

    # диалог с пользователем продолжается, задавать вопросы
    else:
        isAgree = synonyms.isAgree(text)
        if answerNumber == 0:
            if isAgree == 1:
                answerNumber += 1
                text = getTextQuestion(session)
                updateSession(session, 0, 0, answerNumber)
                # todo кнопка повторить вопрос
                return response(text, False)
            elif isAgree == 0:
                return response(getGoodbye(), True)
            else:
                return response("Я не поняла ваш ответ, повторите, пожалуйста", False)

        elif 1 <= answerNumber <= 9:
            isAdded = addScore(text, session, results)
            if isAdded == 0:
                # todo переделать чтобы в зависимости от вопроса давались подсказки
                return response("неправильная форма ответа", False)
            else:
                question = returnQuestion(answerNumber, session, results)
                answerNumber += 1
                updateSession(session, 0, 0, answerNumber)
                # todo кнопки повторить вопрос;да/нет; 12345
                return response(question, False)

        else:
            isAdded = addScore(text, session, results)
            if isAdded == 0:
                return response("Ответьте только числом от 1 до 5", False)
            else:
                updateSession(session, 0, 1, answerNumber)
                # todo добавить кнопки статистика и выход
                return response(getResultText(results), False)


def response(text, end_session):
    return {
        'response':
            {
                'text': text,
                'end_session': end_session,
                'buttons': [
                    {
                        "title": "Выход",
                        "hide": True
                    }
                ]
            },
        'version': '1.0'
    }


def getMaxScore(results):
    maxScore = max(results['goodScore'], results['neutralScore'], results['badScore'])
    if maxScore == results['goodScore'] == results['neutralScore'] == results['badScore']:
        return "neutralScore"
    elif maxScore == results['goodScore']:
        if maxScore == results['neutralScore']:
            return "goodScore"
        elif maxScore == results['badScore']:
            return "neutralScore"
        else:
            return "goodScore"
    elif maxScore == results['neutralScore']:
        if maxScore == results['badScore']:
            return "badScore"
        else:
            return "neutralScore"
    elif maxScore == results['badScore']:
        return "badScore"


def getSentiment(text):
    tokenizer = RegexTokenizer()
    model = FastTextSocialNetworkModel(tokenizer=tokenizer)
    result = model.predict([text.lower()], k=1)
    return list(result[0].keys()).pop(0)


# ======================= Работа с базой данных ===========================
def getResultText(results):
    result = getMaxScore(results)

    resultText = getConclusion()

    if result == "goodScore":
        resultText += getGoodResult()
    elif result == "neutralScore":
        resultText += getNeutralResult()
    else:
        resultText += getNegativeResult()

    if results['anxiety'] == 4 or results['anxiety'] == 5:
        resultText += getAnxiety(0)  # начало текста
        if results['frustration'] == 4 or results['frustration'] == 5:
            resultText += getFrustration(1)
        if results['aggressiveness'] == 4 or results['aggressiveness'] == 5:
            resultText += getAggressiveness(1)
        if results['rigidity'] == 4 or results['rigidity'] == 5:
            resultText += getRigidity(1)

    elif results['frustration'] == 4 or results['frustration'] == 5:
        resultText += getFrustration(0)  # начало текста
        if results['aggressiveness'] == 4 or results['aggressiveness'] == 5:
            resultText += getAggressiveness(1)
        if results['rigidity'] == 4 or results['rigidity'] == 5:
            resultText += getRigidity(1)

    elif results['aggressiveness'] == 4 or results['aggressiveness'] == 5:
        resultText += getAggressiveness(0)  # начало текста
        if results['rigidity'] == 4 or results['rigidity'] == 5:
            resultText += getRigidity(1)

    elif results['rigidity'] == 4 or results['rigidity'] == 5:
        resultText += getRigidity(0)  # начало текста

    elif (results['anxiety'] == 1 or results['anxiety'] == 2) and (results['frustration'] == 1 or results['frustration'] == 2) and (results['aggressiveness'] == 1 or results['aggressiveness'] == 2) and (results['rigidity'] == 1 or results['rigidity'] == 2):
        resultText += getAnxiety(1)+getFrustration(1)+getAggressiveness(1)+getRigidity(1)

    resultText += ". "

    resultText += getMethodic()

    resultText += getEnd()

    return resultText


def addScore(answer, session, results):
    lastQ = dbConnection.getLastQuestion(session)
    type = int(dbConnection.getQuestionType(int(lastQ[0][0]))[0][0])
    if type == 1:
        result = getSentiment(answer)
        if result == 'positive':
            results['goodScore'] += 1
        elif result == 'neutral':
            results['neutralScore'] += 1
        elif result == 'negative':
            results['badScore'] += 1
        else:
            results['neutralScore'] += 0.5
    elif type == 2:
        result = synonyms.isYesOrNo(answer)
        if result == 1:
            results['goodScore'] += 1
        elif result == 0:
            results['badScore'] += 1
        else:
            return 0
    elif type == 3:
        result = synonyms.isYesOrNo(answer)
        if result == 1:
            results['badScore'] += 1
        elif result == 0:
            results['goodScore'] += 1
        else:
            return 0
    elif type == 4:
        answer = synonyms.isNumeric(answer)
        if answer:
            results['anxiety'] += answer
            if answer == 1:
                results['goodScore'] += 2
            elif answer == 2:
                results['goodScore'] += 1
            elif answer == 3:
                results['neutralScore'] += 1
            elif answer == 4:
                results['badScore'] += 1
            else:
                results['badScore'] += 2
        else:
            return 0
    elif type == 5:
        answer = synonyms.isNumeric(answer)
        if answer:
            results['frustration'] += answer
            if answer == 1:
                results['goodScore'] += 2
            elif answer == 2:
                results['goodScore'] += 1
            elif answer == 3:
                results['neutralScore'] += 1
            elif answer == 4:
                results['badScore'] += 1
            else:
                results['badScore'] += 2
        else:
            return 0
    elif type == 6:
        answer = synonyms.isNumeric(answer)
        if answer:
            results['aggressiveness'] += answer
            if answer == 1:
                results['goodScore'] += 2
            elif answer == 2:
                results['goodScore'] += 1
            elif answer == 3:
                results['neutralScore'] += 1
            elif answer == 4:
                results['badScore'] += 1
            else:
                results['badScore'] += 2
        else:
            return 0
    else:
        answer = synonyms.isNumeric(answer)
        if answer:
            results['rigidity'] += answer
            if answer == 1:
                results['goodScore'] += 2
            elif answer == 2:
                results['goodScore'] += 1
            elif answer == 3:
                results['neutralScore'] += 1
            elif answer == 4:
                results['badScore'] += 1
            else:
                results['badScore'] += 2
        else:
            return 0

    updateResult(session, results)


def getAnswerNumber(session):
    return int(dbConnection.getAnswerNumber(session)[0][0])


def getResultsDict(session):
    results = dbConnection.getResults(session)
    resultsDict = dict()
    resultsDict['goodScore'] = int(results[0][0])
    resultsDict['neutralScore'] = int(results[0][1])
    resultsDict['badScore'] = int(results[0][2])
    resultsDict['anxiety'] = int(results[0][3])
    resultsDict['frustration'] = int(results[0][4])
    resultsDict['aggressiveness'] = int(results[0][5])
    resultsDict['rigidity'] = int(results[0][6])
    return resultsDict


def getLastQuestionText(session):
    id_q = int(dbConnection.getLastQuestion(session)[0][0])
    if id_q:
        return str(dbConnection.getQuestion(id_q)[0][0])
    else:
        return "Вы готовы начать проходить опрос для определения вашего настроения?"


def addSession(session):
    user = request.json.get('session', {}).get('user', {}).get('user_id')
    user_tuple = (user,)
    userIDs = dbConnection.getUsers()
    if user_tuple not in userIDs:
        dbConnection.addUser(user)

    dbConnection.addResult(0, 0, 0, 0, 0, 0, 0)
    from datetime import datetime
    date = datetime.now()
    id_res = str(dbConnection.getLastResult()[0][0])
    dbConnection.addSession(session, 1, date, user, id_res, 0, 0, 0)


def updateSession(session, isNew, isFinished, answerNumber):
    dbConnection.updateSession(session, isNew, isFinished, answerNumber)


def updateResult(session, results):
    id_result = str(dbConnection.getResult(session)[0][0])
    dbConnection.updateResult(id_result, results['goodScore'], results['neutralScore'], results['badScore'],
                              results['anxiety'], results['frustration'], results['aggressiveness'],
                              results['rigidity'])


def addFinalResult(session, result):
    dbConnection.addFinalResult(session, result)


def returnQuestion(answerNumber, session, results):
    if answerNumber == 1 or answerNumber == 4 or answerNumber == 7:
        return getBinaryQuestion(session, results)
    elif answerNumber == 2 or answerNumber == 5 or answerNumber == 8 or answerNumber == 9:
        return getRatingQuestion(answerNumber, session)
    elif answerNumber == 3 or answerNumber == 6:
        return getTextQuestion(session)


def getGreeting():
    idList = dbConnection.getGreetings()
    return returnAnswerText(idList)


def getGoodbye():
    idList = dbConnection.getGoodbye()
    return returnAnswerText(idList)


def getConclusion():
    idList = dbConnection.getConclusion()
    return returnAnswerText(idList)


def getGoodResult():
    idList = dbConnection.getGoodResult()
    return returnAnswerText(idList)


def getNeutralResult():
    idList = dbConnection.getNeutralResult()
    return returnAnswerText(idList)


def getNegativeResult():
    idList = dbConnection.getNegativeResult()
    return returnAnswerText(idList)

def getAnxiety(arrayId):
    # Получить текст вопроса по индексу
    textList = dbConnection.getAnswer(dbConnection.getAnswerByType(8)[arrayId][0])
    ans = textList[0]
    return str(ans[0])

def getFrustration(arrayId):
    # Получить текст вопроса по индексу
    textList = dbConnection.getAnswer(dbConnection.getAnswerByType(9)[arrayId][0])
    ans = textList[0]
    return str(ans[0])

def getAggressiveness(arrayId):
    # Получить текст вопроса по индексу
    textList = dbConnection.getAnswer(dbConnection.getAnswerByType(10)[arrayId][0])
    ans = textList[0]
    return str(ans[0])

def getRigidity(arrayId):
    # Получить текст вопроса по индексу
    textList = dbConnection.getAnswer(dbConnection.getAnswerByType(11)[arrayId][0])
    ans = textList[0]
    return str(ans[0])

def getMethodic():
    idList = dbConnection.getMethodic()
    return returnAnswerText(idList)

def getEnd():
    idList = dbConnection.getEnd()
    return returnAnswerText(idList)

def getHelp():
    # Получить текст вопроса по индексу
    textList = dbConnection.getAnswer(dbConnection.getAnswerByType(12)[0][0])
    ans = textList[0]
    return str(ans[0])


def getWhatCanYouDo():
    # Получить текст вопроса по индексу
    textList = dbConnection.getAnswer(dbConnection.getAnswerByType(13)[0][0])
    ans = textList[0]
    return str(ans[0])


def returnAnswerText(idList):
    # Выбрать случайный неповторяющийся индекс вопроса и записать его
    idRandom = random.choice(idList)

    # Получить текст вопроса по индексу
    textList = dbConnection.getAnswer(int(idRandom[0]))
    ans = textList[0]
    return str(ans[0])


# === Получить текстовый вопрос, который ранее не задавался пользователю ===
def getTextQuestion(session):
    # Получить индексы всех вопросов текстового типа
    idList = dbConnection.getIDTextQuestions()
    return returnQuestionText(idList, session)


# === Получить вопрос с ответом ДА/НЕТ, который ранее не задавался пользователю ===
def getBinaryQuestion(session, results):
    result = getMaxScore(results)
    # Получить индексы всех вопросов в зависимости от результата
    if result == "goodScore":
        idList = dbConnection.getIDBinaryGoodQuestions()
    elif result == "badScore":
        idList = dbConnection.getIDBinaryBadQuestions()
    else:
        if random.randint(0, 1):
            idList = dbConnection.getIDBinaryGoodQuestions()
        else:
            idList = dbConnection.getIDBinaryBadQuestions()

    return returnQuestionText(idList, session)


# === Получить числовой вопрос, который ранее не задавался пользователю ===
def getRatingQuestion(answerNumber, session):
    if answerNumber == 2:
        idList = dbConnection.getIDRatingAnxietyQuestions()
    elif answerNumber == 5:
        idList = dbConnection.getIDRatingFrustrationQuestions()
    elif answerNumber == 8:
        idList = dbConnection.getIDRatingAgressivnessQuestions()
    else:
        idList = dbConnection.getIDRatingRigidityQuestions()

    return returnQuestionText(idList, session)


def returnQuestionText(idList, session):
    # Выбрать случайный неповторяющийся индекс вопроса и записать его
    idRandom = random.choice(idList)
    usedIDs = dbConnection.getUsedQuestionIDs(session)
    if usedIDs != None:
        while idRandom in usedIDs:
            idRandom = random.choice(idList)

    dbConnection.addUsedQuestion(session, int(idRandom[0]))
    dbConnection.updateLastQuestionID(session, int(idRandom[0]))
    # Получить текст вопроса по индексу
    textList = dbConnection.getQuestion(int(idRandom[0]))
    question = textList[0]
    return str(question[0])


app.run('0.0.0.0', port=5000, debug=True)
