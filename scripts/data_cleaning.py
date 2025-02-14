import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)


def sanitize_column_name(column_name: str) -> str:
    """
    Sanitize a single column name by:
      - Converting to lowercase
      - Replacing spaces and special characters with underscores
      - Removing leading/trailing whitespace
      - Ensuring the name is a valid Python identifier

    :param column_name: Original column name
    :return: Sanitized column name
    """
    # Convert to lowercase and strip whitespace
    column_name = column_name.lower().strip()

    # Replace spaces and certain special characters with underscores
    column_name = re.sub(r'[\s/\-.,]+', '_', column_name)

    # Remove any remaining non-alphanumeric characters (except underscores)
    column_name = re.sub(r'[^a-z0-9_]', '', column_name)

    # Ensure the column name is a valid Python identifier
    if not column_name.isidentifier():
        # If not, prepend an underscore
        column_name = '_' + column_name

    return column_name


def clean_data(raw_path: str, cleaned_path: str) -> None:
    """
    Read raw data, clean it, and save the cleaned data to a new file.

    :param raw_path: Path to the CSV file containing raw data
    :param cleaned_path: Path where the cleaned CSV file will be saved
    :raises Exception: If any errors occur during data loading, cleaning, or saving
    """
    try:
        # Load raw data
        df = pd.read_csv(raw_path)
        logger.info(f"Raw data loaded from '{raw_path}'. Shape: {df.shape}")

        # Drop rows with missing values
        df.dropna(inplace=True)

        # Sanitize column names
        df.columns = [sanitize_column_name(col) for col in df.columns]

        # Save cleaned data
        df.to_csv(cleaned_path, index=False)
        logger.info(f"Cleaned data saved to '{cleaned_path}'. Shape: {df.shape}")

    except Exception as e:
        logger.error(f"Error in clean_data: {e}")
        raise


if __name__ == "__main__":
    # Configure logging for script execution
    logging.basicConfig(level=logging.INFO)

    # Example usage
    clean_data("raw_data.csv", "cleaned_data.csv")
