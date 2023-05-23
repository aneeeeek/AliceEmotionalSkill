import random
import re

from flask import Flask, request
import answers
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
        return response("До встречи!", True)

    # пользователь просит повторить вопрос
    if synonyms.isRepeatQuestion(textWithoutPunctuation):
        return response(getLastQuestionText(session), False)

    # диалог с пользователем начался, сказать приветствие
    if isNewSession:
        return response(answers.getGreeting(random.randint(0, answers.getGreetingsSize() - 1)), False)

    # диалог с пользователем продолжается, задавать вопросы
    else:
        isAgree = synonyms.isAgree(text)
        if answerNumber == 0:
            if isAgree == 1:
                answerNumber += 1
                text = getTextQuestion(session)
                updateSession(session, 0, 0, answerNumber)
                return response(text, False)
            elif isAgree == 0:
                return response("Ну и пока", True)
            else:
                return response("Я не поняла ваш ответ, повторите, пожалуйста", False)

        elif answerNumber >= 1 and answerNumber <= 9:
            isAdded = addScore(text, session, results)
            if isAdded == 0:
                # todo переделать чтобы в зависимости от вопроса давались подсказки
                return response("неправильная форма ответа", False)
            else:
                question = returnQuestion(answerNumber, session, results)
                answerNumber += 1
                updateSession(session, 0, 0, answerNumber)
                return response(question, False)

        else:
            isAdded = addScore(text, session, results)
            if isAdded == 0:
                return response("Ответьте только числом от 1 до 5", False)
            else:
                updateSession(session, 0, 1, answerNumber)
                result = getMaxScore(results)

                allScore = "На основе анализа вашего настроения "
                if result == "goodScore":
                    addFinalResult(session, 'positive')
                    return response(
                        allScore + "можно сделать вывод, что Вы чувствуете себя хорошо! Сохраняйте позитивный настрой!",
                        True)  # закончить сессию
                elif result == "neutralScore":
                    addFinalResult(session, 'neutral')
                    return response(
                        allScore + "можно сделать вывод, что Вы чувствуете себя не так уж плохо! Все наладится, главное оставаться сильным!",
                        True)  # закончить сессию
                else:
                    addFinalResult(session, 'negative')
                    return response(
                        allScore + "можно сделать вывод, что Вы чувствуете себя плохо! Не бойтесь, черные полосы всегда проходят!",
                        True)  # закончить сессию


def response(text, end_session):
    return {
        'response':
            {
                'text': text,
                'end_session': end_session
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
    return str(dbConnection.getQuestion(id_q)[0][0])


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
