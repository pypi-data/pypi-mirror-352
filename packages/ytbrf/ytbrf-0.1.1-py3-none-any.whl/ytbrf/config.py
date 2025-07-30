import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from dataclasses import dataclass
from rich.console import Console
import argparse

console = Console()

@dataclass
class SummaryConfig:
    type: str
    model: str
    server_url: str
    api_key: str
    ratio: float
    target_language: str

@dataclass
class TranscriptionConfig:
    method: str
    model: str
    models_dir: str
    force_language: str
    delete_intermediate_files: bool

@dataclass
class OutputConfig:
    directory: str
    filename_pattern: str

@dataclass
class YouTubeConfig:
    api_key: str
    audio_quality: str
    audio_format: str

@dataclass
class Config:
    summary: SummaryConfig
    transcription: TranscriptionConfig
    output: OutputConfig
    youtube: YouTubeConfig

class ConfigManager:
    DEFAULT_CONFIG_PATH = "config.yaml"
    USER_CONFIG_PATH = os.path.expanduser("~/.config/ytbrf/config.yaml")
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config()
        print(f"Config path: {self.config_path}")
        self.config = self._load_config()

    def _find_config(self) -> str:
        """
        User's config directory
        """
        return self.USER_CONFIG_PATH
    
    def _load_config(self) -> Config:
        """Load and validate configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
        except FileNotFoundError:
            console.print(f"[yellow]Configuration file not found at {self.config_path}. Using defaults.[/yellow]")
            config_data = {}
        except yaml.YAMLError as e:
            console.print(f"[red]Error parsing configuration file: {e}[/red]")
            raise
        
        # Load default configuration
        default_config = self._get_default_config()
        
        # Merge user configuration with defaults
        merged_config = self._deep_merge(default_config, config_data)
        
        # Validate and convert to Config object
        return self._validate_config(merged_config)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values from config.yaml.example."""
        # Path to the example config file
        example_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml.example")
        
        try:
            with open(example_config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                
            # Handle user-dependent paths
            if "transcription" in config_data and "models_dir" not in config_data["transcription"]:
                # Add default models_dir relative to user's home directory
                config_data["transcription"]["models_dir"] = os.path.expanduser("~/whisper.cpp/models")
                
            # Add any missing fields that might not be in the example config
            if "transcription" in config_data and "delete_intermediate_files" not in config_data["transcription"]:
                config_data["transcription"]["delete_intermediate_files"] = False
                
            if "transcription" in config_data and "method" not in config_data["transcription"]:
                # Convert mode to method if it exists
                if "mode" in config_data["transcription"]:
                    config_data["transcription"]["method"] = config_data["transcription"].pop("mode")
                else:
                    config_data["transcription"]["method"] = "whisper-cpp"
                    
            return config_data
        except (FileNotFoundError, yaml.YAMLError) as e:
            console.print(f"[yellow]Error loading example config: {e}. Using hardcoded defaults.[/yellow]")
            
            # Fallback to hardcoded defaults if example config can't be loaded
            return {
                "summary": {
                    "type": "openai",
                    "model": "gemma-2-9b-it",
                    "server_url": "http://localhost:1234/v1",
                    "api_key": "lm-studio",
                    "ratio": 0.2,
                    "target_language": "zh-cn"
                },
                "transcription": {
                    "method": "whisper-cpp",
                    "models_dir": os.path.expanduser("~/whisper.cpp/models"),
                    "model": "small",
                    "force_language": "auto",
                    "delete_intermediate_files": False
                },
                "output": {
                    "directory": ".",
                    "filename_pattern": "{title}-{lang}.txt"
                },
                "youtube": {
                    "api_key": "",
                    "audio_quality": "best",
                    "audio_format": "mp3"
                }
            }
    
    def _deep_merge(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, with user values taking precedence."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _validate_config(self, config: Dict[str, Any]) -> Config:
        """Validate configuration values and convert to Config object."""
        # Validate summary ratio
        if not 0 < config["summary"]["ratio"] <= 1:
            raise ValueError("Summary ratio must be between 0 and 1")
        # Validate whisper model
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if config["transcription"]["model"] not in valid_models:
            raise ValueError(f"Invalid whisper model. Must be one of: {', '.join(valid_models)}")
        # Validate audio format
        valid_formats = ["mp3", "m4a", "wav"]
        if config["youtube"]["audio_format"] not in valid_formats:
            raise ValueError(f"Invalid audio format. Must be one of: {', '.join(valid_formats)}")
        # Convert to Config object
        return Config(
            summary=SummaryConfig(**config["summary"]),
            transcription=TranscriptionConfig(**config["transcription"]),
            output=OutputConfig(**config["output"]),
            youtube=YouTubeConfig(**config["youtube"])
        )
    
    def get_config(self) -> Config:
        """Get the current configuration."""
        return self.config
    
    def save_config(self, config: Config) -> None:
        """Save configuration to file."""
        config_dir = os.path.dirname(self.config_path)
        os.makedirs(config_dir, exist_ok=True)
        config_dict = {
            "summary": {
                "type": config.summary.type,
                "model": config.summary.model,
                "server_url": config.summary.server_url,
                "api_key": config.summary.api_key,
                "ratio": config.summary.ratio,
                "target_language": config.summary.target_language
            },
            "transcription": {
                "method": config.transcription.method,
                "models_dir": config.transcription.models_dir,
                "model": config.transcription.model,
                "force_language": config.transcription.force_language,
                "delete_intermediate_files": config.transcription.delete_intermediate_files
            },
            "output": {
                "directory": config.output.directory,
                "filename_pattern": config.output.filename_pattern
            },
            "youtube": {
                "api_key": config.youtube.api_key,
                "audio_quality": config.youtube.audio_quality,
                "audio_format": config.youtube.audio_format
            }
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
