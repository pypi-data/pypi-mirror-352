from enum import Enum


class Language(Enum):
    KOREAN = "ko"
    RUSSIAN = "ru"
    GERMAN = "de"
    FRENCH = "fr"
    PORTUGUESE = "pt"
    CHINESE_SIMPLIFIED = "zh-hans"
    CHINESE_TRADITIONAL = "zh-hant"
    SPANISH = "es"
    ITALIAN = "it"
    POLISH = "pl"
    UKRAINIAN = "uk"
    ENGLISH = "en"

    def __str__(self):
        return self.value


class Platform(Enum):
    PC = "pc"
    PS4 = "ps4"
    XBOX = "xbox"
    SWITCH = "switch"
    MOBILE = "mobile"

    def __str__(self):
        return self.value
