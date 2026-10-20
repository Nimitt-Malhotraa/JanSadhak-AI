import re

TOKEN_PATTERN = r"[\w\u0900-\u0963\u0966-\u097F]+"


def tokenize(text):
    return re.findall(TOKEN_PATTERN, text.lower())
