from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from au_iomanager.base import BaseIO
from loguru import logger


class UnityCatalogManager(BaseIO):
    """
    Manages operations specific to Unity Catalog in Databricks environments.

    This class handles data writing operations to Unity Catalog, ensuring best practices
    are followed for table creation, optimization, and maintenance.
    """

    def __init__(self, context: Dict[str, Any]):
        """
        Initialize the Unity Catalog Manager.

        Args:
            context: Application context containing Spark session and configuration
        """
        self.context = context
        self._unity_catalog_enabled = self._check_unity_catalog_support()

    def _check_unity_catalog_support(self) -> bool:
        """
        Verify if Unity Catalog is enabled in the Spark context.

        Returns:
            bool: True if Unity Catalog is enabled, False otherwise
        """
        return (
            self._spark_available()
            and self.context.spark.conf.get(
                "spark.databricks.unityCatalog.enabled", "false"
            ).lower()
            == "true"
        )

    def write_to_unity_catalog(
        self,
        df: Any,
        config: Dict[str, Any],
        start_date: Optional[str],
        end_date: Optional[str],
        out_key: str,
    ) -> None:
        """
        Write data to Unity Catalog following best practices.

        Args:
            df: DataFrame to write
            config: Configuration parameters for the write operation
            start_date: Start date for partitioned data
            end_date: End date for partitioned data
            out_key: Output key identifier

        Raises:
            ValueError: If configuration is invalid
            Exception: For any other write operation errors
        """
        if not df or df.isEmpty():
            logger.warning("Empty DataFrame. No data will be written to Unity Catalog.")
            return

        parsed = self._parse_output_key(out_key)
        self._validate_uc_config(config)

        catalog = config["catalog_name"]
        schema = config.get("schema", parsed["schema"])
        sub_folder = config.get("sub_folder", parsed["sub_folder"])
        table_name = config.get("table_name", parsed["table_name"])
        full_table_name = f"{catalog}.{schema}.{table_name}"
        storage_location = f"{self.context.output_path}/{out_key}"

        try:
            self._ensure_schema_exists(catalog, schema, config.get("output_path"))
            writer, options = self._configure_writer(df, config, start_date, end_date)

            self._execute_write_operation(
                writer,
                table_name,
                full_table_name,
                options,
                storage_location,
                sub_folder,
            )
            self._post_write_operations(config, full_table_name, start_date, end_date)
        except Exception as e:
            logger.error(f"Error writing to Unity Catalog {full_table_name}: {str(e)}")
            raise

    def _validate_uc_config(self, config: Dict[str, Any]) -> None:
        """
        Validate required configuration for Unity Catalog.

        Args:
            config: Configuration parameters

        Raises:
            ValueError: If required parameters are missing
        """
        self._validate_config(
            config, ["table_name", "schema", "catalog_name"], "Unity Catalog"
        )

    def _configure_writer(
        self,
        df: Any,
        config: Dict[str, Any],
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Configure DataFrame writer with appropriate write options.

        Args:
            df: DataFrame to write
            config: Configuration parameters
            start_date: Start date for partitioned data
            end_date: End date for partitioned data

        Returns:
            Tuple containing the configured writer and options dictionary
        """
        write_mode = config.get("write_mode", "overwrite")
        if write_mode not in ["overwrite", "append", "ignore", "error"]:
            logger.warning(
                f"Write mode '{write_mode}' not recognized. Using 'overwrite'."
            )
            write_mode = "overwrite"

        writer = df.write.format("delta").mode(write_mode)
        options = {"overwriteSchema": "true"}

        if partition_col := config.get("partition_col"):
            if partition_col not in ("catalog", ""):
                writer = writer.partitionBy(partition_col)
                self._apply_overwrite_strategy(
                    config, options, partition_col, start_date, end_date
                )

        return writer, options

    def _apply_overwrite_strategy(
        self,
        config: Dict[str, Any],
        options: Dict[str, str],
        partition_col: str,
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> None:
        """
        Apply overwrite strategy if configured.

        Args:
            config: Configuration parameters
            options: Write options dictionary to be updated
            partition_col: Column used for partitioning
            start_date: Start date for partitioned data
            end_date: End date for partitioned data

        Raises:
            ValueError: If dates are missing or format is invalid
        """
        if config.get("overwrite_strategy") == "replaceWhere":
            if not start_date or not end_date:
                raise ValueError(
                    "start_date and end_date are required for replaceWhere"
                )
            if not (
                self._validate_date_format(start_date)
                and self._validate_date_format(end_date)
            ):
                raise ValueError(f"Invalid date format: {start_date} - {end_date}")

            options["replaceWhere"] = (
                f"{partition_col} BETWEEN '{start_date}' AND '{end_date}'"
            )
            options["overwriteSchema"] = "false"

    def _validate_date_format(self, date_str: str) -> bool:
        """
        Validate the format of a date string (YYYY-MM-DD).

        Args:
            date_str: Date string to validate

        Returns:
            bool: True if format is valid, False otherwise
        """
        try:
            year, month, day = date_str.split("-")
            return (
                len(year) == 4
                and year.isdigit()
                and len(month) == 2
                and month.isdigit()
                and int(month) <= 12
                and len(day) == 2
                and day.isdigit()
                and int(day) <= 31
            )
        except Exception:
            return False

    def _execute_write_operation(
        self,
        writer: Any,
        table_name: str,
        full_table_name: str,
        options: Dict[str, str],
        storage_location: str,
        sub_folder: str,
    ) -> None:
        """
        Execute the data write operation to the table.

        Args:
            writer: Configured DataFrame writer
            table_name: Table name
            full_table_name: Fully qualified table name (catalog.schema.table)
            options: Write options
            storage_location: Base storage location
            sub_folder: Sub-folder within the storage location

        Raises:
            ValueError: If configuration is incomplete
        """
        if not storage_location or not table_name:
            raise ValueError("Incomplete configuration to determine path")

        path = f"{storage_location}/{sub_folder}/{table_name}"
        writer.options(**options).save(path)
        logger.info(f"Data saved to: {path}")

        self.context.spark.sql(
            f"""
            CREATE TABLE IF NOT EXISTS {full_table_name}
            USING DELTA
            LOCATION '{path}'
        """
        )
        logger.success(f"Table {full_table_name} registered in Unity Catalog")

    def _post_write_operations(
        self,
        config: Dict[str, Any],
        full_table_name: str,
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> None:
        """
        Execute operations after writing data.

        Args:
            config: Configuration parameters
            full_table_name: Fully qualified table name
            start_date: Start date for partitioned data
            end_date: End date for partitioned data
        """
        try:
            if partition_col := config.get("partition_col"):
                if start_date and end_date:
                    self._optimize_table(
                        full_table_name, partition_col, start_date, end_date
                    )

                self._add_table_comment(
                    full_table_name, config.get("description"), partition_col
                )

            if config.get("vacuum", True):
                self._execute_vacuum(
                    full_table_name, config.get("vacuum_retention_hours")
                )
        except Exception as e:
            logger.warning(f"Error in post-write operations: {str(e)}")

    def _optimize_table(
        self, full_table_name: str, partition_col: str, start_date: str, end_date: str
    ) -> None:
        """
        Optimize the table for the specified date range.

        Args:
            full_table_name: Fully qualified table name
            partition_col: Column used for partitioning
            start_date: Start date for optimization
            end_date: End date for optimization
        """
        if not self._spark_available():
            logger.warning("Spark not available for table optimization")
            return

        logger.info(f"Optimizing table {full_table_name}")
        try:
            self.context.spark.sql(
                f"""
                OPTIMIZE {full_table_name}
                WHERE {partition_col} BETWEEN '{start_date}' AND '{end_date}'
            """
            )
            logger.info(f"Table {full_table_name} optimized successfully")
        except Exception as e:
            logger.error(f"Error optimizing table: {str(e)}")

    def _add_table_comment(
        self,
        full_table_name: str,
        description: Optional[str],
        partition_col: Optional[str],
    ) -> None:
        """
        Add descriptive comment to the table.

        Args:
            full_table_name: Fully qualified table name
            description: Table description
            partition_col: Column used for partitioning
        """
        if not self._spark_available():
            return

        safe_description = (description or "Data table").replace("'", "''")
        comment = f"{safe_description}. Partition: {partition_col or 'N/A'}"

        try:
            self.context.spark.sql(f"COMMENT ON TABLE {full_table_name} IS '{comment}'")
            logger.info(f"Comment added to table {full_table_name}")
        except Exception as e:
            logger.error(f"Error adding comment: {str(e)}")

    def _execute_vacuum(
        self, full_table_name: str, retention_hours: Optional[int] = None
    ) -> None:
        """
        Execute VACUUM to clean up old versions.

        Args:
            full_table_name: Fully qualified table name
            retention_hours: Retention hours for old versions (minimum 168 hours/7 days)
        """
        if not self._spark_available():
            return

        hours = max(168, retention_hours or 168)  # Minimum 7 days (168 hours)
        logger.info(f"Executing VACUUM on {full_table_name}")

        try:
            self.context.spark.sql(f"VACUUM {full_table_name} RETAIN {hours} HOURS")
            logger.info(f"VACUUM completed on {full_table_name}")
        except Exception as e:
            logger.error(f"Error executing VACUUM: {str(e)}")

    def _ensure_schema_exists(
        self, catalog: str, schema: str, managed_location: Optional[str] = None
    ) -> None:
        """
        Ensure schema exists in Unity Catalog.

        Args:
            catalog: Catalog name
            schema: Schema name
            managed_location: Managed location for the schema

        Raises:
            ValueError: If catalog or schema are empty
        """
        if not self._unity_catalog_enabled:
            logger.warning("Unity Catalog is not enabled. Cannot create schema.")
            return

        if not catalog or not schema:
            raise ValueError("Catalog and schema cannot be empty")

        create_sql = f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}"
        if managed_location:
            create_sql += f" MANAGED LOCATION '{managed_location}'"

        try:
            logger.info(f"Verifying schema: {catalog}.{schema}")
            self.context.spark.sql(create_sql)
            logger.info(f"Schema {catalog}.{schema} created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating schema {catalog}.{schema}: {str(e)}")
            raise


class DataWriter(BaseIO):
    """
    Manages data writing operations in different formats.

    This class provides methods to write data to traditional storage systems
    in various formats like delta, parquet, csv, etc.
    """

    SUPPORTED_FORMATS = ["delta", "parquet", "csv", "json", "orc"]

    def write_data(self, df: Any, path: str, config: Dict[str, Any]) -> None:
        """
        Write data to traditional storage systems.

        Args:
            df: DataFrame to write
            path: Target path for the data
            config: Configuration parameters

        Raises:
            ValueError: If path is empty or configuration is invalid
        """
        if not path:
            raise ValueError("Output path cannot be empty")

        self._validate_write_config(config)
        self._prepare_local_directory(path)

        try:
            writer = self._configure_basic_writer(df, config)
            logger.info(f"Saving data to: {path}")
            writer.save(str(path))
            logger.success(f"Data saved successfully to: {path}")
        except Exception as e:
            logger.error(f"Error saving to {path}: {str(e)}")
            raise

    def _validate_write_config(self, config: Dict[str, Any]) -> None:
        """
        Validate basic write configuration.

        Args:
            config: Configuration parameters

        Raises:
            ValueError: If required parameters are missing or format is not supported
        """
        self._validate_config(config, ["format"], "write operation")

        if config.get("format") not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {config.get('format')}. Supported formats: {self.SUPPORTED_FORMATS}"
            )

    def _configure_basic_writer(self, df: Any, config: Dict[str, Any]) -> Any:
        """
        Configure writer for non-UC formats.

        Args:
            df: DataFrame to write
            config: Configuration parameters

        Returns:
            Configured DataFrame writer

        Raises:
            ValueError: If DataFrame is None or partition columns are not found
        """
        if not df:
            raise ValueError("DataFrame cannot be None")

        format_type = config["format"]
        writer = df.write.format(format_type).mode(
            config.get("write_mode", "overwrite")
        )

        if partition_columns := config.get("partition"):
            missing_cols = [col for col in partition_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Partition columns not found: {missing_cols}")
            writer = writer.partitionBy(
                *(
                    [partition_columns]
                    if isinstance(partition_columns, str)
                    else partition_columns
                )
            )

        # Format-specific options
        if format_type == "delta":
            writer = writer.option("overwriteSchema", "true")
        elif format_type == "csv":
            writer = (
                writer.option("header", "true")
                .option("quote", '"')
                .option("escape", '"')
            )

        # Additional options from configuration
        if extra_options := config.get("options", {}):
            for key, value in extra_options.items():
                writer = writer.option(key, value)

        return writer


class ModelArtifactManager(BaseIO):
    """
    Manages the writing of ML model artifacts.

    This class provides methods to save model artifacts to the model registry.
    """

    def save_model_artifacts(self, node: Dict[str, Any], model_version: str) -> None:
        """
        Save model artifacts to the model registry.

        Args:
            node: Node configuration containing model artifacts
            model_version: Model version identifier

        Raises:
            ValueError: If node is invalid or model version is empty
        """
        if not node or not isinstance(node, dict):
            raise ValueError("Node must be a valid dictionary")
        if not model_version:
            raise ValueError("Model version cannot be empty")

        model_registry_path = self.context.global_settings.get("model_registry_path")
        if not model_registry_path:
            logger.warning("Model registry path not configured")
            return

        for artifact in node.get("model_artifacts", []):
            if not artifact or not isinstance(artifact, dict):
                logger.warning("Invalid artifact found, skipping")
                continue

            try:
                artifact_path = self._build_artifact_path(
                    model_registry_path, artifact, model_version
                )
                self._create_artifact_directory(artifact_path)
                logger.info(
                    f"Artifact '{artifact.get('name', 'unnamed')}' saved to: {artifact_path}"
                )
            except Exception as e:
                logger.error(
                    f"Error saving artifact {artifact.get('name', 'unknown')}: {str(e)}"
                )

    def _build_artifact_path(
        self, base_path: str, artifact: Dict[str, Any], version: str
    ) -> Path:
        """
        Build the complete path for the artifact.

        Args:
            base_path: Base path for the model registry
            artifact: Artifact configuration
            version: Model version

        Returns:
            Path object for the artifact

        Raises:
            ValueError: If base path is empty or artifact has no name
        """
        if not base_path:
            raise ValueError("Model registry base path cannot be empty")
        if not (artifact_name := artifact.get("name")):
            raise ValueError("Artifact must have a name")

        return Path(base_path) / artifact_name / version


class OutputManager(BaseIO):
    """
    Manages output data writing operations in different formats and destinations.

    This class serves as a facade for all data output operations, delegating to specialized
    managers based on the target destination and format.
    """

    def __init__(self, context: Dict[str, Any]):
        """
        Initialize the Output Manager.

        Args:
            context: Application context containing configuration and sessions
        """
        self.context = context
        self.unity_catalog_manager = UnityCatalogManager(context)
        self.data_writer = DataWriter(context)
        self.model_artifact_manager = ModelArtifactManager(context)

    def save_output(
        self,
        node: Dict[str, Any],
        df: Any,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> None:
        """
        Save output data according to node configuration.

        Args:
            node: Node configuration
            df: DataFrame to write
            start_date: Start date for partitioned data
            end_date: End date for partitioned data

        Raises:
            ValueError: If node is invalid or DataFrame is None
        """
        self._validate_inputs(node, df)

        out_keys = self._get_output_keys(node)
        if not out_keys:
            logger.warning(
                f"Node {node.get('output', 'unknown')} has no output configuration"
            )
            return

        for out_key in out_keys:
            try:
                self._save_single_output(out_key, df, start_date, end_date)
            except Exception as e:
                logger.error(f"Error saving output '{out_key}': {str(e)}")
                if self.context.global_settings.get("fail_on_error", True):
                    raise

    def _validate_inputs(self, node: Dict[str, Any], df: Any) -> None:
        """
        Validate input parameters.

        Args:
            node: Node configuration
            df: DataFrame to write

        Raises:
            ValueError: If node is None or not a dictionary, or if DataFrame is None
        """
        if not node:
            raise ValueError("Parameter 'node' cannot be None")
        if not isinstance(node, dict):
            raise ValueError(
                f"Parameter 'node' must be a dictionary, received: {type(node)}"
            )
        if df is None:
            raise ValueError("Output DataFrame cannot be None")

    def _get_output_keys(self, node: Dict[str, Any]) -> List[str]:
        """
        Get output keys from a node.

        Args:
            node: Node configuration

        Returns:
            List of output keys
        """
        keys = node.get("output", [])
        return (
            [keys]
            if isinstance(keys, str)
            else (keys if isinstance(keys, list) else [])
        )

    def _save_single_output(
        self,
        out_key: str,
        df: Any,
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> None:
        """
        Save a single output.

        Args:
            out_key: Output key
            df: DataFrame to write
            start_date: Start date for partitioned data
            end_date: End date for partitioned data

        Raises:
            ValueError: If output key is empty or configuration is not found
        """
        if not out_key:
            raise ValueError("Output key cannot be empty")

        dataset_config = self.context.output_config.get(out_key)
        if not dataset_config:
            raise ValueError(f"Output configuration '{out_key}' not found")

        try:
            if self._should_use_unity_catalog(dataset_config):
                self.unity_catalog_manager.write_to_unity_catalog(
                    df, dataset_config, start_date, end_date, out_key
                )
            else:
                base_path = self._resolve_output_path(dataset_config, out_key)
                self.data_writer.write_data(df, base_path, dataset_config)
        except Exception as e:
            logger.error(f"Error saving output '{out_key}': {str(e)}")
            raise

    def _should_use_unity_catalog(self, dataset_config: Dict[str, Any]) -> bool:
        """
        Determine if Unity Catalog should be used for writing.

        Args:
            dataset_config: Dataset configuration

        Returns:
            bool: True if Unity Catalog should be used, False otherwise
        """
        return (
            dataset_config
            and dataset_config.get("format") == "unity_catalog"
            and self.unity_catalog_manager._unity_catalog_enabled
        )

    def _resolve_output_path(
        self, dataset_config: Dict[str, Any], out_key: str
    ) -> Union[Path, str]:
        """
        Build paths compatible with multi-environment (Azure, AWS, GCP, local).

        Args:
            dataset_config: Dataset configuration
            out_key: Output key

        Returns:
            Path object or string representing the output path

        Raises:
            ValueError: If configuration is invalid or output path is not configured
        """
        # Validations
        if not isinstance(dataset_config, dict):
            raise ValueError("dataset_config must be a dictionary")
        if not out_key or not isinstance(out_key, str):
            raise ValueError("out_key must be a non-empty string")

        # Extract components
        try:
            components = {
                "table_name": str(
                    dataset_config.get(
                        "table_name", self._parse_output_key(out_key)["table_name"]
                    )
                ).strip(),
                "schema": str(
                    dataset_config.get(
                        "schema", self._parse_output_key(out_key)["schema"]
                    )
                ).strip(),
                "sub_folder": str(
                    dataset_config.get(
                        "sub_folder", self._parse_output_key(out_key)["sub_folder"]
                    )
                ).strip(),
            }

            if not all(components.values()):
                raise ValueError("Path components cannot be empty")
        except (KeyError, AttributeError) as e:
            raise ValueError(f"Error parsing out_key: {str(e)}")

        # Verify context has output_path
        if not hasattr(self.context, "output_path") or not self.context.output_path:
            raise ValueError("Context does not have output_path configured")

        base_path = self.context.output_path
        path_parts = [
            components["schema"],
            components["sub_folder"],
            components["table_name"],
        ]

        # Path type detection
        if isinstance(base_path, Path) or (
            isinstance(base_path, str) and not re.match(r"^[a-z0-9]+://", base_path)
        ):
            # Handle local or DBFS paths (Path or str without scheme)
            try:
                base = Path(base_path)
                # Special handling for DBFS in Databricks
                if str(base).startswith(("/dbfs", "dbfs:")):
                    return Path("/dbfs") / "/".join(path_parts).lstrip("/")
                return base.joinpath(*path_parts)
            except Exception as e:
                raise ValueError(f"Error building local path: {str(e)}")
        else:
            # Handle cloud storage and URLs
            base_str = str(base_path).rstrip("/")
            full_path = "/".join([p for p in path_parts if p])

            # Prevent double slashes
            separator = "" if base_str.endswith("/") else "/"
            return f"{base_str}{separator}{full_path}"

    def save_ml_output(
        self,
        node: Dict[str, Any],
        df: Any,
        model_version: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> None:
        """
        Save ML model data and artifacts.

        Args:
            node: Node configuration
            df: DataFrame to write
            model_version: Model version identifier
            start_date: Start date for partitioned data
            end_date: End date for partitioned data

        Raises:
            ValueError: If model version is empty
        """
        if not model_version:
            raise ValueError("Model version cannot be empty")

        try:
            self.save_output(node, df, start_date, end_date)
            self.model_artifact_manager.save_model_artifacts(node, model_version)
        except Exception as e:
            logger.error(f"Error in save_ml_output: {str(e)}")
            raise
