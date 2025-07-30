"""
Configuration data models for Vaahai.

This module contains Pydantic models that define the structure of the configuration.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from vaahai.core.config.enums import ReviewDepth, ReviewFocus, OutputFormat


# Current schema version
CURRENT_SCHEMA_VERSION = 1


class LLMConfig(BaseModel):
    """LLM configuration settings."""
    provider: str = "openai"
    model: str = "gpt-4"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000
    autogen_enabled: bool = True  # Enable/disable Autogen integration


class AutogenConfig(BaseModel):
    """Autogen framework configuration."""
    enabled: bool = True
    default_model: str = "gpt-3.5-turbo"
    temperature: float = 0
    use_docker: bool = False
    docker_image: str = "python:3.9-slim"


class ReviewConfig(BaseModel):
    """Review command configuration."""
    depth: ReviewDepth = ReviewDepth.STANDARD
    focus: ReviewFocus = ReviewFocus.ALL
    output_format: OutputFormat = OutputFormat.TERMINAL
    interactive: bool = False
    save_history: bool = False
    private: bool = False


class AnalyzeConfig(BaseModel):
    """Analyze command configuration."""
    tools: List[str] = Field(default_factory=lambda: ["auto"])
    output_format: OutputFormat = OutputFormat.TERMINAL
    include_metrics: bool = True


class DocumentConfig(BaseModel):
    """Document command configuration."""
    style: str = "standard"
    output_format: OutputFormat = OutputFormat.MARKDOWN
    include_examples: bool = True


class ExplainConfig(BaseModel):
    """Explain command configuration."""
    depth: ReviewDepth = ReviewDepth.STANDARD
    output_format: OutputFormat = OutputFormat.TERMINAL
    include_context: bool = True


class VaahaiConfig(BaseModel):
    """Main configuration model."""
    
    # Schema version for backward compatibility
    schema_version: int = CURRENT_SCHEMA_VERSION
    
    llm: LLMConfig = Field(default_factory=LLMConfig)
    autogen: AutogenConfig = Field(default_factory=AutogenConfig)
    review: ReviewConfig = Field(default_factory=ReviewConfig)
    analyze: AnalyzeConfig = Field(default_factory=AnalyzeConfig)
    document: DocumentConfig = Field(default_factory=DocumentConfig)
    explain: ExplainConfig = Field(default_factory=ExplainConfig)
    log_level: str = "info"
    cache_dir: Optional[Path] = None
    custom: Dict[str, Any] = Field(default_factory=dict)
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Override model_dump to include schema_version."""
        data = super().model_dump(**kwargs)
        data["schema_version"] = CURRENT_SCHEMA_VERSION
        return data
