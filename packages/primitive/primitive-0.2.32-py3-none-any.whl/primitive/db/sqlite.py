from pathlib import Path
from time import sleep

from loguru import logger
from sqlalchemy import Engine, create_engine, inspect
from sqlalchemy.orm import Session as SQLAlchemySession

from primitive.db.base import Base
from primitive.utils.cache import get_cache_dir


def init() -> None:
    db_path: Path = get_cache_dir() / "primitive.sqlite3"

    # Drop DB existing database if it exists
    # if db_path.exists():
    #     logger.warning(f"Deleting existing SQLite database at {db_path}")
    #     db_path.unlink()
    if db_path.exists():
        return

    logger.info(f"Initializing SQLite database at {db_path}")
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)


def engine() -> Engine:
    db_path: Path = get_cache_dir() / "primitive.sqlite3"
    return create_engine(f"sqlite:///{db_path}", echo=False)


def wait_for_db() -> None:
    # Wait for the database to be created
    db_path: Path = get_cache_dir() / "primitive.sqlite3"

    max_tries = 60
    current_try = 1
    while not db_path.exists() and current_try <= max_tries:
        logger.debug(
            f"Waiting for SQLite database to be created... [{current_try} / {max_tries}]"
        )
        sleep(1)
        current_try += 1
        continue
    if current_try > max_tries:
        message = f"SQLite database was not created after {max_tries} tries. Exiting..."
        logger.error(message)
        raise RuntimeError(message)

    # check if table exists
    max_tries = 60
    current_try = 1
    while not inspect(engine()).has_table("JobRun") and current_try <= max_tries:
        logger.error("SQLite database is not ready.")
        sleep(1)
        current_try += 1
        continue
    if current_try > max_tries:
        message = (
            f"Database tables were not created after {max_tries} tries. Exiting..."
        )
        logger.error(message)
        raise RuntimeError(message)
    logger.debug("SQLite database is ready.")


def Session() -> SQLAlchemySession:
    from sqlalchemy.orm import sessionmaker

    return sessionmaker(bind=engine())()
