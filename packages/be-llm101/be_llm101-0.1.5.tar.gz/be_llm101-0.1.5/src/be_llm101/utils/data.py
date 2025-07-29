"""
Data utility functions for be-llm101 package.
"""

from pathlib import Path


def get_data_path(filename: str = "IT_survey.csv") -> str:
    """
    Get the path to a data file included with the package.

    Args:
        filename: Name of the data file (default: "IT_survey.csv")

    Returns:
        Path to the data file

    Example:
        >>> from be_llm101.utils.data import get_data_path
        >>> path = get_data_path("IT_survey.csv")
        >>> df = pd.read_csv(path)
    """
    # Get the utils directory, then go up to be_llm101 package directory
    utils_dir = Path(__file__).parent
    package_dir = utils_dir.parent
    data_dir = package_dir / "data"

    return str(data_dir / filename)


def load_data(filename: str = "IT_survey.csv"):
    """
    Load data as a pandas DataFrame (convenience function).

    Args:
        filename: Name of the data file (default: "IT_survey.csv")

    Returns:
        pandas.DataFrame with the data

    Example:
        >>> from be_llm101.utils.data import load_data
        >>> df = load_data()
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required to use load_data(). Install with: pip install pandas"
        )

    path = get_data_path(filename)
    return pd.read_csv(
        path, usecols=["ID", "Feedback"], dtype={"ID": int, "Feedback": str}
    )
