from typing import List, Type, Iterator
import contextlib
import pandas as pd
from sqlalchemy import create_engine, URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session, DeclarativeMeta
from pathlib import Path
import yaml

from src.config.paths import find_competition_root, find_nearest_config, find_project_root
from src.logging.setup import setup_logger  

# Initialize a logger for database operations
_logger = setup_logger("database_manager_init", find_project_root() / "logs/database.log")

class DatabaseManager:
    """Handles database connections, table creation, and data insertion."""
    
    def __init__(self, config_name: str = "database.yaml", context_path: Path = None):
        self.config_path = find_nearest_config(
            start_path=context_path, config_name=config_name
        )
        self.config = self._load_config()
        self.db_config = self.config.get("db_config", {})
        self._configure_logger()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def _configure_logger(self) -> None:
        """Configure instance logger based on config settings."""
        logging_config = self.config.get("logging_config", {})
        relative_log_path = logging_config.get("log_path", "logs/database.log")
        logger_name = logging_config.get("logger_name", "database_manager")

        log_path = find_competition_root(self.config_path) / relative_log_path
        self.logger = setup_logger(logger_name, log_path)
        self.logger.info(f"Logger configured with path: {log_path}")

    def _load_config(self) -> dict:
        """Load database configuration from YAML file."""
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            _logger.info(f"Loaded database config from {self.config_path}")
            return config
        except Exception as e:
            _logger.exception(f"Error loading config: {e}")
            raise

    def _create_engine(self):
        """Dynamically create a SQLAlchemy engine using extracted db_config."""
        required_keys = {"host", "port", "name", "user", "password"}
        if missing := required_keys - self.db_config.keys():
            self.logger.error(f"Missing required config keys: {missing}")
            raise ValueError(f"Missing required config keys: {missing}")

        try:
            url = URL.create(
                drivername="postgresql",
                username=self.db_config["user"],
                password=self.db_config["password"],
                host=self.db_config["host"],
                port=self.db_config["port"],
                database=self.db_config["name"],
            )
            engine = create_engine(url)
            self.logger.info("Database engine created successfully")
            return engine
        except Exception as e:
            self.logger.exception(f"Engine creation failed: {e}")
            raise

    @contextlib.contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Context manager for transactional database sessions."""
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
            session.bulk_insert_mappings(
                model, df.to_dict(orient="records")
            )
            self.logger.info(
                f"Inserted {len(df)} records into {model.__tablename__}"
            )

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