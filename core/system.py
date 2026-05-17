"""
REUserBot Core System Module
Handles system initialization, logging, and update checking
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"userbot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("REUserBot")

# System info
BRANCH = "Official"
VERSION = "1.0.0"

def get_system_info():
    """Returns system information"""
    return {
        "branch": BRANCH,
        "version": VERSION,
        "python_version": sys.version,
        "log_file": str(log_file)
    }

def log_startup():
    """Log startup message"""
    logger.info("REUserBot Started")
    logger.info(f"Branch: {BRANCH}")
    logger.info(f"Version: {VERSION}")

def log_error(error_message):
    """Log error message"""
    logger.error(error_message)

def log_info(info_message):
    """Log info message"""
    logger.info(info_message)
