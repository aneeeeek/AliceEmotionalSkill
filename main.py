import random
from flask import Flask, request
import questions
import answers
import enum

from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel

questionNumber = 0

app = Flask(__name__)

goodScore, neutralScore, badScore = 0, 0, 0

@app.route("/alice", methods=["POST"])
def main():
    global questionNumber
    text = request.json.get('request', {}).get('original_utterance')

    # диалог с пользователем начался
    if request.json.get('session', {}).get('new'):
        return response(answers.getGreeting(random.randint(0, answers.getGreetingsSize()-1)), False)

    # диалог с пользователем продолжается
    else:

        if questionNumber == 0:
            if text.lower() == 'давай': # TODO синонимы
                questionNumber += 1  # перейти к следующему вопросу
                # TODO сделать случайный вопрос из текста чтобы не повторялся - так везде
                return response(questions.get_baq(random.randint(0, questions.get_size_baq()-1)), False)
            else:
                return response("Ну и пока", True) # закончить сессию

        elif questionNumber == 1:
            # TODO сохранить текстовый ответ, передать в нейронку, начислить очки
            print(getSentiment(text))
            questionNumber += 1  # перейти к следующему вопросу
            return response(questions.get_neq(random.randint(0, questions.get_size_neq()-1)), False)
        elif questionNumber == 2:
            # TODO сохранить да/нет/возможно ответ, начислить очки, проверить что сказал то что нужно - если нет, попросить повторить ответ в заданной форме
            questionNumber += 1  # перейти к следующему вопросу
            return response(questions.get_rq(random.randint(0, questions.get_size_rq()-1)), False)
        elif questionNumber == 3:
            # TODO сохранить числовой ответ, начислить очки, проверить что сказал то что нужно - если нет, попросить повторить ответ в заданной форме
            questionNumber += 1  # перейти к следующему вопросу
            return response(questions.get_baq(random.randint(0, questions.get_size_baq()-1)), False)
        elif questionNumber == 4:
            # TODO сохранить текстовый ответ, передать в нейронку, начислить очки
            getSentiment(text)
            questionNumber += 1  # перейти к следующему вопросу
            return response(questions.get_rq(random.randint(0, questions.get_size_rq()-1)), False)
        elif questionNumber == 5:
            # TODO сохранить числовой ответ, начислить очки, проверить что сказал то что нужно - если нет, попросить повторить ответ в заданной форме
            questionNumber += 1  # перейти к следующему вопросу
            return response(questions.get_neq(random.randint(0, questions.get_size_neq()-1)), False)
        elif questionNumber == 6:
            # TODO сохранить да/нет/возможно ответ, начислить очки, проверить что сказал то что нужно - если нет, попросить повторить ответ в заданной форме
            questionNumber += 1  # перейти к следующему вопросу
            return response(questions.get_neq(random.randint(0, questions.get_size_neq()-1)), False)
        else:
            # TODO сохранить да/нет/возможно ответ, начислить очки, проверить что сказал то что нужно - если нет, попросить повторить ответ в заданной форме

            # TODO посчитать результаты, объявить их
            return response("Ну в общем ты грустный, не грусти", True)  # закончить сессию



def response(text, end_session):
    return {
        'response':
            {
                'text': text,
                'end_session': end_session
            },
        'version': '1.0'
    }

def getSentiment(text):
    tokenizer = RegexTokenizer()
    model = FastTextSocialNetworkModel(tokenizer=tokenizer)
    result = model.predict([text.lower()], k=1)
    print(result)
    return list(result[0].keys()).pop(0)


app.run('0.0.0.0', port=5000, debug=True)