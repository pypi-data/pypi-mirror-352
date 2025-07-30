import json
from jsonschema import validate as jsonschema_validate, ValidationError


SECTOR_MAPPINGS = {
    "artificial intelligence": "ai",
    "clothing retail": "fashion",
    "financial services": "financials",
    "investments": "financials",
    "lodging": "hospitality",
}

ATTRIBUTE_INDUSTRY = {"name": "sector", "formatter": "lower", "mappings": SECTOR_MAPPINGS}

POSITION_MAPPINGS = {
    "short story writer": "writer",
}

ATTRIBUTE_HEADQUARTERS = {"name": "headquarters"}
ATTRIBUTE_ALIAS = {"name": "alias", "split": ",", "exclude": "(.+ )?others"}
ATTRIBUTE_DESCRIPTION = {"regex": "(.+),.+"}
ATTRIBUTE_POSSITION = {
    "name": "position",
    "formatter": "lower",
    "split": ",",
    "mappings": POSITION_MAPPINGS,
}
ATTRIBUTE_CATEGORY = {"name": "category", "formatter": "lower"}
FIND_PEOPLE = {"pipeline": "entity", "uri": "Person"}
CAPTURE_PERSON = {
    "to": "Person",
    "attributes": {
        "wiki_type": {
            "name": "company",
            "formatter": "lower",
        },
    },
}

ATTRIBUTE_KEY_PEOPLE = {
    "find": FIND_PEOPLE,
    "convert": CAPTURE_PERSON,
}

EN_DEFAULT_URIS = {
    "Person": {
        "occupation": ATTRIBUTE_POSSITION,
        "occupations": ATTRIBUTE_POSSITION,
        "occupation(s)": ATTRIBUTE_POSSITION,
        "canonical": {},
        "birth_name": {"name": "alias", **ATTRIBUTE_KEY_PEOPLE},
        "also_known_as": {"name": "alias", **ATTRIBUTE_KEY_PEOPLE},
        "political_party": {"formatter": "lower"},
        "position": ATTRIBUTE_POSSITION,
        "short_description": [
            {"name": "country", "uri": "PlaceAdj.country"},
            {"name": "country", "uri": "Country"},
        ],
        # "short_description": [{"name": "country", "uri": "PlaceAdj.country", "formatter": "lower", "mappings": {"uk": "Greate Brittain"}}],
    },
    "Company": {
        "industry": ATTRIBUTE_INDUSTRY,
        "canonical": {},
        "headquarters": ATTRIBUTE_HEADQUARTERS,
        "key_people": ATTRIBUTE_KEY_PEOPLE,
        "wiki_candidates": [{"pattern": r"(.+)", "replacement": r"\1_Inc"}, {"pattern": r"(.+)", "replacement": r"\1_\(company\)"}],
        "website": {"name": "website"},
    },
    "Event": {
        "_conditions": ["initial_caps"],
        "location": {},
        "type": ATTRIBUTE_CATEGORY,
    },
    "Publisher": {
        "industry": ATTRIBUTE_INDUSTRY,
        "canonical": {},
        "headquarters": ATTRIBUTE_HEADQUARTERS,
        "key_people": ATTRIBUTE_KEY_PEOPLE,
    },
    "Organization": {
        "abbreviation": {"name": "abbr", "split": ",", "formatter": "upper"},
        "type": ATTRIBUTE_CATEGORY,
        "canonical": {},
        "headquarters": ATTRIBUTE_HEADQUARTERS,
        "secretary_general": ATTRIBUTE_KEY_PEOPLE,
        "executive_director": {},
    },
    "Product": {
        "developer": {"name": "company"},
        "type": ATTRIBUTE_CATEGORY,
    },
    "Place": {
        "short_description": [
            {"name": "country", "uri": "PlaceAdj.country"},
            {"name": "country", "uri": "Country"},
        ]
    },
    "Weapon": {
        "developer": {"name": "company"},
        "type": ATTRIBUTE_CATEGORY,
    },
    "Drug": {
        "other_names": ATTRIBUTE_ALIAS,
        "trade_names": ATTRIBUTE_ALIAS,
        "description": ATTRIBUTE_DESCRIPTION,
        "type": ATTRIBUTE_CATEGORY,
    },
    "UnknownThing": {
        "other_names": ATTRIBUTE_ALIAS,
        "trade_names": ATTRIBUTE_ALIAS,
        "headquarters": ATTRIBUTE_HEADQUARTERS,
        "description": ATTRIBUTE_DESCRIPTION,
        "canonical": {"formatter": "none"},
        "occupation": ATTRIBUTE_POSSITION,
        "occupations": ATTRIBUTE_POSSITION,
    },
}


