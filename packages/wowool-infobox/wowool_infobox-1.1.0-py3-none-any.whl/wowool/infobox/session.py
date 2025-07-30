from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from sqlalchemy import Column, Integer, String, Date
from io import StringIO
from sqlalchemy.sql import text
from wowool.infobox.exceptions import InfoBoxException
import sys
import traceback
import json
import time
from sqlalchemy import event

_session = None

Base = declarative_base()


def commit_with_retry(session, retries=3, delay=1):
    attempt = 0
    while attempt < retries:
        try:
            session.commit()
            return  # Successfully committed
        except OperationalError as e:
            print(f"Commit failed due to lock, retrying... ({attempt + 1}/{retries}) {e}")
            attempt += 1
            time.sleep(delay)
    raise Exception("Commit failed after retries")


class InfoBoxInstance(Base):
    __tablename__ = "InfoBoxInstance"

    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        autoincrement=True,
    )

    literal = Column(String, index=True)
    language_code = Column(String, index=True)
    concept = Column(String, index=True)
    attributes = Column(String)
    description = Column(String)
    discoverd_date = Column(Date, nullable=True)
    search_literal = Column(String, index=True)

    def __repr__(self):
        return f"InfoBoxInstance: {self.id} {self.language_code},{self.literal},{self.concept},{self.attributes},{self.description}"

    def __str__(self):
        with StringIO() as output:
            output.write(f"""{{ "id":{self.id}, "literal":"{self.literal}", "language":"{self.language_code}" """)
            if self.concept:
                output.write(f""", "concept":"{self.concept}" """)
            if self.concept:
                output.write(f""", "attributes":{self.attributes} """)
            output.write("}")
            return output.getvalue()


class InfoBoxData(Base):
    __tablename__ = "InfoBoxData"
    literal = Column(String, primary_key=True)
    language_code = Column(String, primary_key=True)
    source = Column(String, primary_key=True)
    json_string = Column(String)

    def __repr__(self):
        return f"InfoBoxData: {self.language_code},{self.literal},{self.source},{self.json_string}"


def checkTableExists(engine, tablename):
    with engine.connect() as con:
        dbcur = con.execute(
            text(
                f"""
            SELECT name
            FROM sqlite_master
            WHERE name = '{tablename}' """
            )
        )

        one = dbcur.fetchone()
        if one and one[0] == tablename:
            return True

    return False


#  perform a full text match on the literals,
#  we will have to see what the future brings when we unleash the beast.
# def get_rec_match(session, literal):
#     results = [i[0] for i in session.execute(text(f"""SELECT rowid from InfoBoxInstance_idx where literal match '"{literal}"'""")).all()]
#     return results


def update_fulltext_table(engine):
    ddl = [
        """
        CREATE VIRTUAL TABLE InfoBoxInstance_idx USING fts5(
            literal,
            content='InfoBoxInstance',
            content_rowid='id'
        )
        """,
        """
        CREATE TRIGGER InfoBoxInstance_ai AFTER INSERT ON InfoBoxInstance BEGIN
            INSERT INTO InfoBoxInstance_idx (rowid, literal)
            VALUES (new.id, new.literal);
        END
        """,
        """
        CREATE TRIGGER InfoBoxInstance_ad AFTER DELETE ON InfoBoxInstance BEGIN
            INSERT INTO InfoBoxInstance_idx (InfoBoxInstance_idx, rowid, literal)
            VALUES ('delete', old.id, old.literal);
        END
        """,
        """
        CREATE TRIGGER InfoBoxInstance_au AFTER UPDATE ON InfoBoxInstance BEGIN
            INSERT INTO InfoBoxInstance_idx (InfoBoxInstance_idx, rowid, literal)
            VALUES ('delete', old.id, old.literal);
            INSERT INTO InfoBoxInstance_idx (rowid, literal)
            VALUES (new.id, new.literal);
        END
        """,
    ]

    if not checkTableExists(engine, "InfoBoxInstance_idx"):
        with engine.connect() as con:
            for statement in ddl:
                con.execute(text(statement))


def make_search_literal(input):
    return input.replace("'", "").lower()


