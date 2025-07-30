from requests.utils import requote_uri
from wowool.infobox.config import config
from wowool.annotation import Concept


def get_language_code(language):
    return config.get_language_code(language)


def convert_args(input: str | Concept):
    if isinstance(input, str):
        return (input, requote_uri(input))
    return (input.canonical, requote_uri(input.canonical))
