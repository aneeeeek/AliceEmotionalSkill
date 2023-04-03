greetings = ["Привет! Это навык для определения Вашего настроения. Распознав ваше эмоциональное состояние, я могу поделиться с вами советами по его улучшению. Ну что, продолжим?",
             "Приветствую! Этот навык может определять Ваше настроение, а затем я могу подсказать, как его улучшить. Хотите попробовать?"]


good_mood_answers = ["Вы чувствуете себя прекрасно, это здорово! Сохраняйте хороший настрой с собой"]

neutral_mood_answers = ["В целом, день был не очень насыщен эмоциями для вас"]

bad_mood_answers = ["Ой, кажется он злой, он очень плохой... Давайте успокоимся, все будет хорошо!"]

def getGreeting(id:int):
    return greetings[id]

def getGreetingsSize():
    return len(greetings)

def get_gma(id:int):
    return good_mood_answers[id]
def get_nma(id:int):
    return neutral_mood_answers[id]
def get_bma(id:int):
    return bad_mood_answers[id]