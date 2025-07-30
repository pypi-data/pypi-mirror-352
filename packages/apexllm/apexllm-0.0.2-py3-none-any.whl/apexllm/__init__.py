"""
apexllm - A lightweight and efficient LLM utility package.
"""

__version__ = "0.0.2"
__author__ = "Apex Developer"

from .core import generate, LLMMODEL, validate_api_keys

__all__ = ["generate", "LLMMODEL", "validate_api_keys"] 