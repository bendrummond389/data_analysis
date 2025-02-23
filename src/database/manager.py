# Standard library
import contextlib
import logging
from pathlib import Path
from typing import Dict, Iterator, List, Type

# Third-party
import pandas as pd
import yaml
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeMeta, Session, sessionmaker

# Project modules
from src.logging.logging import AppLogger


class DatabaseManager:
    """Centralized database connection and operation management.
    
    Features:
    - Dynamic engine configuration
    - Transactional session management
    - ORM integration
    - Bulk data operations
    - Connection pooling
    - Configurable logging

    Usage:
    >>> logger = AppLogger(...)
    >>> db = DatabaseManager.from_yaml(Path("config/db.yaml"), logger)
    >>> with db.session_scope() as session:
    ...     session.query(User).all()
    """

    # --------------------------
    # Initialization & Configuration
    # --------------------------

    def __init__(self, config: Dict, logger: AppLogger) -> None:
        self.config = config
        self.logger = logger
        self._engine = None

    @classmethod
    def from_yaml(cls, config_path: Path, logger: AppLogger) -> "DatabaseManager":
        """Create instance from YAML configuration file.
        
        Args:
            config_path: Path to YAML configuration file
            logger: Preconfigured application logger
        """
        return cls(
            config=cls._load_yaml_config(config_path),
            logger=logger
        )

    # --------------------------
    # Core Engine Configuration
    # --------------------------

    @staticmethod
    def _load_yaml_config(config_path: Path) -> Dict:
        """Load and validate database configuration from YAML."""
        try:
            with config_path.open("r") as f:
                return yaml.safe_load(f) or {}
        except (FileNotFoundError, yaml.YAMLError) as e:
            raise ValueError(f"Failed to load database config: {e}") from e

    @property
    def engine(self):
        """Lazy-loaded SQLAlchemy engine instance."""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    def _create_engine(self):
        """Construct and validate SQLAlchemy engine with connection pooling."""
        db_config = self.config.get("database", self._default_db_config())
        self._validate_db_config(db_config)

        engine = create_engine(
            self._build_connection_url(db_config),
            pool_size=10,
            max_overflow=2,
            pool_recycle=300
        )
        
        self._test_connection(engine)
        self.logger.info(f"Engine initialized: {engine}")
        return engine

    def _test_connection(self, engine) -> None:
        """Validate database connectivity."""
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    # --------------------------
    # Configuration Helpers
    # --------------------------

    def validate_connection(self) -> None:
        """Public method to verify active database connection."""
        try:
            if self.engine is None:
                raise RuntimeError("Database engine not initialized")
            self.logger.info("Database connection validated")
        except Exception as e:
            self.logger.exception("Connection validation failed")
            raise

    @staticmethod
    def _default_db_config() -> Dict:
        """Default fallback configuration values."""
        return {
            "host": "localhost",
            "port": 5432,
            "name": "default_db",
            "user": "postgres",
            "password": ""
        }

    def _validate_db_config(self, config: Dict) -> None:
        """Ensure required connection parameters exist."""
        required = {"host", "port", "name", "user", "password"}
        if missing := required - config.keys():
            raise ValueError(f"Missing configuration keys: {missing}")

    @staticmethod
    def _build_connection_url(config: Dict) -> URL:
        """Construct PostgreSQL connection URL."""
        return URL.create(
            drivername="postgresql",
            username=config["user"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
            database=config["name"],
        )

    # --------------------------
    # Session Management
    # --------------------------

    @property
    def SessionLocal(self):
        """Database session factory."""
        if not hasattr(self, "_SessionLocal"):
            # Ensure engine exists before creating session maker
            engine = self.engine  
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        return self._SessionLocal

    @contextlib.contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Transactional session context manager with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.exception("Session rollback due to error")
            raise
        finally:
            session.close()

    # --------------------------
    # Database Operations
    # --------------------------

    def create_tables(self, models: List[Type[DeclarativeMeta]]) -> None:
        """Create database tables from SQLAlchemy models."""
        try:
            self.logger.info(f"Creating tables for {len(models)} models")
            
            for model in models:
                if hasattr(model, "__table__"):
                    model.__table__.create(bind=self.engine, checkfirst=True)
            
            self.logger.info(f"Successfully created {len(models)} tables")
        except SQLAlchemyError as e:
            self.logger.exception("Table creation failed")
            raise

    def insert_dataframe(self, df: pd.DataFrame, model: Type[DeclarativeMeta]) -> None:
        """Bulk insert DataFrame records into database."""
        with self.session_scope() as session:
            session.bulk_insert_mappings(
                model, 
                df.to_dict(orient="records")
            )
            self.logger.info(
                f"Inserted {len(df)} records into {model.__tablename__}"
            )

    def dispose(self) -> None:
        """Clean up engine resources and connections."""
        if self._engine:
            self._engine.dispose()
            self.logger.info("Database engine resources released")