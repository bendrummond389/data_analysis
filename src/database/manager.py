from typing import List, Type
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session, DeclarativeMeta
from pathlib import Path
import yaml

from src.config.paths import find_competition_root, find_nearest_config, find_project_root
from src.logging.setup import setup_logger  

# Initialize a logger for database operations
logger = setup_logger("database_manager", find_project_root() / "logs/database.log")

class DatabaseManager:
    """Handles database connections, table creation, and data insertion."""
    
    def __init__(self, config_name: str = "database.yaml", context_path: Path = None):
        self.config_path = find_nearest_config(
            start_path=context_path, config_name=config_name
        )
        self.config = self._load_config()

        self.db_config = self.config.get("db_config", {})
        self.logging_config = self.config.get("logging_config", {})

        relative_log_path = self.logging_config.get("log_path", "logs/database.log")

        log_path = find_competition_root(self.config_path) / relative_log_path

        self.logger = setup_logger("database_manager", log_path)
        self.logger.info(f"Setting log path: {log_path}")

        self.logger.info(f"Initialized DatabaseManager with config: {self.config_path}")

        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _load_config(self) -> dict:
        """Load database configuration."""
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded database config from {self.config_path}")
        return config

    def _create_engine(self):
        """Dynamically create a SQLAlchemy engine using extracted db_config."""
        required_keys = {"host", "port", "name", "user", "password"}
        missing_keys = required_keys - self.db_config.keys()

        if missing_keys:
            self.logger.error(f"Missing required database config keys: {missing_keys}")
            raise ValueError(f"Missing required config keys: {missing_keys}")

        try:
            engine = create_engine(
                f"postgresql://{self.db_config['user']}:{self.db_config['password']}@"
                f"{self.db_config['host']}:{self.db_config['port']}/{self.db_config['name']}"
            )
            self.logger.info("Database engine successfully created")
            return engine
        except Exception as e:
            self.logger.exception(f"Error creating database engine: {e}")
            raise

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def create_tables(self, models: List[Type[DeclarativeMeta]]) -> None:
        """Create database tables from ORM models."""
        try:
            for model in models:
                if hasattr(model, "__table__"):
                    model.__table__.create(bind=self.engine, checkfirst=True)
            self.logger.info("Tables created successfully")
        except SQLAlchemyError as e:
            self.logger.exception(f"Error creating tables: {e}")
            raise

    def insert_dataframe(self, df: pd.DataFrame, model: Type[DeclarativeMeta]) -> None:
        """Insert a pandas DataFrame into the database."""
        session = self.get_session()
        try:
            records = [model(**row) for row in df.to_dict(orient="records")]
            session.bulk_save_objects(records)
            session.commit()
            self.logger.info(f"Inserted {len(records)} records into {model.__tablename__}")
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.exception(f"Database error: {e}")
            raise
        finally:
            session.close()

    def with_db_session(self, func):
        """Decorator to manage database sessions."""
        def wrapper(*args, **kwargs):
            session = self.get_session()
            try:
                result = func(session, *args, **kwargs)
                session.commit()
                return result
            except Exception as e:
                session.rollback()
                self.logger.exception(f"Transaction failed: {e}")
                raise
            finally:
                session.close()
        return wrapper