import configparser
import logging
import os
import sys
from datetime import datetime
from logging import Logger
from logging import config as LoggerConfig
from pathlib import Path

from .config import logging_config

runtime_pth = Path(os.path.abspath(sys.argv[0])).parent
# Get the current date for the log filename
datestamp: str = datetime.now().strftime("%Y-%m-%d")

# Multiton state
_instances: dict[Path, Logger] = {}


def init_logger(
    log_dir: Path | None = None,
    config_path: Path | None = None,
    app_name: str = "myapp",
) -> Logger:
    # Ensure the log directory exists in the executing root
    if log_dir is None:
        log_dir = runtime_pth / "Logs"
    
    # Ensure log_dir is a Path object
    if isinstance(log_dir, str):
        log_dir = Path(log_dir)
    if log_dir in _instances:
        return _instances[log_dir]
    log_dir.mkdir(parents=True, exist_ok=True)
    log_filename: Path = log_dir / f"{app_name}_{datestamp}.log"

    if config_path is None:
        config_path = Path()

    # Check if the configuration file exists or roll back to the default configuration
    if config_path.is_file():
        # Load the configuration file
        config = configparser.ConfigParser()
        config.read(config_path)
        # Update the file handler's filename in the configuration
        config.set("handler_fileHandler", "args", f"(r'{log_filename}', 'a')")
        # Apply the logging configuration from config file
        LoggerConfig.fileConfig(config)

    else:
        # Update the file handler's filename in the configuration
        logging_config["handlers"]["fileHandler"]["filename"] = log_filename
        # Apply the logging configuration from defalut config dictionary
        LoggerConfig.dictConfig(logging_config)

    # Return the root logger
    _instances[log_dir] = logging.getLogger()

    return _instances[log_dir]


def clean_logs(log_dir: Path, days_count: int = 10) -> None:
    """
    Remove log files older than the specified number of days.

    :param log_dir: Path to the directory containing log files.
    :param days_count: Number of days to retain log files. Older files will be removed.
    """
    if not log_dir.is_dir():
        print(f"{log_dir} is not a valid directory.")
        return

    cutoff_time = datetime.now().timestamp() - (
        days_count * 86400
    )  # 86400 seconds in a day
    for log_file in log_dir.iterdir():
        if log_file.is_file() and log_file.suffix == ".log":
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    print(f"Deleted old log file: {log_file}")
                except Exception as e:
                    print(f"Failed to delete {log_file}: {e}")
