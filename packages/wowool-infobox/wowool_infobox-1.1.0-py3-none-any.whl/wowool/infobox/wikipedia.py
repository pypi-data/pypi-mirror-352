import re
import requests
from wowool.infobox.session import InfoBoxData
from wowool.infobox.utilities import convert_args
from wowool.string import initial_caps, camelize

# from wowool.infobox.process.process import run_discovery_worker
# from wowool.infobox.process.discovery_client import run_discovery_worker
from wowool.infobox.process.discovery import run_discovery_worker
from bs4 import BeautifulSoup
from wowool.annotation import Concept
from requests.utils import requote_uri
from datetime import datetime
from wowool.infobox.logger import logger
from wowool.infobox.session import Session
from wowool.infobox.utilities import get_language_code

ATTRIBUTE_PATTERN = re.compile(r"{{(.*?)(:?[|](.*?))?}}")
ATTRIBUTE_PATTERN_ATTR = re.compile(r"(.+?)= *{{(.+?)?}}")
ATTRIBUTE_PATTERN_REFER_TO = re.compile(r".*?refer to:(.*).?")
REDIRECTION_PATTERN = re.compile(r"#REDIRECT *\[\[(.*?)\]\].*")
SEARCHRESULT_PATTERN = re.compile(r"([0-9]+) statements?, ([0-9]+) sitelinks?.*")

SOURCE = "wikipedia"

CSS_CANONICAL = "span.mw-page-title-main,h1.mw-first-heading"
CSS_REDIRECT = "span.mw-redirectedfrom"

DESCRIPTOR_MAPPINGS = {}


def canonical_cleanup(literal):
    return literal.replace("-", " ")


def get_rec_wikipedia(infobox: Session, literal: str | Concept, language_code):
    if isinstance(literal, str):

        retval = (
            infobox.session.query(InfoBoxData)
            .filter(InfoBoxData.literal.ilike(literal), InfoBoxData.language_code == language_code, InfoBoxData.source == SOURCE)
            .first()
        )
        if retval:
            return {"literal": canonical_cleanup(retval.literal), "item": retval}
    else:
        retval = infobox.session.query(InfoBoxData).filter_by(literal=literal.canonical, language_code=language_code, source=SOURCE).first()
        if not retval:
            retval = infobox.session.query(InfoBoxData).filter_by(literal=literal.text, language_code=language_code, source=SOURCE).first()
        if retval:
            return {"literal": canonical_cleanup(retval.literal), "item": retval}


def is_descriptor(concept):
    return concept.uri == "Descriptor"


def is_position(concept):
    return concept.uri == "Position"


REMOVE_BRAKETS = re.compile(r"[\[(][^\])]+[\])]")


def valid_value(value, attr_info):
    if "exclude" in attr_info:
        if "exclude_" not in attr_info:
            attr_info["exclude_"] = re.compile(attr_info["exclude"])
        if attr_info["exclude_"].match(value):
            return False
    return True


def formatter_lower(value):
    return value.lower()


def formatter_upper(value):
    return value.upper()


FORMATTER = {
    "camelize": camelize,
    "lower": formatter_lower,
    "upper": formatter_upper,
    "initial_caps": initial_caps,
    "none": lambda x: x,
}


def format_value(value, attr_info):
    value = FORMATTER[attr_info.get("formatter", "none")](value)
    value = attr_info.get("mappings", {}).get(value, value)
    if "regex" in attr_info:
        attr_info["regex_"] = re.compile(attr_info["regex"])
    if "regex_" in attr_info:
        if m := attr_info["regex_"].match(value):
            for group in m.groups():
                if group:
                    return group
    return value


