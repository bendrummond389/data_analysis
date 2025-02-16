import logging

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from scripts.utils import load_config

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

def load_data_to_db(
    df: pd.DataFrame,
    table_name: str
) -> None:
    """
    Load cleaned data from a Pandas DataFrame into a PostgreSQL database table.

    :param df: Pandas DataFrame containing the cleaned data.
    :param db_config: Dictionary containing database connection details.
    :param table_name: Name of the table to load data into (default: "acs2017_county_data").
    :return: None
    :raises Exception: If any error occurs during the data loading process.
    """
    try:
        engine = create_db_engine()

        # Write the DataFrame to the database, replacing the table if it already exists
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        logger.info(f"Data successfully loaded into table: {table_name}")
    except Exception as e:
        logger.error(f"Error in load_data_to_db: {e}")
        raise
