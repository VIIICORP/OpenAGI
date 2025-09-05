"""Structured logging system for OpenAGI."""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import structlog
    from structlog.typing import FilteringBoundLogger
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    FilteringBoundLogger = object


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    json_logs: bool = True,
    enable_colors: bool = True,
) -> None:
    """Setup structured logging for OpenAGI."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )
    
    if not STRUCTLOG_AVAILABLE:
        return
    
    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        if enable_colors and sys.stdout.isatty():
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        else:
            processors.append(structlog.dev.ConsoleRenderer(colors=False))
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        
        if json_logs:
            file_formatter = logging.Formatter('%(message)s')
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        file_handler.setFormatter(file_formatter)
        
        # Add file handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "openagi"):
    """Get a structured logger instance."""
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


class OpenAGILogger:
    """Enhanced logger with OpenAGI-specific features."""
    
    def __init__(self, name: str = "openagi"):
        if STRUCTLOG_AVAILABLE:
            self.logger = structlog.get_logger(name)
        else:
            self.logger = logging.getLogger(name)
        self._context: Dict[str, Any] = {}
    
    def bind(self, **kwargs: Any) -> "OpenAGILogger":
        """Bind context to logger."""
        new_logger = OpenAGILogger(self.logger.name if hasattr(self.logger, 'name') else "openagi")
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, 'bind'):
            new_logger.logger = self.logger.bind(**kwargs)
        else:
            new_logger.logger = self.logger
        new_logger._context = {**self._context, **kwargs}
        return new_logger
    
    def with_component(self, component: str) -> "OpenAGILogger":
        """Add component context."""
        return self.bind(component=component)
    
    def with_session(self, session_id: str) -> "OpenAGILogger":
        """Add session context."""
        return self.bind(session_id=session_id)
    
    def with_user(self, user_id: str) -> "OpenAGILogger":
        """Add user context."""
        return self.bind(user_id=user_id)
    
    def _format_message(self, msg: str, **kwargs: Any) -> str:
        """Format message with context."""
        if kwargs or self._context:
            context = {**self._context, **kwargs}
            context_str = " ".join(f"{k}={v}" for k, v in context.items())
            return f"{msg} {context_str}"
        return msg
    
    def debug(self, msg: str, **kwargs: Any) -> None:
        """Log debug message."""
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, 'debug'):
            self.logger.debug(msg, **kwargs)
        else:
            self.logger.debug(self._format_message(msg, **kwargs))
    
    def info(self, msg: str, **kwargs: Any) -> None:
        """Log info message."""
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, 'info'):
            self.logger.info(msg, **kwargs)
        else:
            self.logger.info(self._format_message(msg, **kwargs))
    
    def warning(self, msg: str, **kwargs: Any) -> None:
        """Log warning message."""
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, 'warning'):
            self.logger.warning(msg, **kwargs)
        else:
            self.logger.warning(self._format_message(msg, **kwargs))
    
    def error(self, msg: str, **kwargs: Any) -> None:
        """Log error message."""
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, 'error'):
            self.logger.error(msg, **kwargs)
        else:
            self.logger.error(self._format_message(msg, **kwargs))
    
    def critical(self, msg: str, **kwargs: Any) -> None:
        """Log critical message."""
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, 'critical'):
            self.logger.critical(msg, **kwargs)
        else:
            self.logger.critical(self._format_message(msg, **kwargs))
    
    def exception(self, msg: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, 'exception'):
            self.logger.exception(msg, **kwargs)
        else:
            self.logger.exception(self._format_message(msg, **kwargs))
    
    def metric(self, name: str, value: float, **tags: Any) -> None:
        """Log a metric."""
        self.info(
            "metric",
            metric_name=name,
            metric_value=value,
            metric_type="gauge",
            **tags
        )
    
    def event(self, event_type: str, **data: Any) -> None:
        """Log an event."""
        self.info(
            "event",
            event_type=event_type,
            **data
        )
    
    def audit(self, action: str, **context: Any) -> None:
        """Log an audit event."""
        self.info(
            "audit",
            action=action,
            audit=True,
            **context
        )


# Global logger instance
_global_logger: Optional[OpenAGILogger] = None


def get_openagi_logger(name: str = "openagi") -> OpenAGILogger:
    """Get the global OpenAGI logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = OpenAGILogger(name)
    return _global_logger


def configure_logging_from_config(config) -> None:
    """Configure logging from OpenAGI config."""
    setup_logging(
        level=config.monitoring.log_level,
        log_file=config.monitoring.log_file,
        json_logs=config.environment != "development",
        enable_colors=config.environment == "development",
    )