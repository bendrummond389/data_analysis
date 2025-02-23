import logging
from typing import List, Type


import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.orm import sessionmaker, Session, DeclarativeMeta
from scripts import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_db_engine() -> Engine:
    """
    Create a SQLAlchemy engine using the provided database configuration.

    :param db_config: Dictionary containing database connection details.
                      Example:
                      {
                          "user": "username",
                          "password": "password",
                          "host": "localhost",
                          "port": 5432,
                          "database": "mydb"
                      }
    :return: SQLAlchemy Engine instance connected to the specified database.
    :raises Exception: If any error occurs while creating the engine.
    """
    try:
        db_config = load_config()["db_config"]
        connection_string = (
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        return create_engine(connection_string)
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def get_session() -> Session:
    """
    Create a SQLAlchemy session for database interaction.

    :param db_config: Dictionary containing database connection details.
    :return: SQLAlchemy Session instance.
    :raises Exception: If any error occurs while creating the session.
    """
    try:
        engine = create_db_engine()
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return session_factory()
    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        raise

def create_tables(session: Session, models: List[Type[DeclarativeMeta]]) -> None:
    """Create database tables from ORM models if they don't exist"""
    try:
        for model in models:
            if hasattr(model, '__table__'):
                model.__table__.create(bind=session.get_bind(), checkfirst=True)
        logger.info("Tables created/verified successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating tables: {e}")
        raise

def insert_dataframe(session: Session, df: pd.DataFrame, model: Type[DeclarativeMeta]) -> None:
    """Insert DataFrame data into database using SQLAlchemy ORM"""
    try:
        # Convert DataFrame to list of model instances
        records = [model(**row) for row in df.to_dict(orient='records')]
        
        # Bulk insert with return_defaults=False for better performance
        session.bulk_save_objects(records, return_defaults=False)
        session.commit()
        logger.info(f"Successfully inserted {len(records)} records into {model.__tablename__}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error inserting data: {e}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error: {e}")
        raise

def with_db_session(func):
    """Decorator for managing database session lifecycle"""
    def wrapper(*args, **kwargs):
        session = get_session()
        try:
            result = func(session, *args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            session.close()
    return wrapper