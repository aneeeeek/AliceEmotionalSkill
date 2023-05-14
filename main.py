import random
from flask import Flask, request
import questions
import answers
import enum

from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel

answerNumber = 0

app = Flask(__name__)

goodScore, neutralScore, badScore = 0, 0, 0
textID_arr, yesNoGoodID_arr, yesNoBadID_arr, numberID_arr= [], [], [], []

@app.route("/alice", methods=["POST"])
def main():
    global answerNumber
    text = request.json.get('request', {}).get('original_utterance')
    # todo проверять, тот ли пользователь проходит тест
    # todo сделать графики после статистики
    # todo проверить че будет если я напишу текст на английском)))))))))

    if isExitText(text):
        return response("До встречи!", True)

    # TODO присваивать баллы в текстовом в зависимости от уверенности нейронки ???

    # диалог с пользователем начался
    if request.json.get('session', {}).get('new'):
        return response(answers.getGreeting(random.randint(0, answers.getGreetingsSize() - 1)), False)

    # диалог с пользователем продолжается
    else:

        # ответ на вопрос о прохождении навыка
        if answerNumber == 0:
            if text.lower() == 'давай':
                answerNumber += 1
                id = random.randint(0, questions.get_size_baq() - 1)
                textID_arr.append(id)
                return response(questions.get_baq(id), False)
            else:
                return response("Ну и пока", True)

        # ответ на текстовый вопрос 1
        elif answerNumber == 1:
            addScoreForText(getSentiment(text))
            answerNumber += 1
            return responseFromScore()

        # ответ на вопрос да/нет/возможно 1
        elif answerNumber == 2:
            if text == 'да' or text=='нет':
                #addScoreForYesNo(text)
                answerNumber += 1
                return response(questions.get_rq(random.randint(0, questions.get_size_rq() - 1)), False)
            else:
                return response("Ответьте словами ДА или НЕТ", False)

        # ответ на вопрос числом 1
        elif answerNumber == 3:
            if text.isnumeric():
                if 5 >= int(text) >= 1:
                    addScoreForNumeric(int(text))
                    answerNumber += 1
                    return response(questions.get_baq(random.randint(0, questions.get_size_baq() - 1)), False)
            else:
                return response("Ответьте целым числом в заданном диапазоне: от 1 до 5", False)

        # ответ на текстовый вопрос 2
        elif answerNumber == 4:
            addScoreForText(getSentiment(text))
            getSentiment(text)
            answerNumber += 1
            return response(questions.get_rq(random.randint(0, questions.get_size_rq() - 1)), False)

        # ответ на вопрос числом 2
        elif answerNumber == 5:
            if text.isnumeric():
                if 5 >= int(text) >= 1:
                    addScoreForNumeric(int(text))
                    answerNumber += 1
                    # TODO посмотреть на скоры и в зависимости от них задать следующий вопрос
                    return response(questions.get_neq_good(random.randint(0, questions.get_size_neq_good() - 1)), False)
            else:
                return response("Ответьте целым числом в заданном диапазоне: от 1 до 5", False)

        # ответ на вопрос да/нет/возможно 2
        elif answerNumber == 6:
            # TODO проверить что сказал то что нужно - если нет, попросить повторить ответ в заданной форме
            answerNumber += 1
            # TODO посмотреть на скоры и в зависимости от них задать следующий вопрос
            return response(questions.get_neq_good(random.randint(0, questions.get_size_neq_good() - 1)), False)

        # ответ на вопрос да/нет/возможно 3
        else:
            # TODO проверить что сказал то что нужно - если нет, попросить повторить ответ в заданной форме


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

def responseFromScore():
    result = getMaxScore(goodScore,neutralScore,badScore)
    if result == "goodScore":
        while 1:
            id = random.randint(0, questions.get_size_neq_good() - 1)
            if id not in yesNoGoodID_arr:
                yesNoGoodID_arr.append(id)
                return response(questions.get_neq_good(id), False)
    elif result == "badScore":
        while 1:
            id = random.randint(0, questions.get_size_neq_bad() - 1)
            if id not in yesNoBadID_arr:
                yesNoBadID_arr.append(id)
                return response(questions.get_neq_bad(id), False)
    else:
        res = random.randint(0, 1)
        if res == 0:
            while 1:
                id = random.randint(0, questions.get_size_neq_good() - 1)
                if id not in yesNoGoodID_arr:
                    yesNoGoodID_arr.append(id)
                    return response(questions.get_neq_good(id), False)
        else:
            while 1:
                id = random.randint(0, questions.get_size_neq_bad() - 1)
                if id not in yesNoBadID_arr:
                    yesNoBadID_arr.append(id)
                    return response(questions.get_neq_bad(id), False)


def getSentiment(text):
    tokenizer = RegexTokenizer()
    model = FastTextSocialNetworkModel(tokenizer=tokenizer)
    result = model.predict([text.lower()], k=1)
    return list(result[0].keys()).pop(0)


def addScoreForText(result):
    global goodScore, neutralScore, badScore
    if result == 'positive':
        goodScore += 1
    elif result == 'neutral':
        neutralScore += 1
    elif result == 'negative':
        badScore += 1
    else:
        neutralScore += 0.5


def addScoreForNumeric(result):
    global goodScore, neutralScore, badScore
    if result == 5 or result == 4:
        goodScore += result
    elif result == 3:
        neutralScore += result
    elif result == 1 or result == 2:
        badScore += result

#def addScoreForYesNo(result):


app.run('0.0.0.0', port=5000, debug=True)
