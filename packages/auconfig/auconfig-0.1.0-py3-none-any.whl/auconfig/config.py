import importlib
import json
from pathlib import Path
import sys
import yaml
from functools import lru_cache
from typing import Dict, Any, List, Optional, Union

from loguru import logger
from auconfig.session import SparkSessionFactory


class ConfigLoader:
    """Responsible for loading configuration from multiple sources."""

    @staticmethod
    def load_config(source: Union[str, Dict]) -> Dict[str, Any]:
        """
        Load configuration from various sources:
        - YAML file (.yaml, .yml)
        - JSON file (.json)
        - Python module (.py) that defines a 'config' variable
        - Direct dictionary input
        """
        if isinstance(source, dict):
            return source

        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Config source not found: {source}")

        suffix = path.suffix.lower()

        if suffix in (".yaml", ".yml"):
            return ConfigLoader._load_yaml_file(path)
        elif suffix == ".json":
            return ConfigLoader._load_json_file(path)
        elif suffix == ".py":
            return ConfigLoader._load_python_module(path)
        else:
            raise ValueError(f"Unsupported config format: {suffix}")

    @staticmethod
    def _load_yaml_file(file_path: Path) -> Dict[str, Any]:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {str(e)}") from e

    @staticmethod
    def _load_json_file(file_path: Path) -> Dict[str, Any]:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                return json.load(file) or {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {str(e)}") from e

    @staticmethod
    def _load_python_module(file_path: Path) -> Dict[str, Any]:
        """Load a Python file as a module and extract its 'config' variable."""
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec:
            raise ImportError(f"Could not load Python module: {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise ImportError(f"Error executing module {file_path}: {str(e)}") from e

        if not hasattr(module, "config"):
            raise AttributeError(
                f"Python module {file_path} must define 'config' variable"
            )

        return module.config

    @staticmethod
    def interpolate_variables(string: str, variables: Dict[str, Any]) -> str:
        """Replaces variables in a string with their corresponding values.

        Args:
            string: String containing variables in ${var} format
            variables: Dictionary of variable names and their values

        Returns:
            String with all variables replaced by their values
        """
        if not string or not variables:
            return string

        result = string
        for key, value in variables.items():
            placeholder = f"${{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result


class Context:
    """Context for managing configuration-based pipelines."""

    REQUIRED_GLOBAL_SETTINGS = ["input_path", "output_path", "mode"]

    def __init__(
        self,
        global_settings: Union[str, Dict],
        pipelines_config: Union[str, Dict],
        nodes_config: Union[str, Dict],
        input_config: Union[str, Dict],
        output_config: Union[str, Dict],
    ):
        """Initialize the context with configuration sources.

        Args:
            global_settings: Path to global settings file or dictionary
            pipelines_config: Path to pipelines configuration file or dictionary
            nodes_config: Path to nodes configuration file or dictionary
            input_config: Path to input configuration file or dictionary
            output_config: Path to output configuration file or dictionary

        Raises:
            ValueError: If configurations are invalid
        """
        self.config_loader = ConfigLoader()

        # Load and validate configurations
        self._load_configurations(
            global_settings,
            pipelines_config,
            nodes_config,
            input_config,
            output_config,
        )

        # Initialize Spark with the execution mode
        self.spark = SparkSessionFactory.create_session(self.execution_mode)

        # Process configurations
        self._process_configurations()

    def _load_configurations(
        self,
        global_settings: Union[str, Dict],
        pipelines_config: Union[str, Dict],
        nodes_config: Union[str, Dict],
        input_config: Union[str, Dict],
        output_config: Union[str, Dict],
    ) -> None:
        """Load all configuration sources and validate global settings.

        Args:
            global_settings: Global settings source (file path or dict)
            pipelines_config: Pipelines configuration source (file path or dict)
            nodes_config: Nodes configuration source (file path or dict)
            input_config: Input configuration source (file path or dict)
            output_config: Output configuration source (file path or dict)

        Raises:
            ValueError: If global settings are invalid
        """
        # Load global settings first
        self.global_settings = self._load_config(global_settings, "global settings")
        self._validate_global_settings()
        self.execution_mode = self.global_settings.get("mode", "databricks")

        # Load other configurations
        self.pipelines_config = self._load_config(pipelines_config, "pipelines config")
        self.nodes_config = self._load_config(nodes_config, "nodes config")
        self.input_config = self._load_config(input_config, "input config")
        self.output_config = self._load_config(output_config, "output config")

    def _process_configurations(self) -> None:
        """Process and prepare configurations after loading."""
        # Initialize main properties
        self.layer = self.global_settings.get("layer", "").lower()
        self.input_path = self.global_settings.get("input_path", "")
        self.output_path = self.global_settings.get("output_path", "")

        # Process input paths
        self._interpolate_input_paths()

    def _load_config(
        self, source: Union[str, Dict], config_name: str
    ) -> Dict[str, Any]:
        """Load configuration from source with validation.

        Args:
            source: Configuration source (file path or dictionary)
            config_name: Name of the configuration for error messages

        Returns:
            Loaded configuration dictionary

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            config = self.config_loader.load_config(source)
            if not isinstance(config, dict):
                raise ValueError(f"{config_name} must be a dictionary")
            return config
        except Exception as e:
            logger.error(f"Error loading {config_name}: {str(e)}")
            raise

    def _validate_global_settings(self) -> None:
        """Validate that required global settings are present.

        Raises:
            ValueError: If any required setting is missing
        """
        missing_settings = [
            s for s in self.REQUIRED_GLOBAL_SETTINGS if s not in self.global_settings
        ]

        if missing_settings:
            raise ValueError(
                f"Missing required global settings: {', '.join(missing_settings)}"
            )

    def _interpolate_input_paths(self) -> None:
        """Interpolate variables in input data paths."""
        for config in self.input_config.values():
            if "filepath" in config:
                config["filepath"] = self.config_loader.interpolate_variables(
                    config["filepath"], {"input_path": self.input_path}
                )

    @property
    @lru_cache(maxsize=1)
    def pipelines(self) -> Dict[str, Dict[str, Any]]:
        """Return all loaded and validated pipeline configurations.

        Returns:
            Dictionary of pipeline configurations

        Raises:
            ValueError: If there are validation errors
        """
        return self._load_pipelines()

    def _load_pipelines(self) -> Dict[str, Dict[str, Any]]:
        """Load and validate pipelines from configuration.

        Returns:
            Dictionary of processed pipeline configurations

        Raises:
            ValueError: If referenced nodes are missing
        """
        pipelines = self.pipelines_config
        missing_nodes = self._validate_pipeline_nodes(pipelines)
        if missing_nodes:
            raise ValueError(f"Missing nodes: {', '.join(missing_nodes)}")

        return {
            name: self._generate_pipeline_config(name, contents)
            for name, contents in pipelines.items()
        }

    def _validate_pipeline_nodes(self, pipelines: Dict[str, Any]) -> List[str]:
        """Validate that all referenced nodes exist in the configuration.

        Args:
            pipelines: Dictionary of pipeline configurations

        Returns:
            List of missing node names
        """
        missing = []
        for pipeline in pipelines.values():
            for node in pipeline.get("nodes", []):
                if node not in self.nodes_config:
                    missing.append(node)
        return list(set(missing))  # Remove duplicates

    def _generate_pipeline_config(
        self, name: str, contents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate complete configuration for a specific pipeline.

        Args:
            name: Name of the pipeline
            contents: Raw pipeline configuration

        Returns:
            Processed pipeline configuration
        """
        return {
            "nodes": [
                {"name": node_name, **self.nodes_config[node_name]}
                for node_name in contents.get("nodes", [])
            ],
            "inputs": contents.get("inputs", []),
            "outputs": contents.get("outputs", []),
        }

    def get_pipeline(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific pipeline configuration by name.

        Args:
            name: Name of the pipeline

        Returns:
            Pipeline configuration or None if not found
        """
        return self.pipelines.get(name)

    @classmethod
    def from_json_config(
        cls,
        global_settings: Dict[str, Any],
        pipelines_config: Dict[str, Any],
        nodes_config: Dict[str, Any],
        input_config: Dict[str, Any],
        output_config: Dict[str, Any],
    ) -> "Context":
        """Create Context instance directly from JSON/dictionary configurations.

        Args:
            global_settings: Global settings dictionary
            pipelines_config: Pipelines configuration dictionary
            nodes_config: Nodes configuration dictionary
            input_config: Input configuration dictionary
            output_config: Output configuration dictionary

        Returns:
            Context instance
        """
        return cls(
            global_settings=global_settings,
            pipelines_config=pipelines_config,
            nodes_config=nodes_config,
            input_config=input_config,
            output_config=output_config,
        )

    @classmethod
    def from_python_dsl(cls, python_module_path: str) -> "Context":
        """Create Context instance from a Python DSL module.

        The Python module should define the following variables:
        - global_settings: Dict[str, Any]
        - pipelines_config: Dict[str, Any]
        - nodes_config: Dict[str, Any]
        - input_config: Dict[str, Any]
        - output_config: Dict[str, Any]

        Args:
            python_module_path: Path to the Python DSL module

        Returns:
            Context instance

        Raises:
            AttributeError: If required variables are missing from the module
            ImportError: If the module cannot be loaded
        """
        # Load the Python module
        path = Path(python_module_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Python DSL module not found: {python_module_path}"
            )

        module_name = path.stem
        spec = importlib.util.spec_from_file_location(module_name, path)
        if not spec:
            raise ImportError(f"Could not load Python DSL module: {python_module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise ImportError(
                f"Error executing DSL module {python_module_path}: {str(e)}"
            ) from e

        # Extract required configurations
        required_vars = [
            "global_settings",
            "pipelines_config",
            "nodes_config",
            "input_config",
            "output_config",
        ]

        missing_vars = [var for var in required_vars if not hasattr(module, var)]
        if missing_vars:
            raise AttributeError(
                f"Python DSL module {python_module_path} must define: {', '.join(missing_vars)}"
            )

        return cls(
            global_settings=module.global_settings,
            pipelines_config=module.pipelines_config,
            nodes_config=module.nodes_config,
            input_config=module.input_config,
            output_config=module.output_config,
        )
