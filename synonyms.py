import re

agree = ["давай", "хорошо", "поехали", "погнали", "согласен", "согласна",
         "ок", "оке", "окей", "выкладывай", "да", "конечно", "ага", "угу",
         "готов", "готова", "хочу", "продолжим", "разумеется", "с удовольствием",
         "с радостью", "легко", "запросто", "могу", "буду", "точно", "именно", "определенно",
         "непременно", "безусловно", "вероятно", "возможно", "договорились", "уверен", "уверена",
         "несомненно", "однозначно", "го", "летс го"]

agree_ = ["не против", "не сомневаюсь", "без проблем"]

single_no = ["не", "нет", "неа"]

single_yes = ["да", "конечно", "ага", "угу", "ок", "оке", "окей", "давай", "хорошо", "согласен", "согласна"]

disagree = ["нет", "вряд ли", "сомневаюсь", "навряд ли", "против", "не согласен", "не согласна",
            "ни за что", "неа", "не окей", "не ок", "не оке", "не готов", "не готова", "не хочу", "не продолжим",
            "не могу", "не буду", "не думаю", "ни в коем случае", "не уверен", "не уверена", "не надо"]

disagree_ = ["да нет", "да нет наверное", "скорее нет чем да"]

exitText = ["выход", "выйди", "выйти", "хватит", "закончи", "алиса хватит", "алиса выход", "алиса выйди", "алиса выйти"
                                                                                                          "алиса закончи",
            "закончить", "алиса закончить", "заверши", "алиса заверши", "завершить", "алиса завершить",
            "достаточно", "алиса достаточно", "перестань", "алиса перестань", "прекрати", "алиса прекрати",
            "останови", "алиса останови", "остановись", "алиса остановись", "прекращай", "алиса прекращай",
            "прервись", "алиса прервись", "замолчи", "алиса замолчи", "заткнись", "алиса заткнись", "уймись",
            "алиса уймись", "утихни", "алиса утихни"]

repeatQuestionRegExp = r'(алиса )?(повтори|скажи)( вопрос)?( пожалуйста)?( еще раз| заново| снова)?'

one = ["1", "один", "единица", "единичка", "кол", "первое", "первый", "первая"]
two = ["2", "два", "двоечка", "двойка", "второе", "второй", "вторая"]
three = ["3", "три", "тройка", "троечка", "третье", "третий", "третья"]
four = ["4", "четыре", "четверка", "четверочка", "четвертое", "четвертый", "четвертая"]
five = ["5", "пять", "пятерка", "пятерочка", "пятое", "пятый", "пятая"]

helpText = ["алиса помоги", "помоги", "алиса помощь", "помощь", "не понял", "не поняла"]

whatCanDoText = ["что мне делать", "что делать", "что ты можешь", "что можешь", "что ты умеешь", "что умеешь",
                 "что ты сделаешь", "что сделаешь", "что ты делаешь", "что делаешь",
                 "в чем смысл", "в чем смысл навыка", "что делает навык", "что может навык"]

repeatSkill = ["начни заново", "начнем заново", "начни еще раз", "начнем еще раз",
               "начни с начала", "начни сначала", "начнем с начала", "начнем сначала",
               "начни снова", "начнем снова", "запусти навык сначала", "запусти сначала",
               "запусти навык с начала", "запусти с начала", "запусти навык снова", "запусти снова",
               "запусти навык еще раз", "запусти еще раз"]

statistics = ["посмотреть статистику", "посмотри статистику", "показать статистику", "покажи статистику",
              "посмотреть мою статистику", "посмотри мою статистику", "показать мою статистику",
              "покажи мою статистику",
              "статистика", "моя статистика", "статистику", "покажи все результаты", "показать все результаты",
              "посмотреть все результаты", "посмотри все результаты",
              "покажи мои результаты", "показать мои результаты",
              "посмотреть мои результаты", "посмотри мои результаты",
              "покажи результаты", "показать результаты", "посмотреть результаты", "посмотри результаты"]


def isAgree(text):
    if text in single_no:
        return 0
    elif text in single_yes:
        return 1
    else:
        for disagreeElement in disagree_:
            if disagreeElement in text:
                return 0

        for agreeElement in agree_:
            if agreeElement in text:
                return 1

        for d in disagree:
            if d in text:
                return 0

        for a in agree:
            if a in text:
                return 1

        return -1


def isExitText(text):
    return text in exitText


def isRepeatQuestion(text):
    return re.match(repeatQuestionRegExp, text)


def isNumeric(text):
    if text in one:
        return 1
    elif text in two:
        return 2
    elif text in three:
        return 3
    elif text in four:
        return 4
    elif text in five:
        return 5
    else:
        return 0


def isYesOrNo(text):
    if text in single_no:
        return 0
    elif text == single_yes[0] or text == single_yes[1] or text == single_yes[2] or text == single_yes[3]:
        return 1
    else:
        return -1


def isWhatCanDo(text):
    return text in whatCanDoText


def isHelp(text):
    return text in helpText


def isRepeatSkill(text):
    return text in repeatSkill


def isStatistic(text):
    return text in statistics
