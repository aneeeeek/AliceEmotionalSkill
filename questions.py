big_answer_questions = ["Расскажите, пожалуйста, в двух предложениях: как прошел Ваш день?",
              "Поделитесь в нескольких словах, что Вас сегодня порадовало за день?",
              "Скажите по секрету в нескольких словах, что Вам не понравилось в сегодняшнем дне?"]

no_yes_questions = ["Ответьте на утверждение ДА или НЕТ: вы чувствовали себя в целом хорошо за день",
                    "Ответьте на утверждение ДА или НЕТ: сегодня вы в печали"]

rate_questions = ["По шкале от 1 до 5, где 1 - очень плохо и 5 - очень хорошо, каким было ваше настроение сегодня?"]

def get_baq(id:int):
    return big_answer_questions[id]
def get_neq(id:int):
    return no_yes_questions[id]
def get_rq(id:int):
    return rate_questions[id]

def get_size_baq():
    return len(big_answer_questions)
def get_size_neq():
    return len(no_yes_questions)
def get_size_rq():
    return len(rate_questions)

