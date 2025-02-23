from typing import List, Type, Iterator, Dict
import contextlib
import pandas as pd
from sqlalchemy import create_engine, URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session, DeclarativeMeta
from pathlib import Path
import yaml

from src.config.paths import (
    find_project_root,
    find_nearest_config,
    find_project_root,
)
from src.logging.setup import setup_logger

# Initialize a logger for database operations
# _logger = setup_logger(
#     "database_manager_init", find_project_root() / "logs/database.log"
# )


class DatabaseManager:
    """Handles database connections, table creation, and data insertion."""

    def __init__(self, config: dict = None, config_path: Path = None):
        self.config = config
        self.config_path = config_path 
        self._configure_logger()
        self.engine = None
        self.SessionLocal = None


    def _configure_logger(self) -> None:
        """Configure instance logger based on config settings."""
        logging_config = self.config.get("logging", {})
        relative_log_path = logging_config.get("path", "logs/database.log")
        logger_name = logging_config.get("name", "database_manager")

        # Find project root based on config location or current directory
        start_path = self.config_path.parent if self.config_path else Path.cwd()
        base_path = find_project_root(start_path)
        
        log_path = base_path / relative_log_path
        self.logger = setup_logger(logger_name, log_path)
        self.logger.info(f"Logger configured with path: {log_path}")

    def _load_config(self) -> dict:
        """Load database configuration from YAML file."""
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            raise

    def _load_default_config(self):
        return {
            "host": "localhost",
            "port": 5432,
            "name": "default_db",
            "user": "postgres",
            "password": ""
        }
    
    @staticmethod
    def _load_yaml_config(config_path: Path):
        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise

    def _create_engine(self):
        """Dynamically create a SQLAlchemy engine using extracted db_config."""
        required_keys = {"host", "port", "name", "user", "password"}

        db_config = self.config.get("database", self._load_default_config())
        if missing := required_keys - db_config.keys():
            self.logger.error(f"Missing required config keys: {missing}")
            raise ValueError(f"Missing required config keys: {missing}")

        try:
            url = URL.create(
                drivername="postgresql",
                username=db_config["user"],
                password=db_config["password"],
                host=db_config["host"],
                port=db_config["port"],
                database=db_config["name"],
            )
            engine = create_engine(url)
            self.logger.info("Database engine created successfully")
            return engine
        except Exception as e:
            self.logger.exception(f"Engine creation failed: {e}")
            raise

    @classmethod
    def from_yaml(cls, config_path: Path):
        """Alternative constructor for file-based config"""
        config = cls._load_yaml_config(config_path)
        return cls(config=config, config_path=config_path)

    def connect(self):
        """Explicit method for engine creation"""
        if not self.engine:
            self.engine = self._create_engine()
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )


    @contextlib.contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Context manager for transactional database sessions"""
        if not self.SessionLocal:
            self.connect()
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.exception(f"Session rollback due to error: {e}")
            raise
        finally:
            session.close()

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
        """Insert DataFrame records into the database using bulk insert."""
        with self.session_scope() as session:
            session.bulk_insert_mappings(model, df.to_dict(orient="records"))
            self.logger.info(f"Inserted {len(df)} records into {model.__tablename__}")


