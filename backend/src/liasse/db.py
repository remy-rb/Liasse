from sqlalchemy import Engine, create_engine

from liasse.settings import Settings


def make_engine(settings: Settings) -> Engine:
    return create_engine(str(settings.database_url), pool_pre_ping=True)
