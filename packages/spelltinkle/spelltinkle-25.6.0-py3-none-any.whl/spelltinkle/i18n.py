import re


da = {
    'year': 'år',
    'years': 'år',
    'week': 'uge',
    'mo': 'ma',
    'tu': 'ti',
    'we': 'on',
    'th': 'to',
    'fr': 'fr',
    'sa': 'lø',
    'su': 'sø',
    'may': 'maj',
    'oct': 'okt',
    'modified': 'ændret',
    'me': 'mig',
    'from': 'fra',
    'to': 'til',
    'subject': 'emne',
    'archive': 'arkivér'}

de = {
    'year': 'Yahr',
    'years': 'Yahre',
    'mon': 'Mon',
    'tue': 'Die',
    'wed': 'Mit',
    'thu': 'Don',
    'fri': 'Fre',
    'sat': 'Sam',
    'sun': 'Son',
    'me': 'mich'}


words_in_languages = {
    'da_DK': {'hej', 'et', 'jeg', 'du', 'ikke', 'og', 'er', 'så'}}

dictionary = {}


def set_language(lang=None):
    global dictionary
    dictionary = da


def translate(word):
    return dictionary.get(word, word)


def guess_language(text: str) -> str:
    words = set(re.findall(r'\w+', text))
    for lang, examples in words_in_languages.items():
        for word in examples:
            if word in words:
                return lang
    return 'en_US'
