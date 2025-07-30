"""
Chyslivnyk - Бібліотека для генерації українських числівників у відповідній граматичній формі.

Підтримує:
- Кількісні числівники (цілі, збірні, дробові)
- Порядкові числівники
- Відмінки, роди, числа (де застосовно)
"""

# --- Константы для граматичних параметрів ---

# Відмінки
CASE_NOMINATIVE = "називний"  # Називний відмінок
CASE_GENITIVE = "родовий"  # Родовий відмінок
CASE_DATIVE = "давальний"  # Давальний відмінок
CASE_ACCUSATIVE = "знахідний"  # Знахідний відмінок
CASE_INSTRUMENTAL = "орудний"  # Орудний відмінок
CASE_LOCATIVE = "місцевий"  # Місцевий відмінок

# Роди
GENDER_MASCULINE = "чоловічий"  # Чоловічий рід
GENDER_FEMININE = "жіночий"  # Жіночий рід
GENDER_NEUTER = "середній"  # Середній рід

# Числа
NUMBER_SINGULAR = "однина"  # Однина
NUMBER_PLURAL = "множина"  # Множина


class Chyslivnyk:
    # --- Внутрішні словники для відмінювання ---
    # Зверніть увагу, що ці словники є базовими і можуть потребувати розширення
    # для абсолютної точності для всіх числівників та їх форм.

    _ONES = {
        0: "",  # Використовується як порожній рядок для формування складених
        1: {
            GENDER_MASCULINE: {CASE_NOMINATIVE: "один", CASE_GENITIVE: "одного", CASE_DATIVE: "одному",
                               CASE_ACCUSATIVE: "один", CASE_INSTRUMENTAL: "одним", CASE_LOCATIVE: "одному"},
            GENDER_FEMININE: {CASE_NOMINATIVE: "одна", CASE_GENITIVE: "однієї", CASE_DATIVE: "одній",
                              CASE_ACCUSATIVE: "одну", CASE_INSTRUMENTAL: "однією", CASE_LOCATIVE: "одній"},
            GENDER_NEUTER: {CASE_NOMINATIVE: "одне", CASE_GENITIVE: "одного", CASE_DATIVE: "одному",
                            CASE_ACCUSATIVE: "одне", CASE_INSTRUMENTAL: "одним", CASE_LOCATIVE: "одному"},
            NUMBER_PLURAL: {CASE_NOMINATIVE: "одні", CASE_GENITIVE: "одних", CASE_DATIVE: "одним",
                            CASE_ACCUSATIVE: "одні",
                            CASE_INSTRUMENTAL: "одними", CASE_LOCATIVE: "одних"}
        },
        2: {
            GENDER_MASCULINE: {CASE_NOMINATIVE: "два", CASE_GENITIVE: "двох", CASE_DATIVE: "двом",
                               CASE_ACCUSATIVE: "два",
                               CASE_INSTRUMENTAL: "двома", CASE_LOCATIVE: "двох"},
            GENDER_FEMININE: {CASE_NOMINATIVE: "дві", CASE_GENITIVE: "двох", CASE_DATIVE: "двом",
                              CASE_ACCUSATIVE: "дві",
                              CASE_INSTRUMENTAL: "двома", CASE_LOCATIVE: "двох"},
            GENDER_NEUTER: {CASE_NOMINATIVE: "два", CASE_GENITIVE: "двох", CASE_DATIVE: "двом", CASE_ACCUSATIVE: "два",
                            CASE_INSTRUMENTAL: "двома", CASE_LOCATIVE: "двох"},
        },
        3: {CASE_NOMINATIVE: "три", CASE_GENITIVE: "трьох", CASE_DATIVE: "трьом", CASE_ACCUSATIVE: "три",
            CASE_INSTRUMENTAL: "трьома", CASE_LOCATIVE: "трьох"},
        4: {CASE_NOMINATIVE: "чотири", CASE_GENITIVE: "чотирьох", CASE_DATIVE: "чотирьом", CASE_ACCUSATIVE: "чотири",
            CASE_INSTRUMENTAL: "чотирма", CASE_LOCATIVE: "чотирьох"},
        5: {CASE_NOMINATIVE: "п'ять", CASE_GENITIVE: "п'яти", CASE_DATIVE: "п'яти", CASE_ACCUSATIVE: "п'ять",
            CASE_INSTRUMENTAL: "п'ятьма", CASE_LOCATIVE: "п'яти"},
        6: {CASE_NOMINATIVE: "шість", CASE_GENITIVE: "шести", CASE_DATIVE: "шести", CASE_ACCUSATIVE: "шість",
            CASE_INSTRUMENTAL: "шістьма", CASE_LOCATIVE: "шести"},
        7: {CASE_NOMINATIVE: "сім", CASE_GENITIVE: "семи", CASE_DATIVE: "семи", CASE_ACCUSATIVE: "сім",
            CASE_INSTRUMENTAL: "сімома", CASE_LOCATIVE: "семи"},
        8: {CASE_NOMINATIVE: "вісім", CASE_GENITIVE: "восьми", CASE_DATIVE: "восьми", CASE_ACCUSATIVE: "вісім",
            CASE_INSTRUMENTAL: "вісьмома", CASE_LOCATIVE: "восьми"},
        9: {CASE_NOMINATIVE: "дев'ять", CASE_GENITIVE: "дев'яти", CASE_DATIVE: "дев'яти", CASE_ACCUSATIVE: "дев'ять",
            CASE_INSTRUMENTAL: "дев'ятьма", CASE_LOCATIVE: "дев'яти"}
    }

    _TEENS = {
        10: {CASE_NOMINATIVE: "десять", CASE_GENITIVE: "десяти", CASE_DATIVE: "десяти", CASE_ACCUSATIVE: "десять",
             CASE_INSTRUMENTAL: "десятьма", CASE_LOCATIVE: "десяти"},
        11: {CASE_NOMINATIVE: "одинадцять", CASE_GENITIVE: "одинадцяти", CASE_DATIVE: "одинадцяти",
             CASE_ACCUSATIVE: "одинадцять", CASE_INSTRUMENTAL: "одинадцятьма", CASE_LOCATIVE: "одинадцяти"},
        12: {CASE_NOMINATIVE: "дванадцять", CASE_GENITIVE: "дванадцяти", CASE_DATIVE: "дванадцяти",
             CASE_ACCUSATIVE: "дванадцять", CASE_INSTRUMENTAL: "дванадцятьма", CASE_LOCATIVE: "дванадцяти"},
        13: {CASE_NOMINATIVE: "тринадцять", CASE_GENITIVE: "тринадцяти", CASE_DATIVE: "тринадцяти",
             CASE_ACCUSATIVE: "тринадцять", CASE_INSTRUMENTAL: "тринадцятьма", CASE_LOCATIVE: "тринадцяти"},
        14: {CASE_NOMINATIVE: "чотирнадцять", CASE_GENITIVE: "чотирнадцяти", CASE_DATIVE: "чотирнадцяти",
             CASE_ACCUSATIVE: "чотирнадцять", CASE_INSTRUMENTAL: "чотирнадцятьма", CASE_LOCATIVE: "чотирнадцяти"},
        15: {CASE_NOMINATIVE: "п'ятнадцять", CASE_GENITIVE: "п'ятнадцяти", CASE_DATIVE: "п'ятнадцяти",
             CASE_ACCUSATIVE: "п'ятнадцять", CASE_INSTRUMENTAL: "п'ятнадцятьма", CASE_LOCATIVE: "п'ятнадцяти"},
        16: {CASE_NOMINATIVE: "шістнадцять", CASE_GENITIVE: "шістнадцяти", CASE_DATIVE: "шістнадцяти",
             CASE_ACCUSATIVE: "шістнадцять", CASE_INSTRUMENTAL: "шістнадцятьма", CASE_LOCATIVE: "шістнадцяти"},
        17: {CASE_NOMINATIVE: "сімнадцять", CASE_GENITIVE: "сімнадцяти", CASE_DATIVE: "сімнадцяти",
             CASE_ACCUSATIVE: "сімнадцять", CASE_INSTRUMENTAL: "сімнадцятьма", CASE_LOCATIVE: "сімнадцяти"},
        18: {CASE_NOMINATIVE: "вісімнадцять", CASE_GENITIVE: "вісімнадцяти", CASE_DATIVE: "вісімнадцяти",
             CASE_ACCUSATIVE: "вісімнадцять", CASE_INSTRUMENTAL: "вісімнадцятьма", CASE_LOCATIVE: "вісімнадцяти"},
        19: {CASE_NOMINATIVE: "дев'ятнадцять", CASE_GENITIVE: "дев'ятнадцяти", CASE_DATIVE: "дев'ятнадцяти",
             CASE_ACCUSATIVE: "дев'ятнадцять", CASE_INSTRUMENTAL: "дев'ятнадцятьма", CASE_LOCATIVE: "дев'ятнадцяти"}
    }

    _TENS = {
        20: {CASE_NOMINATIVE: "двадцять", CASE_GENITIVE: "двадцяти", CASE_DATIVE: "двадцяти",
             CASE_ACCUSATIVE: "двадцять",
             CASE_INSTRUMENTAL: "двадцятьма", CASE_LOCATIVE: "двадцяти"},
        30: {CASE_NOMINATIVE: "тридцять", CASE_GENITIVE: "тридцяти", CASE_DATIVE: "тридцяти",
             CASE_ACCUSATIVE: "тридцять",
             CASE_INSTRUMENTAL: "тридцятьма", CASE_LOCATIVE: "тридцяти"},
        40: {CASE_NOMINATIVE: "сорок", CASE_GENITIVE: "сорока", CASE_DATIVE: "сорока", CASE_ACCUSATIVE: "сорок",
             CASE_INSTRUMENTAL: "сорока", CASE_LOCATIVE: "сорока"},
        50: {CASE_NOMINATIVE: "п'ятдесят", CASE_GENITIVE: "п'ятдесяти", CASE_DATIVE: "п'ятдесяти",
             CASE_ACCUSATIVE: "п'ятдесят", CASE_INSTRUMENTAL: "п'ятдесятьма", CASE_LOCATIVE: "п'ятдесяти"},
        60: {CASE_NOMINATIVE: "шістдесят", CASE_GENITIVE: "шістдесяти", CASE_DATIVE: "шістдесяти",
             CASE_ACCUSATIVE: "шістдесят", CASE_INSTRUMENTAL: "шістдесятьма", CASE_LOCATIVE: "шістдесяти"},
        70: {CASE_NOMINATIVE: "сімдесят", CASE_GENITIVE: "сімдесяти", CASE_DATIVE: "сімдесяти",
             CASE_ACCUSATIVE: "сімдесят",
             CASE_INSTRUMENTAL: "сімдесятьма", CASE_LOCATIVE: "сімдесяти"},
        80: {CASE_NOMINATIVE: "вісімдесят", CASE_GENITIVE: "вісімдесяти", CASE_DATIVE: "вісімдесяти",
             CASE_ACCUSATIVE: "вісімдесят", CASE_INSTRUMENTAL: "вісімдесятьма", CASE_LOCATIVE: "вісімдесяти"},
        90: {CASE_NOMINATIVE: "дев'яносто", CASE_GENITIVE: "дев'яноста", CASE_DATIVE: "дев'яноста",
             CASE_ACCUSATIVE: "дев'яносто", CASE_INSTRUMENTAL: "дев'яноста", CASE_LOCATIVE: "дев'яноста"}
    }

    _HUNDREDS = {
        100: {CASE_NOMINATIVE: "сто", CASE_GENITIVE: "ста", CASE_DATIVE: "ста", CASE_ACCUSATIVE: "сто",
              CASE_INSTRUMENTAL: "ста", CASE_LOCATIVE: "ста"},
        200: {CASE_NOMINATIVE: "двісті", CASE_GENITIVE: "двохсот", CASE_DATIVE: "двомстам", CASE_ACCUSATIVE: "двісті",
              CASE_INSTRUMENTAL: "двомастами", CASE_LOCATIVE: "двохстах"},
        300: {CASE_NOMINATIVE: "триста", CASE_GENITIVE: "трьохсот", CASE_DATIVE: "трьомстам", CASE_ACCUSATIVE: "триста",
              CASE_INSTRUMENTAL: "трьомастами", CASE_LOCATIVE: "трьохстах"},
        400: {CASE_NOMINATIVE: "чотириста", CASE_GENITIVE: "чотирьохсот", CASE_DATIVE: "чотирьомстам",
              CASE_ACCUSATIVE: "чотириста", CASE_INSTRUMENTAL: "чотирмастами", CASE_LOCATIVE: "чотирьохстах"},
        500: {CASE_NOMINATIVE: "п'ятсот", CASE_GENITIVE: "п'ятисот", CASE_DATIVE: "п'ятистам",
              CASE_ACCUSATIVE: "п'ятсот",
              CASE_INSTRUMENTAL: "п'ятьмастами", CASE_LOCATIVE: "п'ятистах"},
        600: {CASE_NOMINATIVE: "шістсот", CASE_GENITIVE: "шестисот", CASE_DATIVE: "шестистам",
              CASE_ACCUSATIVE: "шістсот",
              CASE_INSTRUMENTAL: "шістьмастами", CASE_LOCATIVE: "шестистах"},
        700: {CASE_NOMINATIVE: "сімсот", CASE_GENITIVE: "семисот", CASE_DATIVE: "семистам", CASE_ACCUSATIVE: "сімсот",
              CASE_INSTRUMENTAL: "сімомастами", CASE_LOCATIVE: "семистах"},
        800: {CASE_NOMINATIVE: "вісімсот", CASE_GENITIVE: "восьмисот", CASE_DATIVE: "восьмистам",
              CASE_ACCUSATIVE: "вісімсот", CASE_INSTRUMENTAL: "вісьмомастами", CASE_LOCATIVE: "восьмистах"},
        900: {CASE_NOMINATIVE: "дев'ятсот", CASE_GENITIVE: "дев'ятисот", CASE_DATIVE: "дев'ятистам",
              CASE_ACCUSATIVE: "дев'ятсот", CASE_INSTRUMENTAL: "дев'ятьмастами", CASE_LOCATIVE: "дев'ятистах"}
    }

    _THOUSANDS = {
        CASE_NOMINATIVE: "тисяча", CASE_GENITIVE: "тисячі", CASE_DATIVE: "тисячі",
        CASE_ACCUSATIVE: "тисячу", CASE_INSTRUMENTAL: "тисячею", CASE_LOCATIVE: "тисячі"
    }

    _MILLIONS = {
        CASE_NOMINATIVE: "мільйон", CASE_GENITIVE: "мільйона", CASE_DATIVE: "мільйону",
        CASE_ACCUSATIVE: "мільйон", CASE_INSTRUMENTAL: "мільйоном", CASE_LOCATIVE: "мільйоні"
    }

    _BILLIONS = {
        CASE_NOMINATIVE: "мільярд", CASE_GENITIVE: "мільярда", CASE_DATIVE: "мільярду",
        CASE_ACCUSATIVE: "мільярд", CASE_INSTRUMENTAL: "мільярдом", CASE_LOCATIVE: "мільярді"
    }

    _TRILLIONS = {
        CASE_NOMINATIVE: "трильйон", CASE_GENITIVE: "трильйона", CASE_DATIVE: "трильйону",
        CASE_ACCUSATIVE: "трильйон", CASE_INSTRUMENTAL: "трильйоном", CASE_LOCATIVE: "трильйоні"
    }

    _THOUSAND_ENDING = {'root': "тисяч", 'ending_1': "а", 'ending_2_4': "і", 'ending_5': ""}
    _MILLION_ENDING = {'root': "мільйон", 'ending_1': "", 'ending_2_4': "и", 'ending_5': "ів"}
    _BILLION_ENDING = {'root': "мільярд", 'ending_1': "", 'ending_2_4': "и", 'ending_5': "ів"}
    _TRILLION_ENDING = {'root': "трильйон", 'ending_1': "", 'ending_2_4': "и", 'ending_5': "ів"}

    _COLLECTIVE = {
        2: {CASE_NOMINATIVE: "двоє", CASE_GENITIVE: "двох", CASE_DATIVE: "двом", CASE_ACCUSATIVE: "двоє",
            CASE_INSTRUMENTAL: "двома", CASE_LOCATIVE: "двох"},
        3: {CASE_NOMINATIVE: "троє", CASE_GENITIVE: "трьох", CASE_DATIVE: "трьом", CASE_ACCUSATIVE: "троє",
            CASE_INSTRUMENTAL: "трьома", CASE_LOCATIVE: "трьох"},
        4: {CASE_NOMINATIVE: "четверо", CASE_GENITIVE: "чотирьох", CASE_DATIVE: "чотирьом", CASE_ACCUSATIVE: "четверо",
            CASE_INSTRUMENTAL: "чотирма", CASE_LOCATIVE: "чотирьох"},
        5: {CASE_NOMINATIVE: "п'ятеро", CASE_GENITIVE: "п'ятьох", CASE_DATIVE: "п'ятьом", CASE_ACCUSATIVE: "п'ятеро",
            CASE_INSTRUMENTAL: "п'ятьма", CASE_LOCATIVE: "п'ятьох"},
        6: {CASE_NOMINATIVE: "шестеро", CASE_GENITIVE: "шістьох", CASE_DATIVE: "шістьом", CASE_ACCUSATIVE: "шестеро",
            CASE_INSTRUMENTAL: "шістьма", CASE_LOCATIVE: "шістьох"},
        7: {CASE_NOMINATIVE: "семеро", CASE_GENITIVE: "сімох", CASE_DATIVE: "сімом", CASE_ACCUSATIVE: "семеро",
            CASE_INSTRUMENTAL: "сімома", CASE_LOCATIVE: "сімох"},
        8: {CASE_NOMINATIVE: "восьмеро", CASE_GENITIVE: "вісьмох", CASE_DATIVE: "вісьмом", CASE_ACCUSATIVE: "восьмеро",
            CASE_INSTRUMENTAL: "вісьмома", CASE_LOCATIVE: "вісьмох"},
        9: {CASE_NOMINATIVE: "дев'ятеро", CASE_GENITIVE: "дев'ятьох", CASE_DATIVE: "дев'ятьом",
            CASE_ACCUSATIVE: "дев'ятеро", CASE_INSTRUMENTAL: "дев'ятьма", CASE_LOCATIVE: "дев'ятьох"},
        10: {CASE_NOMINATIVE: "десятеро", CASE_GENITIVE: "десятьох", CASE_DATIVE: "десятьом",
             CASE_ACCUSATIVE: "десятеро",
             CASE_INSTRUMENTAL: "десятьма", CASE_LOCATIVE: "десятьох"},
    }

    # Словник для порядкових числівників (базові форми та відмінки)
    # Важливо: Для складених порядкових числівників відмінюється лише останнє слово.
    # Тому тут зберігаємо лише форми для "простих" порядкових або тих, що змінюють основу.
    _ORDINALS_BASES = {
        1: "перш",
        2: "друг",
        3: "трет",
        4: "четверт",
        5: "п'ят",
        6: "шост",
        7: "сьом",
        8: "восьм",
        9: "дев'ят",
        10: "десят",
        11: "одинадцят",
        12: "дванадцят",
        13: "тринадцят",
        14: "чотирнадцят",
        15: "п'ятнадцят",
        16: "шістнадцят",
        17: "сімнадцят",
        18: "вісімнадцят",
        19: "дев'ятнадцят",
        20: "двадцят",
        30: "тридцят",
        40: "сорок",  # Особливий випадок
        50: "п'ятдесят",  # Особливий випадок, відмінюється як складний
        60: "шістдесят",  # те саме
        70: "сімдесят",  # те саме
        80: "вісімдесят",  # те саме
        90: "дев'яност",  # Особливий випадок
        100: "сот",
        200: "двохсот",
        300: "трьохсот",
        400: "чотирьохсот",
        500: "п'ятисот",
        600: "шестисот",
        700: "семисот",
        800: "восьмисот",
        900: "дев'ятисот",
        1000: "тисячн",
        1000000: "мільйонн",
        1000000000: "мільярдн",
        1000000000000: "трильйонн",
    }

    # Закінчення порядкових числівників за родами, числами та відмінками
    _ORDINAL_ENDINGS = {
        GENDER_MASCULINE: {
            CASE_NOMINATIVE: "ий",
            CASE_GENITIVE: "ого",
            CASE_DATIVE: "ому",
            CASE_ACCUSATIVE: "ий",  # для неістот, для істот як Р.в.
            CASE_INSTRUMENTAL: "им",
            CASE_LOCATIVE: "ому"
        },
        GENDER_FEMININE: {
            CASE_NOMINATIVE: "а",
            CASE_GENITIVE: "ої",
            CASE_DATIVE: "ій",
            CASE_ACCUSATIVE: "у",
            CASE_INSTRUMENTAL: "ою",
            CASE_LOCATIVE: "ій"
        },
        GENDER_NEUTER: {
            CASE_NOMINATIVE: "е",
            CASE_GENITIVE: "ого",
            CASE_DATIVE: "ому",
            CASE_ACCUSATIVE: "е",
            CASE_INSTRUMENTAL: "им",
            CASE_LOCATIVE: "ому"
        },
        NUMBER_PLURAL: {
            CASE_NOMINATIVE: "і",
            CASE_GENITIVE: "их",
            CASE_DATIVE: "им",
            CASE_ACCUSATIVE: "і",  # для неістот, для істот як Р.в.
            CASE_INSTRUMENTAL: "ими",
            CASE_LOCATIVE: "их"
        }
    }

    # Винятки для ORDINAL_ENDINGS для деяких чисел (наприклад, "третій", "третя", "третє")
    _ORDINAL_SPECIAL_ENDINGS = {
        3: {
            GENDER_MASCULINE: {CASE_NOMINATIVE: "третій", CASE_GENITIVE: "третього", CASE_DATIVE: "третьому",
                               CASE_ACCUSATIVE: "третій", CASE_INSTRUMENTAL: "третім", CASE_LOCATIVE: "третьому"},
            GENDER_FEMININE: {CASE_NOMINATIVE: "третя", CASE_GENITIVE: "третьої", CASE_DATIVE: "третій",
                              CASE_ACCUSATIVE: "третю", CASE_INSTRUMENTAL: "третьою", CASE_LOCATIVE: "третій"},
            GENDER_NEUTER: {CASE_NOMINATIVE: "третє", CASE_GENITIVE: "третього", CASE_DATIVE: "третьому",
                            CASE_ACCUSATIVE: "третє", CASE_INSTRUMENTAL: "третім", CASE_LOCATIVE: "третьому"},
            NUMBER_PLURAL: {CASE_NOMINATIVE: "треті", CASE_GENITIVE: "третіх", CASE_DATIVE: "третім",
                            CASE_ACCUSATIVE: "треті", CASE_INSTRUMENTAL: "третіми", CASE_LOCATIVE: "третіх"}
        },
        # Для 40 (сороковий), 90 (дев'яностий), 100 (сотий)
        40: {  # Сороковий
            GENDER_MASCULINE: {CASE_NOMINATIVE: "сороковий", CASE_GENITIVE: "сорокового", CASE_DATIVE: "сороковому",
                               CASE_ACCUSATIVE: "сороковий", CASE_INSTRUMENTAL: "сороковим",
                               CASE_LOCATIVE: "сороковому"},
            GENDER_FEMININE: {CASE_NOMINATIVE: "сорокова", CASE_GENITIVE: "сорокової", CASE_DATIVE: "сороковій",
                              CASE_ACCUSATIVE: "сорокову", CASE_INSTRUMENTAL: "сороковою", CASE_LOCATIVE: "сороковій"},
            GENDER_NEUTER: {CASE_NOMINATIVE: "сорокове", CASE_GENITIVE: "сорокового", CASE_DATIVE: "сороковому",
                            CASE_ACCUSATIVE: "сорокове", CASE_INSTRUMENTAL: "сороковим", CASE_LOCATIVE: "сороковому"},
            NUMBER_PLURAL: {CASE_NOMINATIVE: "сорокові", CASE_GENITIVE: "сорокових", CASE_DATIVE: "сороковим",
                            CASE_ACCUSATIVE: "сорокові", CASE_INSTRUMENTAL: "сороковими", CASE_LOCATIVE: "сорокових"}
        },
        90: {  # Дев'яностий
            GENDER_MASCULINE: {CASE_NOMINATIVE: "дев'яностий", CASE_GENITIVE: "дев'яностого",
                               CASE_DATIVE: "дев'яностому",
                               CASE_ACCUSATIVE: "дев'яностий", CASE_INSTRUMENTAL: "дев'яностим",
                               CASE_LOCATIVE: "дев'яностому"},
            GENDER_FEMININE: {CASE_NOMINATIVE: "дев'яноста", CASE_GENITIVE: "дев'яностої", CASE_DATIVE: "дев'яностій",
                              CASE_ACCUSATIVE: "дев'яносту", CASE_INSTRUMENTAL: "дев'яностою",
                              CASE_LOCATIVE: "дев'яностій"},
            GENDER_NEUTER: {CASE_NOMINATIVE: "дев'яносте", CASE_GENITIVE: "дев'яностого", CASE_DATIVE: "дев'яностому",
                            CASE_ACCUSATIVE: "дев'яносте", CASE_INSTRUMENTAL: "дев'яностим",
                            CASE_LOCATIVE: "дев'яностому"},
            NUMBER_PLURAL: {CASE_NOMINATIVE: "дев'яності", CASE_GENITIVE: "дев'яностих", CASE_DATIVE: "дев'яностим",
                            CASE_ACCUSATIVE: "дев'яності", CASE_INSTRUMENTAL: "дев'яностими",
                            CASE_LOCATIVE: "дев'яностих"}
        },
        100: {  # Сотий
            GENDER_MASCULINE: {CASE_NOMINATIVE: "сотий", CASE_GENITIVE: "сотого", CASE_DATIVE: "сотому",
                               CASE_ACCUSATIVE: "сотий", CASE_INSTRUMENTAL: "сотим", CASE_LOCATIVE: "сотому"},
            GENDER_FEMININE: {CASE_NOMINATIVE: "сота", CASE_GENITIVE: "сотої", CASE_DATIVE: "сотій",
                              CASE_ACCUSATIVE: "соту", CASE_INSTRUMENTAL: "сотою", CASE_LOCATIVE: "сотій"},
            GENDER_NEUTER: {CASE_NOMINATIVE: "соте", CASE_GENITIVE: "сотого", CASE_DATIVE: "сотому",
                            CASE_ACCUSATIVE: "соте", CASE_INSTRUMENTAL: "сотим", CASE_LOCATIVE: "сотому"},
            NUMBER_PLURAL: {CASE_NOMINATIVE: "соті", CASE_GENITIVE: "сотих", CASE_DATIVE: "сотим",
                            CASE_ACCUSATIVE: "соті",
                            CASE_INSTRUMENTAL: "сотими", CASE_LOCATIVE: "сотих"}
        }
    }

    # --- Допоміжні функції для перевірки аргументів ---

    @staticmethod
    def _validate_case(case):
        """Перевіряє, чи є відмінок дійсним."""
        valid_cases = [CASE_NOMINATIVE, CASE_GENITIVE, CASE_DATIVE,
                       CASE_ACCUSATIVE, CASE_INSTRUMENTAL, CASE_LOCATIVE]
        if case not in valid_cases:
            raise ValueError(f"Недійсний відмінок: '{case}'. Допустимі: {', '.join(valid_cases)}")

    @staticmethod
    def _validate_gender(gender):
        """Перевіряє, чи є рід дійсним."""
        valid_genders = [GENDER_MASCULINE, GENDER_FEMININE, GENDER_NEUTER]
        if gender not in valid_genders:
            raise ValueError(f"Недійсний рід: '{gender}'. Допустимі: {', '.join(valid_genders)}")

    @staticmethod
    def _validate_number_type(number_type):
        """Перевіряє, чи є тип числа дійсним."""
        valid_number_types = [NUMBER_SINGULAR, NUMBER_PLURAL]
        if number_type not in valid_number_types:
            raise ValueError(f"Недійсний тип числа: '{number_type}'. Допустимі: {', '.join(valid_number_types)}")

    # --- Внутрішні функції для відмінювання цілих чисел ---

    @staticmethod
    def _incline_hundreds(num, case):
        """Відмінює сотні (100-900)."""
        if num not in Chyslivnyk._HUNDREDS:
            # Це має бути відловлено раніше або це виняток для цієї функції
            raise ValueError(f"Невідоме число для сотень: {num}")
        return Chyslivnyk._HUNDREDS[num].get(case)

    @staticmethod
    def _incline_tens(num, case):
        """Відмінює десятки (20-90)."""
        if num not in Chyslivnyk._TENS:
            raise ValueError(f"Невідоме число для десятків: {num}")
        return Chyslivnyk._TENS[num].get(case)

    @staticmethod
    def _incline_teens(num, case):
        """Відмінює числа від 10 до 19."""
        if num not in Chyslivnyk._TEENS:
            raise ValueError(f"Невідоме число для чисел 10-19: {num}")
        return Chyslivnyk._TEENS[num].get(case)

    @staticmethod
    def _incline_ones(num, case, gender=None, number_type=NUMBER_SINGULAR):
        """Відмінює одиниці (1-9)."""
        if num not in Chyslivnyk._ONES:
            raise ValueError(f"Невідоме число для одиниць: {num}")

        if num == 1:
            if number_type == NUMBER_PLURAL:
                return Chyslivnyk._ONES[1][NUMBER_PLURAL].get(case)
            if gender not in Chyslivnyk._ONES[1]:
                # Цей виняток має бути оброблений на рівні `get_cardinal`
                raise ValueError(
                    f"Для числа 1 обов'язково вкажіть рід: {GENDER_MASCULINE}, {GENDER_FEMININE} або {GENDER_NEUTER}")
            return Chyslivnyk._ONES[1][gender].get(case)
        elif num == 2:
            if gender == GENDER_FEMININE:
                return Chyslivnyk._ONES[2][GENDER_FEMININE].get(case)
            return Chyslivnyk._ONES[2][GENDER_MASCULINE].get(case)  # Чоловічий та середній рід
        return Chyslivnyk._ONES[num].get(case)

    @staticmethod
    def _get_cardinal_part(num, case, gender=GENDER_MASCULINE):
        """
        Допоміжна функція для генерації частини кількісного числівника.
        Обробляє числа до 999.
        """
        if not (0 <= num < 1000):
            raise ValueError("Число має бути в діапазоні від 0 до 999 для цієї функції.")

        parts = []

        if num >= 100:
            hundreds = (num // 100) * 100
            parts.append(Chyslivnyk._incline_hundreds(hundreds, case))
            num %= 100

        if num >= 10 and num < 20:
            parts.append(Chyslivnyk._incline_teens(num, case))
        elif num >= 20:
            tens = (num // 10) * 10
            parts.append(Chyslivnyk._incline_tens(tens, case))
            num %= 10

        if num > 0 and num < 10:
            if num == 1 or num == 2:  # 1 та 2 мають особливості за родом
                parts.append(Chyslivnyk._incline_ones(num, case, gender=gender))
            else:
                parts.append(Chyslivnyk._incline_ones(num, case))

        return " ".join(filter(None, parts))  # Видаляємо порожні рядки

    @staticmethod
    def _get_significant_magnitude(number):
        """
        Returns the significance of the last non-zero digit of a number.

        Args:
            number (int or float): The input number.

        Returns:
            str: A string indicating the magnitude (0, 1, 2,
                 3, 4).
        """
        number = abs(number)  # Work with the absolute value for magnitude

        if 0 <= number <= 999:
            return 0
        elif 1000 <= number <= 999_999:
            return 1
        elif 1_000_000 <= number <= 999_999_999:
            return 2
        elif 1_000_000_000 <= number <= 999_999_999_999:
            return 3
        elif 1_000_000_000_000 <= number <= 999_999_999_999_999:  # Up to just under a quadrillion for trillions
            return 4
        else:
            return 5  # You might want to handle larger numbers or define a limit

    @staticmethod
    def _get_correct_ending(n: int, ending_rules: dict) -> str:
        """
        Повертає коректне закінчення для числівника на основі числа та правил відмінювання.

        Args:
            n (int): Число, для якого потрібно визначити закінчення.
            ending_rules (dict): Словник з правилами відмінювання (наприклад, THOUSAND_ENDING).

        Returns:
            str: Коректне закінчення.
        """
        if not isinstance(n, int) or n < 0:
            raise ValueError("Число має бути невід'ємним цілим числом.")

        # Обробка останніх двох цифр для чисел від 1 до 20
        last_two_digits = n % 100
        if 10 <= last_two_digits <= 20:
            return ending_rules['root'] + ending_rules['ending_5']

        # Обробка останньої цифри
        last_digit = n % 10

        if last_digit == 1:
            return ending_rules['root'] + ending_rules['ending_1']
        elif 2 <= last_digit <= 4:
            return ending_rules['root'] + ending_rules['ending_2_4']
        else:  # last_digit == 0 or last_digit > 4
            return ending_rules['root'] + ending_rules['ending_5']

        # --- Основні функції бібліотеки ---

    @staticmethod
    def get_cardinal(number: int, case: str = CASE_NOMINATIVE, gender: str = GENDER_MASCULINE) -> str:
        """
        Генерує цілий кількісний числівник у вказаній граматичній формі.

        :param number: Ціле число (наприклад, 1, 25, 100).
        :param case: Відмінок (CASE_NOMINATIVE, CASE_GENITIVE, etc.). За замовчуванням: називний.
        :param gender: Рід (GENDER_MASCULINE, GENDER_FEMININE, GENDER_NEUTER). Застосовно для 1, 2.
                       За замовчуванням: чоловічий.
        :return: Рядок з числівником.
        :raises TypeError: Якщо `number` не є цілим числом.
        :raises ValueError: Якщо `number` від'ємне або `case` недійсний.
        """
        if not isinstance(number, int):
            raise TypeError("Число повинно бути цілим (int).")
        if number < 0:
            raise ValueError("Число не може бути від'ємним для кількісних числівників.")

        Chyslivnyk._validate_case(case)
        Chyslivnyk._validate_gender(gender)  # Перевіряємо, хоча використовується не завжди

        if number == 0:
            return "нуль"  # Нуль не відмінюється за родами чи числами

        magnitude = Chyslivnyk._get_significant_magnitude(number)

        original_number = number

        parts = []
        # Обробка числа по розрядах (тисячі, мільйони тощо)
        # Ця частина є спрощеною і не повністю реалізує відмінювання "тисяча", "мільйон" тощо.
        # Для повної реалізації потрібна значно складніша логіка відмінювання груп.
        # Тут я реалізую базову логіку для невеликих чисел та просту конкатенацію для великих.

        # Обробка трильйонів
        if number >= 1_000_000_000_000:
            if original_number == 1_000_000_000_000:
                return Chyslivnyk._TRILLIONS[case]
            tri = number // 1_000_000_000_000

            parts.append(Chyslivnyk._get_cardinal_part(tri, CASE_NOMINATIVE, gender=GENDER_MASCULINE))
            parts.append(Chyslivnyk._get_correct_ending(tri, Chyslivnyk._TRILLION_ENDING))

            number %= 1_000_000_000_000

        # Обробка мільярдів
        if number >= 1_000_000_000:
            if original_number == 1_000_000_000:
                return Chyslivnyk._BILLIONS[case]
            bil = number // 1_000_000_000

            parts.append(Chyslivnyk._get_cardinal_part(bil, CASE_NOMINATIVE, gender=GENDER_MASCULINE))
            parts.append(Chyslivnyk._get_correct_ending(bil, Chyslivnyk._BILLION_ENDING))

            number %= 1_000_000_000

        # Обробка мільйонів
        if number >= 1_000_000:
            if original_number == 1_000_000:
                return Chyslivnyk._MILLIONS[case]

            mil = number // 1_000_000
            parts.append(Chyslivnyk._get_cardinal_part(mil, CASE_NOMINATIVE, gender=GENDER_MASCULINE))
            parts.append(Chyslivnyk._get_correct_ending(mil, Chyslivnyk._MILLION_ENDING))

            number %= 1_000_000

        # Обробка тисяч
        if number >= 1_000:
            if original_number == 1_000:
                return Chyslivnyk._THOUSANDS[case]
            thou = number // 1_000

            parts.append(Chyslivnyk._get_cardinal_part(thou, CASE_NOMINATIVE, gender=GENDER_FEMININE))
            parts.append(Chyslivnyk._get_correct_ending(thou, Chyslivnyk._THOUSAND_ENDING))

            number %= 1_000

        if number > 0:
            parts.append(Chyslivnyk._get_cardinal_part(number, case, gender))

        return " ".join(filter(None, parts)).strip()

    @staticmethod
    def get_collective(number: int, case: str = CASE_NOMINATIVE) -> str:
        """
        Генерує збірний числівник у вказаному відмінку.
        Підтримує числа від 2 до 10 (для повноти словника).

        :param number: Ціле число (2-10).
        :param case: Відмінок (CASE_NOMINATIVE, CASE_GENITIVE, etc.). За замовчуванням: називний.
        :return: Рядок зі збірним числівником.
        :raises TypeError: Якщо `number` не є цілим числом.
        :raises ValueError: Якщо `number` не в діапазоні 2-10 або `case` недійсний.
        """
        if not isinstance(number, int):
            raise TypeError("Число повинно бути цілим (int).")
        # Додано підтримку до 20 для збірних, але словник поки тільки до 10.
        if not (2 <= number <= 20):
            # Якщо треба підтримувати більше, треба розширювати _COLLECTIVE
            raise ValueError("Збірні числівники підтримуються лише для чисел від 2 до 20.")

        Chyslivnyk._validate_case(case)

        if number not in Chyslivnyk._COLLECTIVE:
            # Для чисел, що не в словнику (наприклад, 11-19)
            # можна було б додати логіку для "одинадцятеро", "дванадцятеро" тощо,
            # але це вимагає розширення _COLLECTIVE або загальної логіки.
            raise ValueError(f"Збірний числівник для числа {number} не знайдено в словнику.")

        return Chyslivnyk._COLLECTIVE[number].get(case, Chyslivnyk._COLLECTIVE[number][CASE_NOMINATIVE])

    @staticmethod
    def get_fractional(numerator: int, denominator: int, case: str = CASE_NOMINATIVE,
                       gender: str = GENDER_FEMININE) -> str:
        """
        Генерує дробовий числівник у вказаній граматичній формі.
        Підтримує лише прості дроби.

        :param numerator: Чисельник (ціле число).
        :param denominator: Знаменник (ціле число, не 0).
        :param case: Відмінок (CASE_NOMINATIVE, CASE_GENITIVE, etc.). За замовчуванням: називний.
        :param gender: Рід знаменника для правильного узгодження (GENDER_FEMININE, GENDER_MASCULINE, GENDER_NEUTER).
                       За замовчуванням: жіночий (як у "одна друга").
        :return: Рядок з дробовим числівником.
        :raises TypeError: Якщо чисельник або знаменник не є цілим числом.
        :raises ValueError: Якщо знаменник 0 або `case` недійсний.
        """
        if not isinstance(numerator, int) or not isinstance(denominator, int):
            raise TypeError("Чисельник та знаменник повинні бути цілими числами (int).")
        if denominator == 0:
            raise ValueError("Знаменник не може бути нулем.")
        if numerator < 0:
            raise ValueError("Чисельник не може бути від'ємним для дробових числівників.")
        if denominator < 0:
            raise ValueError("Знаменник не може бути від'ємним.")

        Chyslivnyk._validate_case(case)
        Chyslivnyk._validate_gender(gender)

        if numerator == 0:
            return "нуль"

        # Ціла частина
        if numerator >= denominator and numerator % denominator == 0:
            return Chyslivnyk.get_cardinal(numerator // denominator, case=case, gender=gender)

        # Дробова частина
        num_str = Chyslivnyk.get_cardinal(numerator, case=case, gender=gender)  # Чисельник як кількісний

        # Знаменник як порядковий числівник
        # Після 1 чисельника - знаменник у однині (одна друга)
        # Після 2, 3, 4 чисельників - знаменник у множині (дві третіх)
        # Після 5+ чисельників - знаменник у множині родового відмінка (п'ять восьмих)
        if numerator == 1:
            denom_word = Chyslivnyk.get_ordinal(denominator, case=case, gender=gender, number_type=NUMBER_SINGULAR)
        elif 2 <= numerator <= 4:
            if case == CASE_NOMINATIVE:
                case = CASE_GENITIVE
            # Для 2,3,4 чисельників знаменник залишається в називному множини
            # Але його форма має бути як у Р.в. множини
            # Наприклад: "дві третіх", "чотири п'ятих"
            # Це вимагає обробки як порядкового числівника у родовому відмінку множини
            denom_word = Chyslivnyk.get_ordinal(denominator, case=case, number_type=NUMBER_PLURAL)
        else:  # > 4
            if case == CASE_NOMINATIVE:
                case = CASE_GENITIVE
            denom_word = Chyslivnyk.get_ordinal(denominator, case=case, number_type=NUMBER_PLURAL)

        return f"{num_str} {denom_word}"

    @staticmethod
    def get_decimal_fractional(number: float, case: str = CASE_NOMINATIVE, gender: str = None) -> str:
        """
        Генерує дробовий числівник з десяткового дробу.

        :param number: Десятковий дріб (наприклад, 0.25, 3.14).
        :param case: Відмінок (CASE_NOMINATIVE, CASE_GENITIVE, etc.). За замовчуванням: називний.
        :param gender: Рід (GENDER_FEMININE, GENDER_MASCULINE, GENDER_NEUTER). Застосовно для цілої частини та останнього слова дробу.
                       За замовчуванням: жіночий.
        :return: Рядок з дробовим числівником.
        :raises TypeError: Якщо `number` не є числом з плаваючою комою.
        :raises ValueError: Якщо `case` недійсний.
        """
        if not isinstance(number, (float, int)):
            raise TypeError("Число повинно бути числом (float або int).")

        Chyslivnyk._validate_case(case)

        if number == 0:
            return "нуль"

        int_part = int(number)
        frac_part_abs = abs(number - int_part)

        if gender is None:
            if frac_part_abs > 0:
                gender = GENDER_FEMININE
            else:
                gender = GENDER_MASCULINE

        Chyslivnyk._validate_gender(gender)

        result_parts = []

        # Обробка цілої частини
        if int_part != 0:
            card_int_part = Chyslivnyk.get_cardinal(int_part, case=case, gender=gender)
            result_parts.append(card_int_part)
        else:
            result_parts.append('нуль цілих')

        flag_1_2 = False

        is_1_or_2 = (int_part % 10 == 1) or (int_part % 10 == 2)
        not_11_12 = (int_part != 11) and (int_part != 12)

        if is_1_or_2 and not_11_12:
            flag_1_2 = True

        # Обробка дробової частини
        if frac_part_abs > 0:
            s = str(number)
            # Знаходимо кількість цифр після коми
            if '.' in s:
                decimal_places = len(s) - s.find('.') - 1
                # Обмежуємо кількість знаків після коми для уникнення проблем з float
                # Наприклад, 0.3 може бути 0.29999999999999999.
                # Округлюємо до 5 знаків після коми, щоб уникнути помилок перетворення
                # float на numerator/denominator для простих випадків.
                if decimal_places > 5:
                    decimal_places = 5
                numerator_frac = int(round(frac_part_abs * (10 ** decimal_places)))
                denominator_frac = 10 ** decimal_places
            else:  # Якщо число було цілим, але передано як float (напр. 5.0)
                numerator_frac = 0
                denominator_frac = 1

            if numerator_frac > 0:
                if result_parts:  # Якщо є ціла частина, додаємо "цілих"

                    if flag_1_2:
                        if gender == GENDER_MASCULINE:
                            if case == CASE_NOMINATIVE or case == CASE_ACCUSATIVE:
                                result_parts.append("ціле")
                            elif case == CASE_GENITIVE:
                                result_parts.append("цілого")
                            elif case == CASE_DATIVE:
                                result_parts.append("цілому")
                            elif case == CASE_INSTRUMENTAL:
                                result_parts.append("цілим")
                            elif case == CASE_LOCATIVE:
                                result_parts.append("цілому")
                            else:  # За замовчуванням
                                result_parts.append("ціле")

                        if gender == GENDER_FEMININE:
                            if case == CASE_NOMINATIVE:
                                result_parts.append("ціла")
                            elif case == CASE_GENITIVE:
                                result_parts.append("цілої")
                            elif case == CASE_DATIVE:
                                result_parts.append("цілій")
                            elif case == CASE_ACCUSATIVE:
                                result_parts.append("цілу")
                            elif case == CASE_INSTRUMENTAL:
                                result_parts.append("цілою")
                            elif case == CASE_LOCATIVE:
                                result_parts.append("цілій")
                            else:  # За замовчуванням
                                result_parts.append("ціла")

                    else:
                        if int_part != 0:
                            # Якщо десятковий дріб починається на нуль, то частина цілих не відмінюється. В інших випадках вона відмінюється:
                            if case == CASE_NOMINATIVE or case == CASE_ACCUSATIVE:
                                result_parts.append("цілих")
                            elif case == CASE_GENITIVE:
                                result_parts.append("цілих")
                            elif case == CASE_DATIVE:
                                result_parts.append("цілим")
                            elif case == CASE_INSTRUMENTAL:
                                result_parts.append("цілими")
                            elif case == CASE_LOCATIVE:
                                result_parts.append("цілих")
                            else:  # За замовчуванням
                                result_parts.append("цілих")

                frac_str = Chyslivnyk.get_fractional(numerator_frac, denominator_frac, case=case, gender=gender)
                result_parts.append(frac_str)

        return " ".join(result_parts).strip()

    @staticmethod
    def _get_ordinal_in_form(num, case, gender, number_type, clear=True):
        """
        Допоміжна функція для генерації порядкового числівника.
        Обробляє числа рекурсивно, відмінюючи лише останнє слово для складених.
        """
        if num == 0:
            # Для нуля
            if number_type == NUMBER_SINGULAR:
                if gender == GENDER_MASCULINE: return "нульовий"
                if gender == GENDER_FEMININE: return "нульова"
                if gender == GENDER_NEUTER: return "нульове"
            return "нульові"  # Множина

        # Спеціальні випадки (третій, сороковий, дев'яностий, сотий)
        if num in Chyslivnyk._ORDINAL_SPECIAL_ENDINGS:
            target_dict = Chyslivnyk._ORDINAL_SPECIAL_ENDINGS[num]
            if number_type == NUMBER_PLURAL:
                return target_dict[NUMBER_PLURAL].get(case)
            else:
                return target_dict[gender].get(case)

        # Обробка складених порядкових числівників
        # Відмінюється лише останнє слово
        if num >= 1000000000000:  # Трильйони
            prefix_num = num // 1000000000000
            remainder = num % 1000000000000
            prefix_word = Chyslivnyk.get_cardinal(prefix_num, case=CASE_NOMINATIVE)  # Попередні слова в називному
            # Останнє слово в цьому випадку "трильйонний"
            last_word_base = Chyslivnyk._ORDINALS_BASES[1000000000000]
            last_word = last_word_base + (
                Chyslivnyk._ORDINAL_ENDINGS[number_type].get(case) if number_type == NUMBER_PLURAL else
                Chyslivnyk._ORDINAL_ENDINGS[
                    gender].get(
                    case))
            if remainder == 0:
                if prefix_num == 1 and clear == True:
                    return f"{last_word}"
                else:
                    return f"{prefix_word} {last_word}"
            else:
                if prefix_num == 1 and clear == True:
                    return f"{Chyslivnyk._TRILLIONS[CASE_NOMINATIVE]} {Chyslivnyk._get_ordinal_in_form(remainder, case, gender, number_type, clear=False)}"
                else:
                    return f"{prefix_word} {Chyslivnyk._TRILLIONS[CASE_NOMINATIVE]} {Chyslivnyk._get_ordinal_in_form(remainder, case, gender, number_type, clear=False)}"

        if num >= 1000000000:  # Мільярди
            prefix_num = num // 1000000000
            remainder = num % 1000000000
            prefix_word = Chyslivnyk.get_cardinal(prefix_num, case=CASE_NOMINATIVE)  # Попередні слова в називному
            last_word_base = Chyslivnyk._ORDINALS_BASES[1000000000]
            last_word = last_word_base + (
                Chyslivnyk._ORDINAL_ENDINGS[number_type].get(case) if number_type == NUMBER_PLURAL else
                Chyslivnyk._ORDINAL_ENDINGS[
                    gender].get(
                    case))
            if remainder == 0:
                if prefix_num == 1 and clear == True:
                    return f"{last_word}"
                else:
                    return f"{prefix_word} {last_word}"
            else:
                if prefix_num == 1 and clear == True:
                    return f"{Chyslivnyk._BILLIONS[CASE_NOMINATIVE]} {Chyslivnyk._get_ordinal_in_form(remainder, case, gender, number_type, clear=False)}"
                else:
                    return f"{prefix_word} {Chyslivnyk._BILLIONS[CASE_NOMINATIVE]} {Chyslivnyk._get_ordinal_in_form(remainder, case, gender, number_type, clear=False)}"

        if num >= 1000000:  # Мільйони
            prefix_num = num // 1000000
            remainder = num % 1000000
            prefix_word = Chyslivnyk.get_cardinal(prefix_num, case=CASE_NOMINATIVE)  # Попередні слова в називному
            last_word_base = Chyslivnyk._ORDINALS_BASES[1000000]
            last_word = last_word_base + (
                Chyslivnyk._ORDINAL_ENDINGS[number_type].get(case) if number_type == NUMBER_PLURAL else
                Chyslivnyk._ORDINAL_ENDINGS[
                    gender].get(
                    case))
            if remainder == 0:
                if prefix_num == 1 and clear == True:
                    return f"{last_word}"
                else:
                    return f"{prefix_word} {last_word}"
            else:
                if prefix_num == 1 and clear == True:
                    return f"{Chyslivnyk._MILLIONS[CASE_NOMINATIVE]} {Chyslivnyk._get_ordinal_in_form(remainder, case, gender, number_type, clear=False)}"
                else:
                    return f"{prefix_word} {Chyslivnyk._MILLIONS[CASE_NOMINATIVE]} {Chyslivnyk._get_ordinal_in_form(remainder, case, gender, number_type, clear=False)}"

        if num >= 1000:  # Тисячі
            prefix_num = num // 1000
            remainder = num % 1000
            prefix_word = Chyslivnyk.get_cardinal(prefix_num, case=CASE_NOMINATIVE,
                                                  gender=GENDER_FEMININE)  # Попередні слова в називному
            last_word_base = Chyslivnyk._ORDINALS_BASES[1000]
            last_word = last_word_base + (
                Chyslivnyk._ORDINAL_ENDINGS[number_type].get(case) if number_type == NUMBER_PLURAL else
                Chyslivnyk._ORDINAL_ENDINGS[
                    gender].get(
                    case))
            if remainder == 0:
                if prefix_num == 1 and clear == True:
                    return f"{last_word}"
                else:
                    return f"{prefix_word} {last_word}"
            else:
                return f"{prefix_word} {Chyslivnyk._THOUSANDS[CASE_NOMINATIVE]} {Chyslivnyk._get_ordinal_in_form(remainder, case, gender, number_type, clear=False)}"

        if num >= 100:  # Сотні
            prefix_num = (num // 100) * 100  # Отримуємо 100, 200, 300...
            remainder = num % 100
            if prefix_num in Chyslivnyk._ORDINAL_SPECIAL_ENDINGS:  # Для 100
                prefix_word = Chyslivnyk._ORDINAL_SPECIAL_ENDINGS[prefix_num][gender].get(
                    case) if number_type == NUMBER_SINGULAR else \
                    Chyslivnyk._ORDINAL_SPECIAL_ENDINGS[prefix_num][NUMBER_PLURAL].get(case)
            else:
                # Для 200-900, які не в _ORDINAL_SPECIAL_ENDINGS, треба генерувати їхній порядковий
                # "двохсотий", "трьохсотий"
                base = Chyslivnyk._ORDINALS_BASES[prefix_num]  # напр., "двохсот"
                prefix_word = base + (
                    Chyslivnyk._ORDINAL_ENDINGS[number_type].get(case) if number_type == NUMBER_PLURAL else
                    Chyslivnyk._ORDINAL_ENDINGS[
                        gender].get(case))

            if remainder == 0:  # Якщо число рівно 100, 200, 300
                return prefix_word
            else:
                # Для 101, 256, 321...
                # Наприклад, "сто двадцять перший" - "сто" залишається в називному
                hundreds_cardinal_part = Chyslivnyk._get_cardinal_part(prefix_num, CASE_NOMINATIVE)  # "сто", "двісті"
                last_part = Chyslivnyk._get_ordinal_in_form(remainder, case, gender, number_type, clear=False)
                return f"{hundreds_cardinal_part} {last_part}"

        if num >= 20:  # Десятки та одиниці (20-99)
            tens_val = (num // 10) * 10
            remainder = num % 10
            if remainder == 0:  # Якщо число рівно 20, 30, ...
                if tens_val in Chyslivnyk._ORDINAL_SPECIAL_ENDINGS:  # 40, 90
                    target_dict = Chyslivnyk._ORDINAL_SPECIAL_ENDINGS[tens_val]
                    return target_dict[number_type].get(case) if number_type == NUMBER_PLURAL else target_dict[
                        gender].get(
                        case)
                # Для інших: двадцятий, тридцятий
                base = Chyslivnyk._ORDINALS_BASES[tens_val]
                return base + (
                    Chyslivnyk._ORDINAL_ENDINGS[number_type].get(case) if number_type == NUMBER_PLURAL else
                    Chyslivnyk._ORDINAL_ENDINGS[
                        gender].get(case))
            else:  # Складені: двадцять перший
                tens_cardinal_part = Chyslivnyk._get_cardinal_part(tens_val, CASE_NOMINATIVE)  # "двадцять", "тридцять"
                last_part = Chyslivnyk._get_ordinal_in_form(remainder, case, gender, number_type)
                return f"{tens_cardinal_part} {last_part}"

        if num >= 10:  # Числа 10-19
            if num in Chyslivnyk._ORDINAL_SPECIAL_ENDINGS:  # Сюди поки нічого не потрапляє з 10-19
                target_dict = Chyslivnyk._ORDINAL_SPECIAL_ENDINGS[num]
                return target_dict[number_type].get(case) if number_type == NUMBER_PLURAL else target_dict[gender].get(
                    case)

            base = Chyslivnyk._ORDINALS_BASES[num]
            return base + (
                Chyslivnyk._ORDINAL_ENDINGS[number_type].get(case) if number_type == NUMBER_PLURAL else
                Chyslivnyk._ORDINAL_ENDINGS[
                    gender].get(
                    case))

        if num > 0:  # Одиниці 1-9
            if num in Chyslivnyk._ORDINAL_SPECIAL_ENDINGS:  # 3-й
                target_dict = Chyslivnyk._ORDINAL_SPECIAL_ENDINGS[num]
                return target_dict[number_type].get(case) if number_type == NUMBER_PLURAL else target_dict[gender].get(
                    case)

            base = Chyslivnyk._ORDINALS_BASES[num]
            # Для 1, 2, 5, 6, 7, 8, 9
            return base + (
                Chyslivnyk._ORDINAL_ENDINGS[number_type].get(case) if number_type == NUMBER_PLURAL else
                Chyslivnyk._ORDINAL_ENDINGS[
                    gender].get(
                    case))

        return ""  # Заглушка, якщо число не оброблено

    @staticmethod
    def get_ordinal(number: int, case: str = CASE_NOMINATIVE, gender: str = GENDER_MASCULINE,
                    number_type: str = NUMBER_SINGULAR) -> str:
        """
        Генерує порядковий числівник у вказаній граматичній формі.

        :param number: Ціле число (наприклад, 1, 7, 25).
        :param case: Відмінок (CASE_NOMINATIVE, CASE_GENITIVE, etc.). За замовчуванням: називний.
        :param gender: Рід (GENDER_MASCULINE, GENDER_FEMININE, GENDER_NEUTER). За замовчуванням: чоловічий.
        :param number_type: Число (NUMBER_SINGULAR, NUMBER_PLURAL). За замовчуванням: однина.
        :return: Рядок з числівником.
        :raises TypeError: Якщо `number` не є цілим числом.
        :raises ValueError: Якщо `number` від'ємне або `case`/`gender`/`number_type` недійсні.
        """
        if not isinstance(number, int):
            raise TypeError("Число повинно бути цілим (int).")
        if number < 0:
            raise ValueError("Число не може бути від'ємним для порядкових числівників.")

        Chyslivnyk._validate_case(case)
        Chyslivnyk._validate_gender(gender)
        Chyslivnyk._validate_number_type(number_type)

        return Chyslivnyk._get_ordinal_in_form(number, case, gender, number_type)
