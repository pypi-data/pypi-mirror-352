import os
from typing import Any, Dict, List
from loguru import logger


class BaseIO:
    """Base class for input/output operations.

    This class provides foundational functionality for I/O operations across different storage systems.
    It handles configuration validation, directory preparation, and context management.

    Attributes:
        context (Dict[str, Any]): Application context containing runtime configuration and resources.
    """

    def __init__(self, context: Dict[str, Any]):
        """Initialize BaseIO with an application context.

        Args:
            context (Dict[str, Any]): Application context containing runtime configuration and resources.
        """
        self.context = context
        logger.debug("BaseIO initialized with context")

    def _validate_config(
        self, config: Dict[str, Any], required_fields: List[str], config_type: str
    ) -> None:
        """Validate a configuration against required fields.

        Args:
            config (Dict[str, Any]): Configuration dictionary to validate.
            required_fields (List[str]): List of field names that must be present and non-empty.
            config_type (str): Type of configuration being validated, used in error messages.

        Raises:
            ValueError: If the configuration is None or missing required fields.
        """
        if not config:
            logger.error(
                f"Configuration validation failed: {config_type} configuration is None"
            )
            raise ValueError(f"{config_type} configuration cannot be None")

        missing_fields = [field for field in required_fields if not config.get(field)]
        if missing_fields:
            error_msg = f"Required fields not specified for {config_type}: {', '.join(missing_fields)}"
            logger.error(f"Configuration validation failed: {error_msg}")
            raise ValueError(error_msg)

        logger.debug(f"Configuration for {config_type} successfully validated")

    def _prepare_local_directory(self, path: str) -> None:
        """Create local directories if necessary.

        In local execution mode, ensures that the parent directory for the given path exists.

        Args:
            path (str): File path for which to prepare the directory structure.

        Raises:
            IOError: If directory creation fails.
        """
        if getattr(self.context, "execution_mode", None) == "local":
            try:
                dir_path = os.path.dirname(path)
                if not os.path.isdir(
                    dir_path
                ):  # Avoid creating directories if they already exist
                    logger.debug(f"Creating directory: {dir_path}")
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"Directory created: {dir_path}")
            except OSError as e:  # Capture specific error
                logger.exception(f"Error creating local directory: {dir_path}")
                raise IOError(f"Failed to create directory {dir_path}") from e

    def _spark_available(self) -> bool:
        """Check if Spark context is available.

        Returns:
            bool: True if a valid Spark context exists in the application context, False otherwise.
        """
        is_available = hasattr(self.context, "spark") and self.context.spark is not None
        logger.debug(f"Spark availability: {is_available}")
        return is_available

    def _parse_output_key(self, out_key: str) -> Dict[str, str]:
        """Parse an output key into its components.

        Parses a dot-separated string into schema, sub_folder, and table_name components.

        Args:
            out_key (str): Output key in format 'schema.sub_folder.table_name'.

        Returns:
            Dict[str, str]: Dictionary containing the parsed components.

        Raises:
            ValueError: If the output key format is invalid.
        """
        parts = out_key.split(".")
        if len(parts) != 3:
            error_msg = (
                f"Invalid format: {out_key}. Must be 'schema.sub_folder.table_name'"
            )
            logger.error(f"Output key parsing failed: {error_msg}")
            raise ValueError(error_msg)

        result = {"schema": parts[0], "sub_folder": parts[1], "table_name": parts[2]}
        logger.debug(f"Output key parsed: {out_key} -> {result}")
        return result
