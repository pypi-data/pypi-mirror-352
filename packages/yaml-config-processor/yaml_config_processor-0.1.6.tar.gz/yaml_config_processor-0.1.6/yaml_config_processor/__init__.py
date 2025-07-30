"""
YAML Config Processor

A package for processing configuration templates from YAML strings with JSON user configurations.
"""

from yaml_config_processor.processor import ConfigProcessor, TEMPLATE_META_SCHEMA

try:
    from yaml_config_processor._version import version as __version__
except ImportError:
    # Fallback for development mode
    __version__ = "0.1.6"  # Keep your current version as fallback

__all__ = ['ConfigProcessor', 'TEMPLATE_META_SCHEMA']
