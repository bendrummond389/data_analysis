
import re
import pandas as pd
from typing import Dict, Any


def sanitize_column_name(column_name: str) -> str:
    """
    Sanitize a single column name by:
      - Converting camel case to snake case
      - Converting to lowercase
      - Replacing spaces and special characters with underscores
      - Removing leading/trailing whitespace
      - Ensuring the name is a valid Python identifier

    :param column_name: Original column name
    :return: Sanitized column name
    """
    # Convert camel case to snake case
    column_name = re.sub(r"(?<!^)([A-Z])", r"_\1", column_name)

    # Convert to lowercase and strip whitespace
    column_name = column_name.lower().strip()

    # Replace spaces and certain special characters with underscores
    column_name = re.sub(r"[\s/\-.,]+", "_", column_name)

    # Remove any remaining non-alphanumeric characters (except underscores)
    column_name = re.sub(r"[^a-z0-9_]", "", column_name)

    # Ensure the column name is a valid Python identifier
    if not column_name.isidentifier():
        # If not, prepend an underscore
        column_name = "_" + column_name

    return column_name


def clean_data(df: pd.DataFrame, cleaning_config: Dict[str, Any]) -> pd.DataFrame:
    """Clean DataFrame with configurable options."""
    try:
        # Apply column name sanitization
        if cleaning_config.get("sanitize_columns", True):
            df.columns = [sanitize_column_name(col) for col in df.columns]
        
        # Handle missing values
        if cleaning_config.get("drop_na", True):
            df.dropna(inplace=True)
        
        # Additional cleaning steps
        if cleaning_config.get("strip_strings", True):
            df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        return df
        
    except Exception as e:
        raise
