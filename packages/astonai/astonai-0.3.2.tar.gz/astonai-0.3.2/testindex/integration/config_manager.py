"""
Configuration Manager for TestIndex Integration.

This module provides centralized configuration management for regression guard
settings, CI/CD integration, and project-specific configurations.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict

from testindex.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RegressionConfig:
    """Configuration for regression guard analysis."""
    max_risk_score: float = 0.7
    max_impacted_nodes: int = 50
    min_test_coverage: float = 0.8
    max_critical_nodes: int = 10
    analysis_depth: int = 2
    enable_blocking: bool = True
    enable_ci_integration: bool = True
    
    
@dataclass
class CIIntegrationConfig:
    """Configuration for CI/CD integration."""
    auto_comment_prs: bool = True
    block_high_risk_merges: bool = True
    require_manual_approval: bool = False
    generate_artifacts: bool = True
    artifact_retention_days: int = 30
    notification_channels: list = None
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = []


@dataclass
class OutputConfig:
    """Configuration for output formats and destinations."""
    default_format: str = "both"  # "json", "text", "both"
    json_output_path: Optional[str] = None
    detailed_output_path: Optional[str] = None
    enable_rich_output: bool = True
    log_level: str = "INFO"


@dataclass
class ProjectConfig:
    """Complete project configuration for TestIndex."""
    regression: RegressionConfig
    ci_integration: CIIntegrationConfig
    output: OutputConfig
    project_name: Optional[str] = None
    version: str = "1.0"


class ConfigManager:
    """Manages configuration for TestIndex regression guard and integrations."""
    
    DEFAULT_CONFIG_NAMES = [
        ".testindex.yml",
        ".testindex.yaml", 
        ".testindex.json",
        "testindex.yml",
        "testindex.yaml",
        "testindex.json"
    ]
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager.
        
        Args:
            config_path: Optional path to specific config file
        """
        self.config_path = config_path
        self._config: Optional[ProjectConfig] = None
        
    def load_config(self, search_paths: Optional[list] = None) -> ProjectConfig:
        """Load configuration from file or create default.
        
        Args:
            search_paths: Optional list of paths to search for config files
            
        Returns:
            Loaded or default ProjectConfig
        """
        if self._config:
            return self._config
            
        # Try to load from specified path first
        if self.config_path and self.config_path.exists():
            self._config = self._load_from_file(self.config_path)
            logger.info(f"Loaded configuration from {self.config_path}")
            return self._config
            
        # Search for config files in default locations
        search_locations = search_paths or [Path.cwd()]
        
        for location in search_locations:
            for config_name in self.DEFAULT_CONFIG_NAMES:
                config_file = location / config_name
                if config_file.exists():
                    try:
                        self._config = self._load_from_file(config_file)
                        self.config_path = config_file
                        logger.info(f"Loaded configuration from {config_file}")
                        return self._config
                    except Exception as e:
                        logger.warning(f"Failed to load config from {config_file}: {e}")
                        continue
        
        # No config found, create default
        logger.info("No configuration file found, using defaults")
        self._config = self._create_default_config()
        return self._config
    
    def save_config(self, config: ProjectConfig, output_path: Optional[Path] = None) -> Path:
        """Save configuration to file.
        
        Args:
            config: Configuration to save
            output_path: Optional path to save to (defaults to current config path)
            
        Returns:
            Path where config was saved
        """
        save_path = output_path or self.config_path or Path(".testindex.yml")
        
        # Determine format from extension
        if save_path.suffix in ['.yml', '.yaml']:
            self._save_yaml(config, save_path)
        elif save_path.suffix == '.json':
            self._save_json(config, save_path)
        else:
            # Default to YAML
            save_path = save_path.with_suffix('.yml')
            self._save_yaml(config, save_path)
            
        self.config_path = save_path
        self._config = config
        logger.info(f"Saved configuration to {save_path}")
        return save_path
    
    def get_config(self) -> ProjectConfig:
        """Get current configuration, loading if necessary.
        
        Returns:
            Current ProjectConfig
        """
        if not self._config:
            return self.load_config()
        return self._config
    
    def update_from_env(self, config: Optional[ProjectConfig] = None) -> ProjectConfig:
        """Update configuration from environment variables.
        
        Args:
            config: Optional config to update (uses current if not provided)
            
        Returns:
            Updated configuration
        """
        if config is None:
            config = self.get_config()
            
        # Update regression settings from environment
        if os.getenv('TESTINDEX_MAX_RISK_SCORE'):
            config.regression.max_risk_score = float(os.getenv('TESTINDEX_MAX_RISK_SCORE'))
        if os.getenv('TESTINDEX_MAX_IMPACTED_NODES'):
            config.regression.max_impacted_nodes = int(os.getenv('TESTINDEX_MAX_IMPACTED_NODES'))
        if os.getenv('TESTINDEX_MIN_TEST_COVERAGE'):
            config.regression.min_test_coverage = float(os.getenv('TESTINDEX_MIN_TEST_COVERAGE'))
        if os.getenv('TESTINDEX_MAX_CRITICAL_NODES'):
            config.regression.max_critical_nodes = int(os.getenv('TESTINDEX_MAX_CRITICAL_NODES'))
        if os.getenv('TESTINDEX_ANALYSIS_DEPTH'):
            config.regression.analysis_depth = int(os.getenv('TESTINDEX_ANALYSIS_DEPTH'))
        if os.getenv('TESTINDEX_ENABLE_BLOCKING'):
            config.regression.enable_blocking = os.getenv('TESTINDEX_ENABLE_BLOCKING').lower() == 'true'
            
        # Update CI integration settings
        if os.getenv('TESTINDEX_AUTO_COMMENT_PRS'):
            config.ci_integration.auto_comment_prs = os.getenv('TESTINDEX_AUTO_COMMENT_PRS').lower() == 'true'
        if os.getenv('TESTINDEX_BLOCK_HIGH_RISK'):
            config.ci_integration.block_high_risk_merges = os.getenv('TESTINDEX_BLOCK_HIGH_RISK').lower() == 'true'
        if os.getenv('TESTINDEX_REQUIRE_APPROVAL'):
            config.ci_integration.require_manual_approval = os.getenv('TESTINDEX_REQUIRE_APPROVAL').lower() == 'true'
            
        # Update output settings
        if os.getenv('TESTINDEX_OUTPUT_FORMAT'):
            config.output.default_format = os.getenv('TESTINDEX_OUTPUT_FORMAT')
        if os.getenv('TESTINDEX_JSON_OUTPUT'):
            config.output.json_output_path = os.getenv('TESTINDEX_JSON_OUTPUT')
        if os.getenv('TESTINDEX_DETAILED_OUTPUT'):
            config.output.detailed_output_path = os.getenv('TESTINDEX_DETAILED_OUTPUT')
        if os.getenv('TESTINDEX_LOG_LEVEL'):
            config.output.log_level = os.getenv('TESTINDEX_LOG_LEVEL')
            
        self._config = config
        return config
    
    def create_sample_config(self, output_path: Optional[Path] = None) -> Path:
        """Create a sample configuration file with documentation.
        
        Args:
            output_path: Path to write sample config
            
        Returns:
            Path where sample config was written
        """
        save_path = output_path or Path(".testindex.sample.yml")
        
        sample_config = self._create_default_config()
        
        # Create YAML with comments
        yaml_content = f"""# TestIndex Regression Guard Configuration
# This file configures regression analysis and CI/CD integration

# Project metadata
project_name: "My Project"
version: "1.0"

# Regression analysis settings
regression:
  # Risk score threshold (0.0-1.0, higher = more restrictive)
  max_risk_score: {sample_config.regression.max_risk_score}
  
  # Maximum number of impacted nodes to allow
  max_impacted_nodes: {sample_config.regression.max_impacted_nodes}
  
  # Minimum test coverage ratio required (0.0-1.0)
  min_test_coverage: {sample_config.regression.min_test_coverage}
  
  # Maximum number of critical nodes to allow
  max_critical_nodes: {sample_config.regression.max_critical_nodes}
  
  # Analysis depth for call graph traversal
  analysis_depth: {sample_config.regression.analysis_depth}
  
  # Whether to block merges based on analysis
  enable_blocking: {str(sample_config.regression.enable_blocking).lower()}
  
  # Whether to enable CI/CD integration
  enable_ci_integration: {str(sample_config.regression.enable_ci_integration).lower()}

# CI/CD integration settings
ci_integration:
  # Automatically comment on pull requests
  auto_comment_prs: {str(sample_config.ci_integration.auto_comment_prs).lower()}
  
  # Block high-risk merges automatically
  block_high_risk_merges: {str(sample_config.ci_integration.block_high_risk_merges).lower()}
  
  # Require manual approval for medium/high risk changes
  require_manual_approval: {str(sample_config.ci_integration.require_manual_approval).lower()}
  
  # Generate analysis artifacts
  generate_artifacts: {str(sample_config.ci_integration.generate_artifacts).lower()}
  
  # Artifact retention period (days)
  artifact_retention_days: {sample_config.ci_integration.artifact_retention_days}
  
  # Notification channels (optional)
  notification_channels: []
    # - slack: "#dev-alerts"
    # - email: "team@example.com"

# Output configuration
output:
  # Default output format: "json", "text", or "both"
  default_format: "{sample_config.output.default_format}"
  
  # Optional paths for output files
  json_output_path: null
  detailed_output_path: null
  
  # Enable rich console output
  enable_rich_output: {str(sample_config.output.enable_rich_output).lower()}
  
  # Log level: DEBUG, INFO, WARNING, ERROR
  log_level: "{sample_config.output.log_level}"
"""
        
        with open(save_path, 'w') as f:
            f.write(yaml_content)
            
        logger.info(f"Created sample configuration at {save_path}")
        return save_path
    
    def validate_config(self, config: Optional[ProjectConfig] = None) -> bool:
        """Validate configuration settings.
        
        Args:
            config: Optional config to validate (uses current if not provided)
            
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if config is None:
            config = self.get_config()
            
        # Validate regression settings
        if not 0.0 <= config.regression.max_risk_score <= 1.0:
            raise ValueError(f"max_risk_score must be between 0.0 and 1.0, got {config.regression.max_risk_score}")
            
        if config.regression.max_impacted_nodes <= 0:
            raise ValueError(f"max_impacted_nodes must be positive, got {config.regression.max_impacted_nodes}")
            
        if not 0.0 <= config.regression.min_test_coverage <= 1.0:
            raise ValueError(f"min_test_coverage must be between 0.0 and 1.0, got {config.regression.min_test_coverage}")
            
        if config.regression.max_critical_nodes < 0:
            raise ValueError(f"max_critical_nodes must be non-negative, got {config.regression.max_critical_nodes}")
            
        if config.regression.analysis_depth < 1:
            raise ValueError(f"analysis_depth must be at least 1, got {config.regression.analysis_depth}")
            
        # Validate output settings
        if config.output.default_format not in ["json", "text", "both"]:
            raise ValueError(f"default_format must be 'json', 'text', or 'both', got {config.output.default_format}")
            
        if config.output.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            raise ValueError(f"log_level must be one of DEBUG/INFO/WARNING/ERROR, got {config.output.log_level}")
            
        # Validate CI integration settings
        if config.ci_integration.artifact_retention_days < 1:
            raise ValueError(f"artifact_retention_days must be at least 1, got {config.ci_integration.artifact_retention_days}")
            
        logger.info("Configuration validation passed")
        return True
    
    def _load_from_file(self, config_path: Path) -> ProjectConfig:
        """Load configuration from a specific file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Loaded ProjectConfig
            
        Raises:
            ValueError: If file format is unsupported or invalid
        """
        if not config_path.exists():
            raise ValueError(f"Configuration file not found: {config_path}")
            
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                elif config_path.suffix == '.json':
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
                    
            return self._dict_to_config(data)
            
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {config_path}: {e}")
    
    def _dict_to_config(self, data: Dict[str, Any]) -> ProjectConfig:
        """Convert dictionary to ProjectConfig.
        
        Args:
            data: Dictionary with configuration data
            
        Returns:
            ProjectConfig instance
        """
        # Create default config and update with provided data
        config = self._create_default_config()
        
        if 'project_name' in data:
            config.project_name = data['project_name']
        if 'version' in data:
            config.version = data['version']
            
        # Update regression settings
        if 'regression' in data:
            reg_data = data['regression']
            for key, value in reg_data.items():
                if hasattr(config.regression, key):
                    setattr(config.regression, key, value)
                    
        # Update CI integration settings
        if 'ci_integration' in data:
            ci_data = data['ci_integration']
            for key, value in ci_data.items():
                if hasattr(config.ci_integration, key):
                    setattr(config.ci_integration, key, value)
                    
        # Update output settings
        if 'output' in data:
            output_data = data['output']
            for key, value in output_data.items():
                if hasattr(config.output, key):
                    setattr(config.output, key, value)
                    
        return config
    
    def _create_default_config(self) -> ProjectConfig:
        """Create default configuration.
        
        Returns:
            Default ProjectConfig
        """
        return ProjectConfig(
            regression=RegressionConfig(),
            ci_integration=CIIntegrationConfig(),
            output=OutputConfig()
        )
    
    def _save_yaml(self, config: ProjectConfig, path: Path) -> None:
        """Save configuration as YAML.
        
        Args:
            config: Configuration to save
            path: Path to save to
        """
        data = asdict(config)
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def _save_json(self, config: ProjectConfig, path: Path) -> None:
        """Save configuration as JSON.
        
        Args:
            config: Configuration to save  
            path: Path to save to
        """
        data = asdict(config)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2) 