def parse_attribute_value_str(value, attr_info, language: str):
    if "find" in attr_info:
        find_info = attr_info["find"]
        if "pipeline" in find_info and "uri" in find_info:
            uri = find_info["uri"]
            logger.debug(f"Discovery: pipeline:{language},{find_info['pipeline']} literal={value} uri={uri}")
            doc = run_discovery_worker(f"{language},{find_info['pipeline']}", value)
            if doc:
                for concept in doc.concepts(lambda c: c.uri == uri):
                    value = concept.canonical
                    if valid_value(value, attr_info):
                        value = format_value(value, attr_info)
                        if value:
                            yield value
            else:
                raise RuntimeError("Could not run the discovery pipeline")
        else:
            raise ValueError(f"Invalid find info: {find_info}, missing 'pipeline' or 'uri' value.")
        return

    value = REMOVE_BRAKETS.sub("|", value)
    for value in value.split("|"):
        if value := value.strip():
            if "split" in attr_info:
                for value in value.split(attr_info["split"]):
                    value = value.strip()
                    if valid_value(value, attr_info):
                        value = format_value(value, attr_info)
                        if value:
                            yield value
            else:
                if valid_value(value, attr_info):
                    value = format_value(value, attr_info)
                    if value:
                        yield value


def parse_attribute_values(value_item, attr_info, language: str):
    value = value_item.get_text(" ", strip=True)
    if value:
        yield from parse_attribute_value_str(value, attr_info, language)


WIKI_REPLACE_PATTERN = re.compile(r"[\s_,]+")


def check_redirect(wiki_entry, redirect_entry):
    wr = WIKI_REPLACE_PATTERN.sub("", wiki_entry).lower()
    re = WIKI_REPLACE_PATTERN.sub("", redirect_entry).lower()
    if wr == re:
        return True
    return False


def get_infobox_html_entry(literal: str | Concept, language_code: str):
    encoded_literal = requote_uri(literal)
    url = f"""https://{language_code}.wikipedia.org/wiki/{encoded_literal}"""
    try:
        logger.debug(f'requests.get("{url}")')
        response = requests.get(url)
    except requests.exceptions.ConnectionError as exconn:
        logger.exception(f"Connection error: {url}", exconn)
        return

    data = response.text
    soup = BeautifulSoup(str(data), "html5lib")

    redirected = soup.select_one(CSS_REDIRECT)
    if redirected:
        rederct_lnk = redirected.select_one("a")
        redirect_string = rederct_lnk.get_text(" ", strip=True)
        result = check_redirect(literal, redirect_string)
        if not result:
            return None

    html_data = ""

    canonical_item = soup.select_one(CSS_CANONICAL)
    if canonical_item:
        html_data += canonical_item.prettify(formatter="minimal")
    else:
        raise Exception(f"Could not find canonical item for {literal}, check out {url}")

    shortdescription_item = soup.select_one("div.shortdescription")
    if shortdescription_item:
        html_data += shortdescription_item.prettify(formatter="minimal")
    infobox = soup.select_one("table.infobox")
    if infobox:
        html_data += infobox.prettify(formatter="minimal")
        return {"literal": literal, "html": html_data}


def get_infobox_html(literal: str | Concept, language_code: str, attributes):
    if isinstance(literal, str):
        return get_infobox_html_entry(literal, language_code)
    elif isinstance(literal, Concept):
        result = get_infobox_html_entry(literal.canonical, language_code)
        if result:
            return result
        else:
            camelized_text = literal.text.lower()
            if camelized_text != literal.canonical.lower():
                return get_infobox_html_entry(literal.text, language_code)
            wiki_candidates = attributes.get("wiki_candidates", [])
            for sr_desc in wiki_candidates:
                wiki_candidate = re.sub(sr_desc["pattern"], sr_desc["replacement"], literal.canonical)
                result = get_infobox_html_entry(wiki_candidate, language_code)
                if result:
                    return result


def get_valid_descriptor_match(attributes_data, uri: str):
    if uri == "UnknownThing":
        return uri

    descriptors = attributes_data.get("wiki_type", [])
    if not descriptors:
        return uri
    for descriptor in descriptors:
        mapped_descriptor = DESCRIPTOR_MAPPINGS.get(descriptor, descriptor)
        if mapped_descriptor == uri:
            return uri


