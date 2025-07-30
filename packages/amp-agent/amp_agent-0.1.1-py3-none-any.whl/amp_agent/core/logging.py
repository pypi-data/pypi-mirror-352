import logging
import os
import colorlog

def setup_logging():
    """
    Configure logging for the AMP agent system.
    Sets up root logger and custom loggers with colored output.
    """
    # Set root logger to WARNING to suppress most third-party logs
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    
    # Create a custom formatter with colors for standard log levels
    standard_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s - %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # Create custom formatters for specific loggers
    amp_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s - %(message)s",
        log_colors={
            'DEBUG': 'purple',
            'INFO': 'purple',
            'WARNING': 'purple',
            'ERROR': 'purple',
            'CRITICAL': 'purple',
        }
    )
    
    subs_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s - %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'cyan',
            'WARNING': 'cyan',
            'ERROR': 'cyan',
            'CRITICAL': 'cyan',
        }
    )
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler with the standard formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(standard_formatter)
    root_logger.addHandler(console_handler)
    
    # Create and configure the amp-example logger
    amp_logger = logging.getLogger("SWMH")
    amp_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers from the amp-example logger
    for handler in amp_logger.handlers[:]:
        amp_logger.removeHandler(handler)
    
    # Add a handler with the purple formatter
    amp_handler = logging.StreamHandler()
    amp_handler.setFormatter(amp_formatter)
    amp_logger.addHandler(amp_handler)
    
    # Prevent propagation to root logger to avoid duplicate logs
    amp_logger.propagate = False
    
    # Create and configure the subs logger
    subs_logger = logging.getLogger("subs")
    subs_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers from the subs logger
    for handler in subs_logger.handlers[:]:
        subs_logger.removeHandler(handler)
    
    # Add a handler with the cyan formatter
    subs_handler = logging.StreamHandler()
    subs_handler.setFormatter(subs_formatter)
    subs_logger.addHandler(subs_handler)
    
    # Prevent propagation to root logger to avoid duplicate logs
    subs_logger.propagate = False
    
    # Allow log level to be configured via environment variable
    amp_log_level = os.environ.get("AMP_LOG_LEVEL", "INFO").upper()
    if hasattr(logging, amp_log_level):
        amp_logger.setLevel(getattr(logging, amp_log_level))
        subs_logger.setLevel(getattr(logging, amp_log_level))
    
    # Log the current configuration
    amp_logger.info(f"Logging configured: amp-example={amp_log_level}, all other loggers=WARNING")
    
    return amp_logger, subs_logger

# Initialize loggers
logger, subs_logger = setup_logging()
