"""
Configuration loader for YAML prompt files.
"""
import os
import yaml
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_prompt_config(config_name: str) -> Dict[str, Any]:
    """
    Load agent configuration from YAML file.
    
    Args:
        config_name: Name of the config file (without .yaml extension)
        
    Returns:
        Dictionary containing the agent configuration
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the YAML is invalid
    """
    # Get the path to the resources directory relative to this module
    current_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(current_dir, "..", "resources")
    config_path = os.path.join(resources_dir, f"{config_name}.yaml")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ['name', 'description', 'prompt']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in {config_path}")
        
        # Ensure tools field exists
        if 'tools' not in config:
            config['tools'] = []
        
        logger.info(f"Loaded configuration for {config['name']}")
        return config
        
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {config_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading config {config_path}: {e}")
        raise


def get_system_prompt(config: Dict[str, Any]) -> str:
    """
    Extract system prompt from configuration.
    
    Args:
        config: Agent configuration dictionary
        
    Returns:
        System prompt string
    """
    prompt_config = config.get('prompt', {})
    if isinstance(prompt_config, dict):
        return prompt_config.get('system_prompt', '')
    return str(prompt_config)


def get_user_prompt(config: Dict[str, Any]) -> str:
    """
    Extract user prompt from configuration.
    
    Args:
        config: Agent configuration dictionary
        
    Returns:
        User prompt string
    """
    prompt_config = config.get('prompt', {})
    if isinstance(prompt_config, dict):
        return prompt_config.get('user_prompt', '')
    return ''
