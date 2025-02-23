import logging
from typing import List, Optional, Type, Callable, Any, Dict
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, ArgumentError
from sqlalchemy.orm import sessionmaker, Session, DeclarativeMeta
from pathlib import Path

import yaml

from src.config import load_config
from src.config.paths import find_nearest_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Context-aware database manager that finds appropriate config."""
    
    def __init__(self, config_name: str = "database.yaml", context_path: Optional[Path] = None):
        """
        Args:
            config_name: Name of config file to load
            context_path: Optional starting path for config search
        """
        self.config_path = find_nearest_config(
            start_path=context_path,
            config_name=config_name
        )
        self.config = self._load_config()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )

    def _load_config(self) -> dict:
        """Load configuration from discovered YAML file."""
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _create_engine(self) -> Engine:
        """Create SQLAlchemy engine from config."""
        required_keys = {'user', 'password', 'host', 'port', 'name'}
        missing_keys = required_keys - self.config.keys()
        
        if missing_keys:
            raise ValueError(f"Missing required config keys: {missing_keys}")

        try:
            return create_engine(
                f"postgresql://{self.config['user']}:{self.config['password']}@"
                f"{self.config['host']}:{self.config['port']}/{self.config['name']}"
            )
        except ArgumentError as e:
            raise ValueError(f"Invalid database configuration: {e}") from e

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def create_tables(self, models: List[Type[DeclarativeMeta]]) -> None:
        """Create database tables for ORM models."""
        try:
            for model in models:
                if hasattr(model, "__table__"):
                    model.__table__.create(bind=self.engine, checkfirst=True)
            logger.info("Tables created/verified successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def insert_dataframe(self, df: pd.DataFrame, model: Type[DeclarativeMeta]) -> None:
        """Insert DataFrame data into database."""
        session = self.get_session()
        try:
            records = [model(**row) for row in df.to_dict(orient="records")]
            session.bulk_save_objects(records, return_defaults=False)
            session.commit()
            logger.info(f"Inserted {len(records)} records into {model.__tablename__}")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()

    def with_db_session(self, func: Callable) -> Callable:
        """Session management decorator."""
        def wrapper(*args, **kwargs) -> Any:
            session = self.get_session()
            try:
                result = func(session, *args, **kwargs)
                session.commit()
                return result
            except Exception as e:
                session.rollback()
                logger.error(f"Transaction failed: {e}")
                raise
            finally:
                session.close()
        return wrapper

# Global instance for main project database
def get_default_manager() -> DatabaseManager:
    """Get manager for main project database."""
    config = load_config()["database"]
    return DatabaseManager(config)