class WikiPediaInfobox:
    def __init__(self, infobox: Session, config: dict, language: str | None = "english", lock=None) -> None:
        self.infobox_config = config
        self.infobox = infobox
        self.language = language if language else "english"
        self.language_code = get_language_code(language) if language else "en"
        self.lock = lock

    def add_values(self, attributes_data, attr_info, infobox_config, label, values, language="english"):
        if values:
            attributes_data[label] = values

        if "convert" in attr_info:
            convert_info = attr_info["convert"]
            if "to" in convert_info and "attributes" in convert_info:
                concept = convert_info["to"]
                new_concept_attributes = {}
                for key, convert_info in convert_info["attributes"].items():
                    new_attribute_key = convert_info.get("name", key)
                    if new_descritors := attributes_data.get(key):
                        for new_descritor in new_descritors:
                            key_attr_info = infobox_config.get(new_descritor, {})
                            if key in attributes_data:
                                for value in attributes_data.get("canonical", []):
                                    for new_value in parse_attribute_value_str(value, key_attr_info, language):
                                        if key not in new_concept_attributes:
                                            new_concept_attributes[new_attribute_key] = [new_value]
                                        else:
                                            new_concept_attributes[new_attribute_key].append(new_value)
                for value in values:
                    self.infobox.update_concept(value, concept, new_concept_attributes)
            else:
                raise ValueError(f"Invalid convert info: {convert_info}, missing 'to' or 'attributes' value.")

    def get_config_uri_attributes(self, uri: str):
        if self.language in self.infobox_config and uri in self.infobox_config[self.language]:
            return self.infobox_config[self.language][uri]
        elif uri in self.infobox_config:
            return self.infobox_config[uri]
        return {}

    def get_infobox_attributes(self, literal: str, uri: str | None = None):
        wiki_literal, encoded_literal = convert_args(literal)
        instance_data = get_rec_wikipedia(self.infobox, literal, self.language_code)
        attributes = self.get_config_uri_attributes(uri)
        infobox_data_item = None

        if not instance_data:
            result = html_data = get_infobox_html(literal, self.language_code, attributes)
            if result:
                html_data = result["html"]
                literal_ = result["literal"]
            else:
                literal_ = wiki_literal
                html_data = ""

            infobox_data_item = InfoBoxData(
                literal=literal_,
                language_code=self.language_code,
                source=SOURCE,
                json_string=html_data,
            )
            self.infobox.session.add(infobox_data_item)
            self.infobox.session.commit()

        elif instance_data.items:
            infobox_data_item = instance_data["item"]

        # instance_retval = get_rec_wikipedia(literal, language_code)
        if infobox_data_item:
            attributes = attributes = self.get_config_uri_attributes(uri)

            instance_data = infobox_data_item
            literal_ = infobox_data_item.literal
            attributes_data = {}

            if len(instance_data.json_string):
                soup = BeautifulSoup(str(instance_data.json_string), "html5lib")

                shortdescription_item = soup.select_one("div.shortdescription")
                if shortdescription_item:
                    attr_info = attributes.get("wiki_type", {})
                    shortdescription = shortdescription_item.get_text(" ", strip=True)
                    attributes_data["shortdescription"] = [shortdescription]
                    pipeline = f"{self.language},entity,discovery"
                    logger.debug(f"Discovery: pipeline:{pipeline} literal={literal_} short_description={shortdescription}")
                    if doc := run_discovery_worker(pipeline, shortdescription):
                        #  discover the type of the entity we are dealing with.
                        for concept in doc.concepts(is_descriptor):
                            values = concept.attributes["type"] if "type" in concept.attributes else [concept.stem]
                            for value in values:
                                if value and valid_value(value, attr_info):
                                    value = format_value(value, attr_info)
                                    if value:
                                        value = DESCRIPTOR_MAPPINGS.get(value, value)
                                        if "wiki_type" not in attributes_data:
                                            attributes_data["wiki_type"] = [value]
                                        else:
                                            attributes_data["wiki_type"].append(value)
                        if uri is None and "wiki_type" in attributes_data:
                            attributes = self.get_config_uri_attributes(attributes_data["wiki_type"][0])

                        # meanwhile we can also discover the position of the entity.
                        positions = []
                        for concept in doc.concepts(is_position):
                            value = concept.canonical
                            if value and valid_value(value, attr_info):
                                value = format_value(value, attr_info)
                                if value:
                                    positions.append(value)
                        if positions:
                            attributes_data["position"] = positions

                        if "short_description" in attributes:

                            already_done = set()
                            for sd_attr_info in attributes["short_description"]:

                                sd_attr_name = sd_attr_info["name"]
                                if sd_attr_name in already_done:
                                    continue

                                sd_uri_filter_list = sd_attr_info["uri"].split(".", maxsplit=1)

                                sd_uri_filter = sd_uri_filter_list[0]
                                sd_uri_attr_name = None
                                if len(sd_uri_filter_list) > 1:
                                    sd_uri_attr_name = sd_uri_filter_list[1]

                                for concept in doc.concepts(lambda c: c.uri == sd_uri_filter):
                                    sd_concept_value = None
                                    if sd_uri_attr_name:
                                        if sd_uri_attr_name in concept.attributes:
                                            sd_concept_value = concept.attributes[sd_uri_attr_name][0]
                                    else:
                                        sd_concept_value = concept.canonical
                                    if sd_concept_value:
                                        already_done.add(sd_attr_name)
                                        for value in parse_attribute_value_str(sd_concept_value, sd_attr_info, self.language):
                                            if sd_attr_name not in attributes_data:
                                                attributes_data[sd_attr_name] = [value]
                                            else:
                                                attributes_data[sd_attr_name].append(value)
                    else:
                        logger.error("Could not run the discovery pipeline")

                canonical_item = soup.select_one(CSS_CANONICAL)
                if canonical_item:
                    attr_info = attributes.get("canonical", {})
                    value = canonical_item.get_text(" ", strip=True)
                    if value and valid_value(value, attr_info):
                        value = format_value(value, attr_info)
                        if value:
                            attributes_data["canonical"] = [canonical_cleanup(value)]

                infobox_table = soup.select_one("table.infobox")
                if infobox_table:
                    for label_item in infobox_table.find_all(class_="infobox-label"):
                        label = label_item.get_text(" ", strip=True).lower().replace(" ", "_")
                        attr_info = attributes.get(label, {})

                        value_bucket = label_item.find_next_sibling("td", class_="infobox-data")
                        if value_bucket:
                            value_items = value_bucket
                            if value_items and attributes and label in attributes:
                                new_label = attr_info["name"] if "name" in attr_info else label
                                values = []
                                for value_item in value_items.select("ul li"):
                                    for value in parse_attribute_values(value_item, attr_info, self.language):
                                        values.append(value)
                                if not values:
                                    for value in parse_attribute_values(value_items, attr_info, self.language):
                                        values.append(value)
                                if values:
                                    self.add_values(attributes_data, attr_info, self.infobox_config, new_label, values)
            if self.lock:
                with self.lock:
                    return self._update_db(literal_, uri, attributes_data)
            else:
                return self._update_db(literal_, uri, attributes_data)

    def _update_db(self, literal, uri, attributes_data):
        if attributes_data:
            logger.debug(f"get_infobox_attributes:ATTRIBUTES: canonical={literal} {uri=} {attributes_data}")
        descriptor = get_valid_descriptor_match(attributes_data, uri)
        if attributes_data and descriptor:
            self.infobox.update_concept(
                literal=literal,
                concept=uri,
                attributes=attributes_data,
                description=camelize(descriptor),
                discoverd_date=datetime.now(),
            )
            return attributes_data
        else:
            # update the discoverd_date date only if we did not find anything.
            self.infobox.update_concept(
                literal=literal,
                concept=uri,
                discoverd_date=datetime.now(),
            )
