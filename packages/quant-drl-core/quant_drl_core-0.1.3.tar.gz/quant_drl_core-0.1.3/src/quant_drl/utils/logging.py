from loguru import logger
import os
import sys
from pathlib import Path


def setup_logger(
    log_path: str | Path = None,
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_stdout: bool = True,
) -> logger:
    """
    Configura el logger global de loguru para el proyecto.

    Args:
        log_path (str | Path): Ruta al archivo de log. Si None, se usa 'logs/main.log'.
        level (str): Nivel de logging (DEBUG, INFO, WARNING, ERROR, etc).
        log_to_file (bool): Si True, guarda logs en archivo.
        log_to_stdout (bool): Si True, imprime logs por terminal.

    Returns:
        logger: Instancia de loguru.logger ya configurada.
    """
    logger.remove()

    if log_to_stdout:
        logger.add(sys.stdout, level=level, enqueue=True)

    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        log_path = Path(log_path) if log_path else log_dir / "main.log"

        logger.add(
            log_path,
            rotation="10 MB",
            retention="10 days",
            level=level,
            enqueue=True,
            backtrace=True,
            diagnose=True,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
        )

    return logger