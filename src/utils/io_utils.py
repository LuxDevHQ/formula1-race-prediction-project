"""Helper functions for filesystem I/O used across the pipeline."""

from pathlib import Path
import pandas as pd


def ensure_dir(path: str) -> Path:
    """Create directory if it does not exist and return Path."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_csv(df: pd.DataFrame, path: str) -> None:
    """Persist DataFrame as CSV without index."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_parquet(df: pd.DataFrame, path: str) -> None:
    """Persist DataFrame as parquet for fast downstream loading."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
