import json
from wowool.infobox.session import Session
from wowool.infobox.session import InfoBoxInstance
from wowool.infobox.wikipedia import WikiPediaInfobox
from wowool.infobox.config import DEFAULT_URIS
from sqlalchemy.sql import text
from csv import DictWriter as csv_DictWriter
from argparse import ArgumentParser
import sys
from wowool.infobox.logger import logger
import logging


def main_discover(infobox: Session, input, uri, verbose):
    wiki = WikiPediaInfobox(infobox=infobox, uris=DEFAULT_URIS)
    wiki.get_infobox_attributes(input, uri)


def main_list_instances(infobox: Session, where: str | list | None = None, attributes: bool = False, csv: bool = False, verbose=False):
    if where:
        if isinstance(where, list):
            where = " ".join(where)
        if verbose:
            print(f"where: {where}")
        results = infobox.session.execute(text(f"""SELECT * FROM InfoBoxInstance WHERE {where} ;"""))
    else:
        results = infobox.session.query(InfoBoxInstance)
    results = [item for item in results]
    if csv:
        fieldnames_fix = ["concept", "literal", "search_literal", "description", "discoverd_date"]
        fieldnames = set()
        for item in results:
            if item.attributes:
                attributes = json.loads(item.attributes)
                for key in attributes:
                    fieldnames.add(key)

        fieldnames_fix.extend(list(fieldnames))
        writer = csv_DictWriter(sys.stdout, delimiter=",", fieldnames=fieldnames_fix)
        writer.writeheader()
        for item in results:
            row = {
                "concept": item.concept,
                "literal": item.literal,
                "search_literal": item.search_literal,
                "description": item.description,
                "discoverd_date": item.discoverd_date,
            }
            if item.attributes:
                attributes_ = json.loads(item.attributes)
                for key, values in attributes_.items():
                    row[key] = " | ".join(values)
                # row.update(attributes)

            writer.writerow(row)

    else:
        for item in results:
            if not verbose:
                print(f"{item.concept}, {item.literal} , (search={item.search_literal})")
            else:
                print(f"{item.id},{item.concept}, {item.literal}, {item.search_literal}, {item.description}, {item.discoverd_date}")
            if attributes and item.attributes:
                attributes_ = json.loads(item.attributes)
                for key, values in attributes_.items():
                    print(f"  - {key}:", end="")
                    print(*values, sep=" | ")


def get_info(infobox: Session, input, key=None, language="english", redirect=None):
    return infobox.get_rec(input)


# def main_add_search_literal(literal, recid):
#     add_search_literal(literal, recid)


def main_attributes(infobox: Session, literal, uri: str | None = None, verbose=False):
    item = infobox.get_rec(literal)
    attributes = None
    if not item:
        wiki = WikiPediaInfobox(infobox=infobox, config=DEFAULT_URIS)
        attributes = wiki.get_infobox_attributes(literal, uri)
    else:
        if item[0].attributes:
            attributes = json.loads(item[0].attributes)
    if attributes:
        print(*attributes.items(), sep="\n")


def main_delete_uri(infobox: Session, uri: str | None = None, literal: str | None = None, verbose=False):
    infobox.delete_uri(uri, literal)


def add_argument_parser(parser: ArgumentParser):
    subparsers = parser.add_subparsers()

    parser_discover = subparsers.add_parser(
        "discover",
        help="discovers the given and update the Instance and the Data, usage: discover [language_code] [literal] [wikidata/wikipedia]",
        usage="""infobox discover [language_code] [literal] [source]\n   ex: infobox discover en "Rafael Nadal" wikidata""",
    )
    parser_discover.add_argument("language", type=str, help="language")
    parser_discover.add_argument("input", type=str, help="input literal")
    parser_discover.add_argument("source", type=str, help="wikidata")
    parser_discover.set_defaults(function=main_discover)

    parser_list = subparsers.add_parser(
        "list",
        help="list all the entries, usage: list",
        usage="""infobox list [--where 'concept = "Person"']""",
    )
    parser_list.add_argument("--where", type=str, help="where clause")
    parser_list.add_argument("-a", "--attributes", help="display the attributes", default=False, action="store_true")
    parser_list.add_argument("--csv", help="a csv table format", default=False, action="store_true")
    parser_list.set_defaults(function=main_list_instances)

    subparser = subparsers.add_parser(
        "attributes",
        help="attributes infobox attributes [literal]",
        usage="""infobox add_id [literal] \n   ex: infobox attributes "Kamala Harris" """,
    )
    subparser.add_argument("literal", type=str, help="literal to find")
    subparser.add_argument("--uri", type=str, help="which type of uri to search for", default=None)

    subparser.set_defaults(function=main_attributes)

    subparser = subparsers.add_parser(
        "del",
        help="delete a given [uri]",
        usage="""infobox del [uri] \n   ex: infobox del Person """,
    )
    subparser.add_argument("-u", "--uri", type=str, help="delete the instance of a given uri , ex : infobox --uri Person ", default=None)
    subparser.add_argument(
        "-l", "--literal", type=str, help='delete the instance of a given literal , ex : infobox --literal "Barack Obama" ', default=None
    )
    subparser.set_defaults(function=main_delete_uri)

    parser.add_argument("-v", "--verbose", help="verbose output", default=False, action="store_true")
    parser.add_argument("--logger", help="verbose output", default="INFO")
    return parser


def clean_up(kwargs):
    keys = [k for k in kwargs]
    for key in keys:
        if not kwargs[key]:
            del kwargs[key]


def expand_keys(kwargs):
    if "key" in kwargs:
        if kwargs["key"] == "sd":
            kwargs["key"] = "short description"
        if kwargs["key"] == "ad":
            kwargs["key"] = "ambiguous description"
        if kwargs["key"] == "c":
            kwargs["key"] = "concept"


def is_descriptor(concept):
    return concept.uri == "Descriptor"


def infobox_main(**kwargs):

    dbname = kwargs["database"] if "database" in kwargs else None
    with Session(dbname) as infobox:
        action = kwargs["function"]
        del kwargs["function"]
        logging.basicConfig()
        logger.setLevel(kwargs.pop("logger"))
        action(infobox, **kwargs)

    exit(0)
