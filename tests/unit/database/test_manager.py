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
            "password": "pass"
        },
        "logging_config": {
            "log_path": "logs/test.log",
            "logger_name": "test_logger"
        }
    }

@pytest.fixture
def mock_engine():
    return create_engine("sqlite:///:memory:")

def test_create_engine_success(db_manager):
    with patch("sqlalchemy.URL.create") as mock_url, \
         patch("sqlalchemy.create_engine") as mock_create:
        db_manager._create_engine()
        
        mock_url.assert_called_once_with(
            drivername="postgresql",
            username="user",
            password="pass",
            host="localhost",
            port=5432,
            database="testdb"
        )
        mock_create.assert_called_once()