from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
import os

Base = declarative_base()


def db_setup(db_suffix=''):
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASS"]
    host = os.environ["DB_HOST"]
    port = os.environ["DB_PORT"]
    database = os.environ["DB_NAME"] + db_suffix

    url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    engine = create_engine(url, pool_size=20)
    if not database_exists(engine.url):
        create_database(engine.url)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal



