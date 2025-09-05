"""
Configuration Management for OpenAGI Platform

Handles configuration loading, validation, and management across
the entire platform ecosystem.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = "postgresql://localhost:5432/openagi"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
            "echo": self.echo
        }


@dataclass
class RedisConfig:
    """Redis configuration."""
    url: str = "redis://localhost:6379/0"
    max_connections: int = 20
    retry_on_timeout: bool = True
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[str, int] = field(default_factory=lambda: {})


@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False
    debug: bool = False
    log_level: str = "info"
    cors_origins: list = field(default_factory=lambda: ["*"])
    max_request_size: int = 16 * 1024 * 1024  # 16MB


@dataclass
class ModelsConfig:
    """AI models configuration."""
    cache_dir: str = "models/"
    max_models: int = 10
    default_models: list = field(default_factory=lambda: ["gpt-base", "vision-base"])
    auto_download: bool = True
    timeout_seconds: int = 300
    device: str = "auto"  # auto, cpu, cuda
    precision: str = "fp16"  # fp32, fp16, int8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cache_dir": self.cache_dir,
            "max_models": self.max_models,
            "default_models": self.default_models,
            "auto_download": self.auto_download,
            "timeout_seconds": self.timeout_seconds,
            "device": self.device,
            "precision": self.precision
        }


@dataclass
class TestingConfig:
    """Testing framework configuration."""
    enabled: bool = True
    auto_run: bool = False
    schedule: str = "0 */6 * * *"  # Every 6 hours
    interval_seconds: int = 21600  # 6 hours
    parallel_workers: int = 4
    max_test_duration: int = 3600  # 1 hour
    sample_rate: float = 0.01  # Run 1% of tests for quick validation
    comprehensive_sample_rate: float = 1.0  # Run all tests for comprehensive validation
    seed: int = 42
    categories_enabled: list = field(default_factory=lambda: [
        "functional", "performance", "robustness", "consistency",
        "integration", "security", "regression", "stress", 
        "compatibility", "edge_case"
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.""" 
        return {
            "enabled": self.enabled,
            "auto_run": self.auto_run,
            "schedule": self.schedule,
            "interval_seconds": self.interval_seconds,
            "parallel_workers": self.parallel_workers,
            "max_test_duration": self.max_test_duration,
            "sample_rate": self.sample_rate,
            "comprehensive_sample_rate": self.comprehensive_sample_rate,
            "seed": self.seed,
            "categories_enabled": self.categories_enabled
        }


@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration."""
    enabled: bool = True
    prometheus_port: int = 9090
    metrics_interval: int = 30
    retention_days: int = 30
    alerts_enabled: bool = True
    log_level: str = "info"
    export_metrics: bool = True


@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    enable_rate_limiting: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds


@dataclass
class Config:
    """Main configuration class."""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    models: ModelsConfig = field(default_factory=ModelsConfig)
    testing: TestingConfig = field(default_factory=TestingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Additional platform settings
    debug: bool = False
    environment: str = "development"
    timezone: str = "UTC"
    data_dir: str = "data/"
    logs_dir: str = "logs/"
    temp_dir: str = "tmp/"


class ConfigManager:
    """
    Configuration manager for the OpenAGI platform.
    
    Handles loading configuration from files, environment variables,
    and provides validation and defaults.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
        """
        self.config_path = config_path
        self._config: Optional[Config] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Start with default configuration
        config_dict = {}
        
        # Load from file if provided
        if self.config_path and os.path.exists(self.config_path):
            config_dict = self._load_config_file(self.config_path)
            logger.info("Configuration loaded from file", path=self.config_path)
        else:
            # Try to load from default locations
            default_paths = [
                "config.yaml",
                "config.yml", 
                "config.json",
                "configs/default.yaml",
                "configs/development.yaml"
            ]
            
            for path in default_paths:
                if os.path.exists(path):
                    config_dict = self._load_config_file(path)
                    logger.info("Configuration loaded from default location", path=path)
                    break
        
        # Override with environment variables
        env_overrides = self._load_env_overrides()
        config_dict = self._merge_dicts(config_dict, env_overrides)
        
        # Create configuration object
        self._config = self._create_config_object(config_dict)
        
        # Validate configuration
        self._validate_config()
        
        logger.info("Configuration initialized", environment=self._config.environment)
    
    def _load_config_file(self, path: str) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file."""
        try:
            with open(path, 'r') as f:
                if path.endswith(('.yaml', '.yml')):
                    return yaml.safe_load(f) or {}
                elif path.endswith('.json'):
                    return json.load(f) or {}
                else:
                    logger.warning("Unknown config file format", path=path)
                    return {}
        except Exception as e:
            logger.error("Failed to load config file", path=path, error=str(e))
            return {}
    
    def _load_env_overrides(self) -> Dict[str, Any]:
        """Load configuration overrides from environment variables."""
        overrides = {}
        
        # Database configuration
        if os.getenv("DATABASE_URL"):
            overrides.setdefault("database", {})["url"] = os.getenv("DATABASE_URL")
        if os.getenv("DATABASE_POOL_SIZE"):
            overrides.setdefault("database", {})["pool_size"] = int(os.getenv("DATABASE_POOL_SIZE"))
        
        # Redis configuration
        if os.getenv("REDIS_URL"):
            overrides.setdefault("redis", {})["url"] = os.getenv("REDIS_URL")
        
        # Server configuration
        if os.getenv("SERVER_HOST"):
            overrides.setdefault("server", {})["host"] = os.getenv("SERVER_HOST")
        if os.getenv("SERVER_PORT"):
            overrides.setdefault("server", {})["port"] = int(os.getenv("SERVER_PORT"))
        if os.getenv("SERVER_WORKERS"):
            overrides.setdefault("server", {})["workers"] = int(os.getenv("SERVER_WORKERS"))
        if os.getenv("DEBUG"):
            overrides.setdefault("server", {})["debug"] = os.getenv("DEBUG").lower() == "true"
        
        # Models configuration
        if os.getenv("MODELS_CACHE_DIR"):
            overrides.setdefault("models", {})["cache_dir"] = os.getenv("MODELS_CACHE_DIR")
        if os.getenv("MODELS_DEVICE"):
            overrides.setdefault("models", {})["device"] = os.getenv("MODELS_DEVICE")
        
        # Testing configuration
        if os.getenv("TESTING_ENABLED"):
            overrides.setdefault("testing", {})["enabled"] = os.getenv("TESTING_ENABLED").lower() == "true"
        if os.getenv("TESTING_AUTO_RUN"):
            overrides.setdefault("testing", {})["auto_run"] = os.getenv("TESTING_AUTO_RUN").lower() == "true"
        if os.getenv("TESTING_SAMPLE_RATE"):
            overrides.setdefault("testing", {})["sample_rate"] = float(os.getenv("TESTING_SAMPLE_RATE"))
        
        # Security configuration
        if os.getenv("SECRET_KEY"):
            overrides.setdefault("security", {})["secret_key"] = os.getenv("SECRET_KEY")
        
        # Global settings
        if os.getenv("ENVIRONMENT"):
            overrides["environment"] = os.getenv("ENVIRONMENT")
        if os.getenv("DATA_DIR"):
            overrides["data_dir"] = os.getenv("DATA_DIR")
        
        return overrides
    
    def _merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _create_config_object(self, config_dict: Dict[str, Any]) -> Config:
        """Create Config object from dictionary."""
        # Extract nested configurations
        database_config = DatabaseConfig(**config_dict.get("database", {}))
        redis_config = RedisConfig(**config_dict.get("redis", {}))
        server_config = ServerConfig(**config_dict.get("server", {}))
        models_config = ModelsConfig(**config_dict.get("models", {}))
        testing_config = TestingConfig(**config_dict.get("testing", {}))
        monitoring_config = MonitoringConfig(**config_dict.get("monitoring", {}))
        security_config = SecurityConfig(**config_dict.get("security", {}))
        
        # Extract global settings
        global_settings = {
            k: v for k, v in config_dict.items() 
            if k not in ["database", "redis", "server", "models", "testing", "monitoring", "security"]
        }
        
        return Config(
            database=database_config,
            redis=redis_config,
            server=server_config,
            models=models_config,
            testing=testing_config,
            monitoring=monitoring_config,
            security=security_config,
            **global_settings
        )
    
    def _validate_config(self) -> None:
        """Validate configuration settings."""
        if not self._config:
            raise ValueError("Configuration not loaded")
        
        # Validate database URL
        if not self._config.database.url:
            raise ValueError("Database URL is required")
        
        # Validate server settings
        if self._config.server.port < 1 or self._config.server.port > 65535:
            raise ValueError("Server port must be between 1 and 65535")
        
        if self._config.server.workers < 1:
            raise ValueError("Server workers must be at least 1")
        
        # Validate models settings
        if self._config.models.max_models < 1:
            raise ValueError("Max models must be at least 1")
        
        # Validate testing settings
        if self._config.testing.sample_rate < 0 or self._config.testing.sample_rate > 1:
            raise ValueError("Testing sample rate must be between 0 and 1")
        
        # Validate security settings
        if len(self._config.security.secret_key) < 32:
            logger.warning("Secret key should be at least 32 characters for security")
        
        # Create directories if they don't exist
        for dir_path in [self._config.data_dir, self._config.logs_dir, self._config.temp_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        Path(self._config.models.cache_dir).mkdir(parents=True, exist_ok=True)
    
    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration."""
        return self._config.database
    
    @property
    def redis(self) -> RedisConfig:
        """Get Redis configuration."""
        return self._config.redis
    
    @property
    def server(self) -> ServerConfig:
        """Get server configuration."""
        return self._config.server
    
    @property
    def models(self) -> ModelsConfig:
        """Get models configuration."""
        return self._config.models
    
    @property
    def testing(self) -> TestingConfig:
        """Get testing configuration."""
        return self._config.testing
    
    @property
    def monitoring(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        return self._config.monitoring
    
    @property
    def security(self) -> SecurityConfig:
        """Get security configuration."""
        return self._config.security
    
    @property
    def config(self) -> Config:
        """Get full configuration object."""
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key."""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                elif isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except (AttributeError, KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot notation key."""
        keys = key.split('.')
        target = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if hasattr(target, k):
                target = getattr(target, k)
            else:
                raise KeyError(f"Configuration key '{k}' not found")
        
        # Set the final value
        final_key = keys[-1]
        if hasattr(target, final_key):
            setattr(target, final_key, value)
        else:
            raise KeyError(f"Configuration key '{final_key}' not found")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "database": {
                "url": self._config.database.url,
                "pool_size": self._config.database.pool_size,
                "max_overflow": self._config.database.max_overflow,
                "pool_timeout": self._config.database.pool_timeout,
                "pool_recycle": self._config.database.pool_recycle,
                "echo": self._config.database.echo
            },
            "redis": {
                "url": self._config.redis.url,
                "max_connections": self._config.redis.max_connections,
                "retry_on_timeout": self._config.redis.retry_on_timeout,
                "socket_keepalive": self._config.redis.socket_keepalive,
                "socket_keepalive_options": self._config.redis.socket_keepalive_options
            },
            "server": {
                "host": self._config.server.host,
                "port": self._config.server.port,
                "workers": self._config.server.workers,
                "reload": self._config.server.reload,
                "debug": self._config.server.debug,
                "log_level": self._config.server.log_level,
                "cors_origins": self._config.server.cors_origins,
                "max_request_size": self._config.server.max_request_size
            },
            "models": {
                "cache_dir": self._config.models.cache_dir,
                "max_models": self._config.models.max_models,
                "default_models": self._config.models.default_models,
                "auto_download": self._config.models.auto_download,
                "timeout_seconds": self._config.models.timeout_seconds,
                "device": self._config.models.device,
                "precision": self._config.models.precision
            },
            "testing": {
                "enabled": self._config.testing.enabled,
                "auto_run": self._config.testing.auto_run,
                "schedule": self._config.testing.schedule,
                "interval_seconds": self._config.testing.interval_seconds,
                "parallel_workers": self._config.testing.parallel_workers,
                "max_test_duration": self._config.testing.max_test_duration,
                "sample_rate": self._config.testing.sample_rate,
                "comprehensive_sample_rate": self._config.testing.comprehensive_sample_rate,
                "seed": self._config.testing.seed,
                "categories_enabled": self._config.testing.categories_enabled
            },
            "monitoring": {
                "enabled": self._config.monitoring.enabled,
                "prometheus_port": self._config.monitoring.prometheus_port,
                "metrics_interval": self._config.monitoring.metrics_interval,
                "retention_days": self._config.monitoring.retention_days,
                "alerts_enabled": self._config.monitoring.alerts_enabled,
                "log_level": self._config.monitoring.log_level,
                "export_metrics": self._config.monitoring.export_metrics
            },
            "security": {
                "algorithm": self._config.security.algorithm,
                "access_token_expire_minutes": self._config.security.access_token_expire_minutes,
                "refresh_token_expire_days": self._config.security.refresh_token_expire_days,
                "password_min_length": self._config.security.password_min_length,
                "max_login_attempts": self._config.security.max_login_attempts,
                "lockout_duration_minutes": self._config.security.lockout_duration_minutes,
                "enable_rate_limiting": self._config.security.enable_rate_limiting,
                "rate_limit_requests": self._config.security.rate_limit_requests,
                "rate_limit_window": self._config.security.rate_limit_window
            },
            "debug": self._config.debug,
            "environment": self._config.environment,
            "timezone": self._config.timezone,
            "data_dir": self._config.data_dir,
            "logs_dir": self._config.logs_dir,
            "temp_dir": self._config.temp_dir
        }
    
    def save(self, path: str, format: str = "yaml") -> None:
        """Save configuration to file."""
        config_dict = self.to_dict()
        
        with open(path, 'w') as f:
            if format.lower() in ["yaml", "yml"]:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            elif format.lower() == "json":
                json.dump(config_dict, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        logger.info("Configuration saved", path=path, format=format)
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()
        logger.info("Configuration reloaded")


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def init_config(config_path: Optional[str] = None) -> ConfigManager:
    """Initialize global configuration manager."""
    global _config_manager
    _config_manager = ConfigManager(config_path)
    return _config_manager