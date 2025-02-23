import pytest
from unittest.mock import Mock, patch, MagicMock, call
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from pathlib import Path
import yaml
import logging

from src.database.manager import DatabaseManager


@pytest.fixture
def mock_config():
    return {
        "db_config": {
            "host": "localhost",
            "port": 5432,
            "name": "testdb",
            "user": "user",
            "password": "pass",
        },
        "logging_config": {"log_path": "logs/test.log", "logger_name": "test_logger"},
    }


@pytest.fixture
def db_manager(mock_config, monkeypatch, tmp_path):
    # Create directory structure
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "database.yaml"
    config_file.touch()

    # Create logs directory to prevent FileNotFoundError
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Mock path finding functions
    monkeypatch.setattr(
        "src.database.manager.find_nearest_config", Mock(return_value=config_file)
    )
    # Fix: Mock the imported function in manager.py
    monkeypatch.setattr(
        "src.database.manager.find_competition_root", Mock(return_value=tmp_path)
    )

    # Mock config loading and engine creation
    with patch.object(DatabaseManager, "_load_config", return_value=mock_config):
        with patch("sqlalchemy.create_engine") as mock_create:
            mock_create.return_value = create_engine("sqlite:///:memory:")
            manager = DatabaseManager()
            return manager


def test_create_engine_success(db_manager):
    # Test with actual URL creation but mock engine
    with patch("sqlalchemy.create_engine") as mock_create:
        db_manager._create_engine()

        # Verify create_engine was called with expected arguments
        mock_create.assert_called_once()

        # Get the URL that was passed to create_engine
        called_url = mock_create.call_args[0][0]

        # Verify URL components
        assert called_url.drivername == "postgresql"
        assert called_url.username == "user"
        assert called_url.password == "pass"
        assert called_url.host == "localhost"
        assert called_url.port == 5432
        assert called_url.database == "testdb"