class Session:
    def __init__(self, filename: str | Path = None, language_code: str = "en"):
        self._sqla_session = None
        self.filename = filename
        self.language_code = language_code
        self.Session = init_database(self.filename)

    def __enter__(self):
        if self._sqla_session is None:
            self._sqla_session = self.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._sqla_session.close()
        self._sqla_session = None

    def get_rec_match(self, literal):
        results = [
            i[0] for i in self.session.execute(text(f"""SELECT rowid from InfoBoxInstance_idx where literal match '"{literal}"'""")).all()
        ]
        return results

    @property
    def session(self):
        return self._sqla_session

    def get_literal_match(self, literal: str):
        try:
            search_literal = make_search_literal(literal)
            exact_results = [
                i for i in self.session.query(InfoBoxInstance).filter_by(search_literal=search_literal, language_code=self.language_code)
            ]
            return exact_results
        except Exception as ex:
            print("infobox:get_rec:", ex)
            traceback.print_exc(file=sys.stderr)
            return None

    def get_rec(self, input):
        try:
            literal = input.replace("'", "")
            # encoded_literal = requote_uri(input)
            exact_results = [i for i in self.session.query(InfoBoxInstance).filter_by(literal=literal, language_code=self.language_code)]
            if not exact_results:
                match_result = self.get_rec_match(literal)
                if match_result:
                    exact_results = [i for i in self.session.query(InfoBoxInstance).filter_by(id=match_result[0])]
            return exact_results
        except Exception as ex:
            print("infobox:get_rec:", ex)
            traceback.print_exc(file=sys.stderr)
            return None

    def update_concept(
        self,
        literal: str,
        concept: str,
        attributes: dict | None = None,
        description: str | None = None,
        discoverd_date=None,
        commit=True,
    ) -> InfoBoxInstance:
        search_literal = make_search_literal(literal)
        try:
            item = (
                self.session.query(InfoBoxInstance)
                .with_for_update()
                .filter_by(search_literal=search_literal, language_code=self.language_code, concept=concept)
                .first()
            )

            attributes_str = json.dumps(attributes) if attributes else None
            if item:
                if attributes_str:
                    setattr(item, "attributes", attributes_str)
                if description:
                    setattr(item, "description", description)
                if discoverd_date:
                    setattr(item, "discoverd_date", discoverd_date)
                if commit:
                    commit_with_retry(self.session)
            else:
                item = InfoBoxInstance(
                    search_literal=search_literal,
                    literal=literal,
                    language_code=self.language_code,
                    concept=concept,
                    attributes=attributes_str,
                    description=description,
                    discoverd_date=discoverd_date,
                )
                self.session.add(item)
                if commit:
                    commit_with_retry(self.session)
            return item
        except IntegrityError:
            self.session.rollback()
        except Exception as ex:
            self.session.rollback()
            print("infobox:update_concept:", ex)
            traceback.print_exc(file=sys.stderr)
            return None

    def delete_uri(self, uri: str | None = None, literal: str | None = None):
        """delete a uri from the infobox instance"""

        filters = []
        if uri:
            filters.append(InfoBoxInstance.concept.like(uri))
        if literal:
            filters.append(InfoBoxInstance.literal.like(literal))

        if filters:
            self.session.query(InfoBoxInstance).filter(*filters).delete()
        else:
            self.session.query(InfoBoxInstance).delete()
        self.session.commit()


def init_database(filename: str | Path = None):
    try:
        if not filename:
            cfloder = Path("~/.wowool/cache/").expanduser()
            if not cfloder.exists():
                cfloder.mkdir(parents=True, exist_ok=True)
            filename = cfloder / "wowool-wiki-attribute.db"

        engine = create_engine(f"sqlite:///{filename}?check_same_thread=false&timeout=10")

        # Define an event listener that sets the PRAGMA journal_mode to WAL
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.close()

        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        update_fulltext_table(engine)
        return Session
    except Exception as ex:
        raise InfoBoxException(f"Error: infobox, init_database error [{filename}][{ex}]")


def session():
    global _session
    if _session is None:
        _session = init_database()
    return _session