DEFAULT_URIS = {
    "english": EN_DEFAULT_URIS,
}

# print(json.dumps(DEFAULT_URIS, indent=2))

json_schema = json_schema = {
    "type": "object",
    "patternProperties": {
        ".*": {
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "patternProperties": {
                        "wiki_candidates": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {"pattern": {"type": "string"}, "replacement": {"type": "string"}},
                                "required": ["pattern", "replacement"],
                            },
                        },
                        # {"country": {"name": "country", "uri": "Country"}
                        "short_description": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "uri": {"type": "string"},
                                    "formatter": {"type": "string"},
                                    "split": {"type": "string"},
                                    "mappings": {"type": "object", "additionalProperties": {"type": "string"}},
                                },
                                "required": ["name", "uri"],
                            },
                        },
                        "^(?!wiki_candidates$|short_description)$": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "formatter": {"type": "string"},
                                "split": {"type": "string"},
                                "mappings": {"type": "object", "additionalProperties": {"type": "string"}},
                                "find": {
                                    "type": "object",
                                    "properties": {"pipeline": {"type": "string"}, "uri": {"type": "string"}},
                                    "required": ["pipeline", "uri"],
                                },
                                "convert": {
                                    "type": "object",
                                    "properties": {
                                        "to": {"type": "string"},
                                        "attributes": {
                                            "type": "object",
                                            "patternProperties": {
                                                ".*": {
                                                    "type": "object",
                                                    "properties": {"name": {"type": "string"}, "formatter": {"type": "string"}},
                                                    "required": ["name", "formatter"],
                                                }
                                            },
                                        },
                                    },
                                    "required": ["to", "attributes"],
                                },
                                "exclude": {"type": "string"},
                                "regex": {"type": "string"},
                            },
                        },
                    },
                }
            },
        },
    },
}


def validator(data: dict):
    try:
        jsonschema_validate(instance=data, schema=json_schema)
        return True
    except ValidationError as e:
        print(f"JSON data is invalid: {e}")


class Config:
    """
    General configuration object.
    """

    def __init__(self):

        self._languages = [
            {"name": "english", "code": "en"},
            {"name": "french", "code": "fr"},
            {"name": "dutch", "code": "nl"},
            {"name": "german", "code": "de"},
            {"name": "portuguese", "code": "po"},
            {"name": "swedish", "code": "sv"},
            {"name": "spanish", "code": "es"},
            {"name": "danish", "code": "dk"},
            {"name": "italian", "code": "it"},
            {"name": "norwegian", "code": "no"},
            {"name": "russian", "code": "ru"},
        ]
        self._language_to_code, self._code_to_language = self._generate_language_maps()

    def _generate_language_maps(self):
        self.l2c = {}
        self.c2l = {}
        for language_info in self._languages:
            self.l2c[language_info["name"]] = language_info["code"]
            self.c2l[language_info["code"]] = language_info["name"]
        return self.l2c, self.c2l

    @property
    def languages(self):
        """:return: a (``list``) with the available languages"""
        return self._languages

    def get_language(self, code: str):
        """
        :param str code: get the language for a give code.
        :return: (``str``) : ex english for the code en
        """
        _code = code.lower()
        retval = self._code_to_language[_code] if _code in self._code_to_language else None
        if not retval:
            return code if code in self._language_to_code else None
        return retval

    def get_language_code(self, language: str):
        """
        :param str code: get the code for a give language.
        :return: (``str``) : ex en for the language english
        """
        _language = language.lower()
        retval = self._language_to_code[_language] if _language in self._language_to_code else None
        if not retval:
            return language if language in self._code_to_language else None
        return retval

    def __str__(self):
        info = {"languages": self.languages}
        return json.dumps(info)


config = Config()
