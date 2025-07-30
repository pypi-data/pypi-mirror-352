import json
from wowool.infobox.session import Session

# from wowool.infobox.wikidata import wikidata_discover, get_infobox_wikidata
from wowool.infobox.wikipedia import WikiPediaInfobox
from wowool.diagnostic import Diagnostics
from wowool.document.analysis.document import AnalysisDocument
from wowool.native.core.engine import Engine
from wowool.annotation.concept import Concept
from wowool.utility.apps.decorators import exceptions_to_diagnostics, requires_analysis
from wowool.native.core.analysis import (
    get_internal_concept,
    add_internal_concept,
    remove_internal_concept_attribute,
    get_internal_concept_args,
)
from wowool.infobox.config import DEFAULT_URIS
from wowool.string import camelize
from wowool.annotation import Token
from wowool.infobox.logger import logger
from wowool.infobox.config import config, validator


def token_not_found(tk: Token):
    return "nf" in tk.properties and len(tk.literal) > 4


def merge_attributes(attributes: dict, new_attributes: dict | None):
    if not new_attributes:
        return True, attributes

    updated = False
    for key, values in new_attributes.items():
        if key in attributes:
            if isinstance(values, list):
                for value in values:
                    if value not in attributes[key]:
                        attributes[key].append(value)
                        updated = True
            else:
                if values not in attributes[key]:
                    attributes[key] = values
                    updated = True
        else:
            attributes[key] = values
            updated = True

    return updated, attributes


def remove_hidden_attributes(attributes):
    return {k: v for k, v in attributes.items() if not k.startswith("_")}


def filter_attributes(attributes: dict):
    return {k: v for k, v in attributes.items() if k not in ["canonical", "given", "family", "gender"]}


def get_discriptor(attributes):
    if "descriptor" in attributes and attributes["descriptor"] and len(attributes["descriptor"]) > 0:
        return camelize(attributes["descriptor"][0].replace(",", " "))


def get_wiki_type(attributes, uri: str | None = None):
    if "wiki_type" in attributes:
        for wiki_type in attributes["wiki_type"]:
            yield camelize(wiki_type.replace(",", " "))
    elif uri:
        yield uri


def is_initial_caps_all_words(literal: str):
    return all([word[0].isupper() for word in literal.split()])


class Infobox:
    def __init__(
        self,
        uri_descriptions: dict = DEFAULT_URIS,
        persistency: bool = True,
        log_level: str | None = None,
        language: str | None = None,
        engine: Engine = None,
    ):
        """
        Initialize the Snippet application

        :param source: The Wowool source code
        :param source: str
        """
        self.language = language
        self.language_code = config.get_language_code(language)
        self.uris = uri_descriptions.get(language, uri_descriptions.get("english"))
        validator(DEFAULT_URIS)

        self.persistency = persistency
        if log_level:
            logger.setLevel(log_level)

    def update_concept(self, uri: str, literal: str, concept_attributes: dict, attributes: dict):
        updated, new_attributes = merge_attributes(filter_attributes(remove_hidden_attributes(concept_attributes)), attributes)
        if updated and new_attributes:
            self.session.update_concept(literal, uri, new_attributes)

    @exceptions_to_diagnostics
    @requires_analysis
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        """
        :param document: The document to be processed and enriched with the annotations from the snippet
        :type document: AnalysisDocument

        :returns: The given document with the new annotations. See the :ref:`JSON format <json_apps_infobox>`
        """
        with Session(language_code=self.language_code) as session:
            self.session = session
            lock = self.lock if hasattr(self, "lock") else None
            self.wikidata = WikiPediaInfobox(self.session, self.uris, language=self.language, lock=lock)
            return self.process(document, diagnostics)

    def is_candidate(self, concept: Concept):
        if concept.uri in self.uris:
            if "_conditions" in self.uris[concept.uri]:
                _conditions = self.uris[concept.uri]["_conditions"]
                for condition in _conditions:
                    match condition:
                        case "initial_caps":
                            return is_initial_caps_all_words(concept.canonical)
                        case _:
                            raise ValueError(f"Infobox: Unknown _condition: {condition} for uri {concept.uri}")

                return False
            return True
        return False

    def process(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        previous_concepts = None
        for concept in document.analysis.concepts():
            if self.is_candidate(concept):
                if previous_concepts and previous_concepts.end_offset >= concept.begin_offset:
                    if concept.uri == "UnknownThing":
                        internal_concept = get_internal_concept(document.analysis, concept)
                        if internal_concept:
                            remove_internal_concept_attribute(document.analysis, internal_concept)
                    continue
                previous_concepts = concept
                literal: str = concept.canonical
                item = self.session.get_literal_match(literal)
                if not item or item[0].discoverd_date is None:
                    if get_internal_concept_args(document.analysis, concept.begin_offset, concept.end_offset, "wow::anaphora"):
                        continue
                    attributes = self.wikidata.get_infobox_attributes(literal, concept.uri)
                else:
                    attributes = json.loads(item[0].attributes) if item[0].attributes else None
                if attributes:
                    if self.persistency and concept.uri != "UnknownThing":
                        self.update_concept(concept.uri, literal, concept.attributes, attributes)
                    internal_concept = get_internal_concept(document.analysis, concept)
                    if internal_concept:
                        for descriptor in get_wiki_type(attributes, concept.uri):
                            if descriptor != concept.uri:
                                internal_concept_known = add_internal_concept(
                                    document.analysis,
                                    concept.begin_offset,
                                    concept.end_offset,
                                    descriptor,
                                    unicode_offset=True,
                                )
                            else:
                                internal_concept_known = internal_concept

                            # if concept.uri == "UnknownThing":
                            #     internal_concept_known = internal_concept

                            if internal_concept_known:
                                for key, values in attributes.items():
                                    if isinstance(values, list):
                                        for value in values:
                                            internal_concept_known.add_attribute(key, value)
                                    else:
                                        internal_concept_known.add_attribute(key, str(values))

        document.analysis.reset()

        for token in [tk for tk in Token.iter(document.analysis) if token_not_found(tk)]:
            item = self.session.get_literal_match(token.literal)
            if item and item[0].attributes:
                attributes = json.loads(item[0].attributes)
                for descriptor in get_wiki_type(attributes):
                    internal_concept = add_internal_concept(document.analysis, token.begin_offset, token.end_offset, descriptor)
                    if internal_concept:
                        for key, values in attributes.items():
                            if isinstance(values, list):
                                for value in values:
                                    internal_concept.add_attribute(key, value)
                            else:
                                internal_concept.add_attribute(key, str(values))
                        document.analysis.reset()

        return document
