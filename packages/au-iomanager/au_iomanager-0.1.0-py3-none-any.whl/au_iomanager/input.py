import os
from typing import Any, Dict, List, Optional, Tuple
from types import SimpleNamespace
from au_iomanager.base import BaseIO
from loguru import logger


class InputLoader(BaseIO):
    """
    Responsible for loading input data from multiple formats.

    This class handles the loading of datasets from various file formats and sources,
    supporting both sequential and parallel loading operations.
    """

    # Dictionary mapping file formats to their corresponding reader methods
    FORMAT_READERS = {
        "parquet": "_read_parquet",
        "json": "_read_json",
        "csv": "_read_csv",
        "delta": "_read_delta",
        "pickle": "_read_pickle",
        "avro": "_read_avro",
        "orc": "_read_orc",
        "xml": "_read_xml",
        "query": "_read_query",
    }

    def __init__(self, context: Dict[str, Any]):
        """
        Initialize the InputLoader with a context.

        Args:
            context: A dictionary containing configuration and runtime context
        """
        self.context = context
        self._register_custom_formats()

    def load_inputs(self, node: Dict[str, Any]) -> List[Any]:
        """
        Load all inputs defined for a processing node.

        Args:
            node: Node configuration dictionary containing input definitions

        Returns:
            List of loaded datasets
        """
        input_keys = self._get_input_keys(node)
        if not input_keys:
            logger.warning(f"Node '{node.get('name')}' has no defined inputs")
            return []

        # Choose parallel or sequential loading based on configuration
        if node.get("parallel", False) and self._spark_available():
            return self._load_inputs_parallel(input_keys)
        else:
            return self._load_inputs_sequential(input_keys, node.get("fail_fast", True))

    def _spark_available(self) -> bool:
        """
        Check if Spark is available in the current context.

        Returns:
            True if Spark is available, False otherwise
        """
        return hasattr(self.context, "spark")

    def _load_inputs_parallel(self, input_keys: List[str]) -> List[Any]:
        """
        Load multiple datasets in parallel using Spark.

        Args:
            input_keys: List of input keys to load

        Returns:
            List of loaded datasets
        """
        sc = self.context.spark.sparkContext
        logger.info(f"Loading {len(input_keys)} datasets in parallel")

        # Broadcast configuration to worker nodes
        broadcast_configs = sc.broadcast(
            {
                "input_config": self.context.input_config,
                "execution_mode": self.context.execution_mode,
            }
        )

        # Execute parallel loading tasks
        parallel_results = sc.parallelize(input_keys).map(self._load_task).collect()
        results, errors = self._process_parallel_results(parallel_results)

        if errors:
            logger.warning(f"Errors encountered during parallel loading: {errors}")
        return results

    def _load_task(self, input_key: str) -> Tuple[str, Any, Optional[str]]:
        """
        Task for loading a single dataset in parallel.

        Args:
            input_key: The key identifying the dataset to load

        Returns:
            Tuple containing (input_key, loaded_data, error_message)
        """
        try:
            # Create a simplified context for parallel execution
            ctx = SimpleNamespace(
                **self.context.spark.sparkContext.broadcast(
                    {
                        "input_config": self.context.input_config,
                        "execution_mode": self.context.execution_mode,
                    }
                ).value
            )
            return input_key, InputLoader(ctx)._load_dataset(input_key), None
        except Exception as e:
            return input_key, None, str(e)

    def _process_parallel_results(
        self, results: List[Tuple[str, Any, Optional[str]]]
    ) -> Tuple[List[Any], List[str]]:
        """
        Process the results of parallel loading operations.

        Args:
            results: List of (input_key, data, error) tuples from parallel operations

        Returns:
            Tuple containing (loaded_datasets, error_messages)
        """
        loaded_data = []
        errors = []

        for input_key, data, error in results:
            if error:
                errors.append(f"Error loading '{input_key}': {error}")
                if self.context.get("fail_on_parallel_errors", True):
                    raise RuntimeError(f"Parallel loading errors: {errors}")
            else:
                loaded_data.append(data)

        return loaded_data, errors

    def _load_inputs_sequential(
        self, input_keys: List[str], fail_fast: bool
    ) -> List[Any]:
        """
        Load multiple datasets sequentially.

        Args:
            input_keys: List of input keys to load
            fail_fast: If True, stop on first error; otherwise collect all errors

        Returns:
            List of loaded datasets
        """
        results = []
        errors = []

        logger.info(f"Loading {len(input_keys)} datasets sequentially")
        for key in input_keys:
            try:
                logger.debug(f"Loading dataset: {key}")
                results.append(self._load_dataset(key))
            except Exception as e:
                msg = f"Error loading '{key}': {e}"
                logger.error(msg, exc_info=True)
                if fail_fast:
                    raise
                errors.append(msg)

        if errors:
            logger.warning(f"Completed with errors: {errors}")
        return results

    def _load_dataset(self, input_key: str) -> Any:
        """
        Load a single dataset.

        Args:
            input_key: The key identifying the dataset to load

        Returns:
            The loaded dataset
        """
        config = self._get_dataset_config(input_key)
        format_name = config.get("format", "").lower()

        if format_name not in self.FORMAT_READERS:
            raise ValueError(f"Format '{format_name}' not supported for '{input_key}'")

        reader_method = getattr(self, self.FORMAT_READERS[format_name])

        # SQL queries don't require a filepath
        if format_name == "query":
            return reader_method(config)
        else:
            filepath = self._get_filepath(config, input_key)
            return reader_method(filepath, config)

    def _get_input_keys(self, node: Dict[str, Any]) -> List[str]:
        """
        Get input keys from a node configuration.

        Args:
            node: Node configuration dictionary

        Returns:
            List of input keys
        """
        keys = node.get("input", [])
        return keys if isinstance(keys, list) else [keys]

    def _get_dataset_config(self, input_key: str) -> Dict[str, Any]:
        """
        Get configuration for a dataset.

        Args:
            input_key: The key identifying the dataset

        Returns:
            Configuration dictionary for the dataset

        Raises:
            ValueError: If configuration is missing
        """
        config = self.context.input_config.get(input_key)
        if not config:
            raise ValueError(f"Missing configuration for '{input_key}'")
        return config

    def _get_filepath(self, config: Dict[str, Any], input_key: str) -> str:
        """
        Get filepath for a dataset.

        Args:
            config: Dataset configuration dictionary
            input_key: The key identifying the dataset

        Returns:
            Filepath string

        Raises:
            ValueError: If filepath is missing
            FileNotFoundError: If file doesn't exist in local mode
        """
        path = config.get("filepath")
        if not path:
            raise ValueError(f"Missing filepath for '{input_key}'")

        # Verify file existence in local mode
        if self.context.execution_mode == "local" and not os.path.exists(path):
            raise FileNotFoundError(f"File '{path}' does not exist in local mode")
        return path

    def _register_custom_formats(self) -> None:
        """
        Register custom format handlers if available.

        This method attempts to load and configure dependencies for special formats.
        """
        format_checks = {"delta": self._try_import_delta, "xml": self._try_import_xml}

        for format_name, check_method in format_checks.items():
            if format_name in self.FORMAT_READERS:
                try:
                    check_method()
                except Exception as e:
                    logger.error(f"Error registering format {format_name}: {e}")

    def _try_import_delta(self) -> None:
        """
        Try to import Delta Lake dependencies.

        Raises:
            ImportError: If delta-spark package is not installed
        """
        try:
            from delta import configure_spark_with_delta_pip
        except ImportError:
            logger.error(
                "Package 'delta-spark' not installed. Install it with: pip install delta-spark"
            )
            raise

    def _try_import_xml(self) -> None:
        """
        Try to verify XML dependencies are available.
        """
        try:
            self.context.spark._jvm.com.databricks.spark.xml
        except Exception:
            logger.warning("XML format configured, but library not available.")

    # Format-specific reader methods
    def _read_parquet(self, filepath: str, config: Dict[str, Any]) -> Any:
        """
        Read data in Parquet format.

        Args:
            filepath: Path to the Parquet file or directory
            config: Configuration options

        Returns:
            Loaded dataset
        """
        return self._spark_read("parquet", filepath, config)

    def _read_json(self, filepath: str, config: Dict[str, Any]) -> Any:
        """
        Read data in JSON format.

        Args:
            filepath: Path to the JSON file or directory
            config: Configuration options

        Returns:
            Loaded dataset
        """
        return self._spark_read("json", filepath, config)

    def _read_csv(self, filepath: str, config: Dict[str, Any]) -> Any:
        """
        Read data in CSV format.

        Args:
            filepath: Path to the CSV file or directory
            config: Configuration options

        Returns:
            Loaded dataset
        """
        # Ensure header option is set by default
        options = config.get("options", {})
        options.setdefault("header", "true")
        return self._spark_read("csv", filepath, {**config, "options": options})

    def _read_orc(self, filepath: str, config: Dict[str, Any]) -> Any:
        """
        Read data in ORC format.

        Args:
            filepath: Path to the ORC file or directory
            config: Configuration options

        Returns:
            Loaded dataset
        """
        return self._spark_read("orc", filepath, config)

    def _read_avro(self, filepath: str, config: Dict[str, Any]) -> Any:
        """
        Read data in Avro format.

        Args:
            filepath: Path to the Avro file or directory
            config: Configuration options

        Returns:
            Loaded dataset
        """
        return self._spark_read("avro", filepath, config)

    def _read_delta(self, filepath: str, config: Dict[str, Any]) -> Any:
        """
        Read data in Delta Lake format.

        Args:
            filepath: Path to the Delta Lake table
            config: Configuration options

        Returns:
            Loaded dataset
        """
        reader = self.context.spark.read.options(**config.get("options", {})).format(
            "delta"
        )

        # Handle time travel queries
        if version := config.get("version"):
            return reader.option("versionAsOf", version).load(filepath)
        if timestamp := config.get("timestamp"):
            return reader.option("timestampAsOf", timestamp).load(filepath)
        return reader.load(filepath)

    def _read_pickle(self, filepath: str, config: Dict[str, Any]) -> Any:
        """
        Read data in pickle format.

        Args:
            filepath: Path to the pickle file
            config: Configuration options

        Returns:
            Loaded dataset
        """
        import pickle

        use_pandas = config.get("use_pandas", False)
        if self.context.execution_mode == "local" or use_pandas:
            import pandas as pd

            logger.info(f"Reading pickle file using local method: {filepath}")
            with open(filepath, "rb") as f:
                data = pickle.load(f)
            # Convert pandas DataFrame to Spark DataFrame if needed
            return (
                self.context.spark.createDataFrame(data)
                if isinstance(data, pd.DataFrame) and not use_pandas
                else data
            )

        # Distributed reading with Spark
        logger.info(f"Reading pickle file using distributed method: {filepath}")
        rdd = self.context.spark.sparkContext.binaryFiles(filepath).map(
            lambda x: pickle.loads(x[1])
        )
        return (
            self.context.spark.createDataFrame(rdd)
            if config.get("to_dataframe", True)
            else rdd
        )

    def _read_xml(self, filepath: str, config: Dict[str, Any]) -> Any:
        """
        Read data in XML format.

        Args:
            filepath: Path to the XML file
            config: Configuration options

        Returns:
            Loaded dataset
        """
        row_tag = config.get("rowTag", "row")
        logger.info(f"Reading XML file with row tag '{row_tag}': {filepath}")
        return (
            self.context.spark.read.format("com.databricks.spark.xml")
            .option("rowTag", row_tag)
            .options(**config.get("options", {}))
            .load(filepath)
        )

    def _read_query(self, config: Dict[str, Any]) -> Any:
        """
        Execute a SQL query.

        Args:
            config: Configuration containing the SQL query

        Returns:
            Query result dataset

        Raises:
            ValueError: If query is missing
        """
        if not (query := config.get("query")):
            raise ValueError("Query format specified without SQL query")

        logger.info(f"Executing SQL query: {query[:100]}...")  # Log first 100 chars
        return self.context.spark.sql(query)

    def _spark_read(self, fmt: str, filepath: str, config: Dict[str, Any]) -> Any:
        """
        Generic method for reading data with Spark.

        Args:
            fmt: Format identifier (parquet, json, etc.)
            filepath: Path to the data source
            config: Configuration options

        Returns:
            Loaded dataset
        """
        logger.info(f"Reading {fmt.upper()} data from: {filepath}")
        return (
            self.context.spark.read.options(**config.get("options", {}))
            .format(fmt)
            .load(filepath)
        )
