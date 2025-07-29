import importlib
from typing import Any, Dict, Optional, Callable
from au_execute.commands import Command, NodeCommand, MLNodeCommand
from au_iomanager import InputLoader, OutputManager
from loguru import logger
from auconfig import Context


class PipelineExecutor:
    """
    Executes data pipelines based on the layer type (ML or standard).

    This class handles the execution of both standard data processing and machine learning
    pipelines, providing a unified interface for running complete pipelines or individual nodes.

    Attributes:
        context (Context): Application context containing configuration and settings
        input_loader (InputLoader): Component for loading input data
        output_manager (OutputManager): Component for saving output data
        is_ml_layer (bool): Flag indicating if this is a machine learning layer
    """

    def __init__(self, context: Context):
        """
        Initialize the pipeline executor with application context.

        Args:
            context (Context): Application context containing configuration and settings
        """
        self.context = context
        self.input_loader = InputLoader(context)
        self.output_manager = OutputManager(context)
        self.is_ml_layer = context.layer == "ml"

    def run_pipeline(
        self,
        env: Optional[str] = None,
        pipeline_name: Optional[str] = None,
        node_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        model_version: Optional[str] = None,
        hyperparams: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Main entry point for executing pipelines of any type.

        This method serves as a unified interface to run both standard data pipelines
        and ML pipelines, automatically determining the execution path based on the layer type.

        Args:
            env (str, optional): Execution environment
            pipeline_name (str, optional): Name of the pipeline to execute
            node_name (str, optional): Name of a specific node to execute
            start_date (str, optional): Start date for data processing
            end_date (str, optional): End date for data processing
            model_version (str, optional): Version of the ML model to use
            hyperparams (Dict[str, Any], optional): Hyperparameters for ML models

        Raises:
            ValueError: If required parameters are missing
        """
        # Validate and prepare parameters
        self._validate_required_params(pipeline_name, start_date, end_date)
        pipeline = self._get_pipeline_config(pipeline_name)

        # Resolve dates from parameters or global settings
        start_date = start_date or self.context.global_settings.get("start_date")
        end_date = end_date or self.context.global_settings.get("end_date")

        # Execute appropriate flow based on layer type
        if self.is_ml_layer:
            model_version = model_version or self.context.global_settings.get(
                "default_model_version", "latest"
            )
            logger.info(
                f"Running ML pipeline '{pipeline_name}' with model version '{model_version}'"
            )
            self._execute_ml_flow(
                env,
                pipeline,
                node_name,
                start_date,
                end_date,
                model_version,
                hyperparams,
            )
        else:
            logger.info(f"Running standard pipeline '{pipeline_name}'")
            self._execute_standard_flow(env, pipeline, node_name, start_date, end_date)

    def _validate_required_params(
        self,
        pipeline_name: Optional[str],
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> None:
        """
        Validate required parameters for pipeline execution.

        Args:
            pipeline_name (str, optional): Name of the pipeline
            start_date (str, optional): Start date
            end_date (str, optional): End date

        Raises:
            ValueError: If any required parameter is missing
        """
        if not pipeline_name:
            raise ValueError("Pipeline name is required")

        if not (start_date or self.context.global_settings.get("start_date")):
            raise ValueError("Start date is required")

        if not (end_date or self.context.global_settings.get("end_date")):
            raise ValueError("End date is required")

    def _get_pipeline_config(self, pipeline_name: str) -> Dict[str, Any]:
        """
        Get pipeline configuration from the context.

        Args:
            pipeline_name (str): Name of the pipeline

        Returns:
            Dict[str, Any]: Pipeline configuration

        Raises:
            ValueError: If pipeline configuration is not found
        """
        pipeline = self.context.pipelines.get(pipeline_name)
        if not pipeline:
            raise ValueError(f"Pipeline '{pipeline_name}' not found")
        return pipeline

    def _execute_standard_flow(
        self,
        env: Optional[str],
        pipeline: Dict[str, Any],
        node_name: Optional[str],
        start_date: str,
        end_date: str,
    ) -> None:
        """
        Execute a standard data pipeline.

        This method handles execution of standard data processing pipelines,
        either running a single node or the complete pipeline sequence.

        Args:
            env (str, optional): Execution environment
            pipeline (Dict[str, Any]): Pipeline configuration
            node_name (str, optional): Name of a specific node to execute
            start_date (str): Start date for data processing
            end_date (str): End date for data processing
        """
        if node_name:
            logger.info(f"Running single standard node: '{node_name}'")
            self._run_single_node(node_name, start_date, end_date)
        else:
            self._run_complete_pipeline(env, pipeline, start_date, end_date)

    def _execute_ml_flow(
        self,
        env: Optional[str],
        pipeline: Dict[str, Any],
        node_name: Optional[str],
        start_date: str,
        end_date: str,
        model_version: str,
        hyperparams: Optional[Dict[str, Any]],
    ) -> None:
        """
        Execute a machine learning pipeline.

        This method handles execution of ML pipelines,
        either running a single ML node or the complete ML pipeline sequence.

        Args:
            env (str, optional): Execution environment
            pipeline (Dict[str, Any]): Pipeline configuration
            node_name (str, optional): Name of a specific node to execute
            start_date (str): Start date for data processing
            end_date (str): End date for data processing
            model_version (str): Version of the ML model to use
            hyperparams (Dict[str, Any], optional): Hyperparameters for ML models
        """
        if node_name:
            logger.info(f"Running single ML node: '{node_name}'")
            self._run_single_ml_node(
                env, node_name, start_date, end_date, model_version, hyperparams
            )
        else:
            self._run_complete_ml_pipeline(
                env, pipeline, start_date, end_date, model_version, hyperparams
            )

    def _run_complete_pipeline(
        self,
        env: Optional[str],
        pipeline: Dict[str, Any],
        start_date: str,
        end_date: str,
    ) -> None:
        """
        Execute a complete standard pipeline with all its nodes.

        Args:
            env (str, optional): Execution environment
            pipeline (Dict[str, Any]): Pipeline configuration
            start_date (str): Start date for data processing
            end_date (str): End date for data processing
        """
        node_count = len(pipeline["nodes"])
        logger.info(f"Starting standard pipeline execution with {node_count} nodes")

        for index, node in enumerate(pipeline["nodes"], 1):
            logger.info(f"Processing node {index}/{node_count}: '{node['name']}'")
            self._run_single_node(node["name"], start_date, end_date)

        logger.info("Standard pipeline completed successfully")

    def _run_complete_ml_pipeline(
        self,
        env: Optional[str],
        pipeline: Dict[str, Any],
        start_date: str,
        end_date: str,
        model_version: str,
        hyperparams: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Execute a complete ML pipeline with all its nodes.

        Args:
            env (str, optional): Execution environment
            pipeline (Dict[str, Any]): Pipeline configuration
            start_date (str): Start date for data processing
            end_date (str): End date for data processing
            model_version (str): Version of the ML model to use
            hyperparams (Dict[str, Any], optional): Hyperparameters for ML models
        """
        node_count = len(pipeline["nodes"])
        logger.info(f"Starting ML pipeline execution with {node_count} nodes")

        for index, node in enumerate(pipeline["nodes"], 1):
            logger.info(f"Processing ML node {index}/{node_count}: '{node['name']}'")
            self._run_single_ml_node(
                env, node["name"], start_date, end_date, model_version, hyperparams
            )

        logger.info("ML pipeline completed successfully")

    def _run_single_node(
        self,
        node_name: str,
        start_date: str,
        end_date: str,
    ) -> None:
        """
        Execute a single standard node.

        Args:
            node_name (str): Name of the node to execute
            start_date (str): Start date for data processing
            end_date (str): End date for data processing
        """
        node = self._get_node_config(node_name)
        function = self._load_node_function(node)

        logger.info(f"Executing standard node: '{node_name}'")

        # Load data, execute node and save results
        input_dfs = self.input_loader.load_inputs(node)
        command = NodeCommand(function, input_dfs, start_date, end_date)
        result_df = self._execute_command(command)

        self.output_manager.save_output(node, result_df)
        logger.info(f"Node '{node_name}' completed successfully")

    def _run_single_ml_node(
        self,
        env: Optional[str],
        node_name: str,
        start_date: str,
        end_date: str,
        model_version: str,
        hyperparams: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Execute a single ML node.

        Args:
            env (str, optional): Execution environment
            node_name (str): Name of the node to execute
            start_date (str): Start date for data processing
            end_date (str): End date for data processing
            model_version (str): Version of the ML model to use
            hyperparams (Dict[str, Any], optional): Hyperparameters for ML models
        """
        node = self._get_node_config(node_name)
        function = self._load_node_function(node)

        logger.info(f"Executing ML node: '{node_name}' (version: {model_version})")

        # Load data, execute node and save results
        input_dfs = self.input_loader.load_inputs(node)
        command = MLNodeCommand(
            function,
            input_dfs,
            start_date,
            end_date,
            model_version,
            hyperparams,
            spark=self.context.spark,  # Pass spark session
        )
        result_df = self._execute_command(command)

        self.output_manager.save_ml_output(node, env, result_df, model_version)
        logger.info(f"ML node '{node_name}' completed successfully")

    def _get_node_config(self, node_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific node.

        Args:
            node_name (str): Name of the node

        Returns:
            Dict[str, Any]: Node configuration

        Raises:
            ValueError: If node configuration is not found
        """
        node = self.context.nodes_config.get(node_name)
        if not node:
            raise ValueError(f"Node '{node_name}' not found")
        return node

    def _load_node_function(self, node: Dict[str, Any]) -> Callable:
        """
        Load a node's function from its corresponding module.

        Args:
            node (Dict[str, Any]): Node configuration

        Returns:
            Callable: The node function

        Raises:
            ValueError: If module/function configuration is missing
            ImportError: If module cannot be imported
            AttributeError: If function cannot be found in module
        """
        module_path = node.get("module")
        function_name = node.get("function")

        if not module_path or not function_name:
            raise ValueError("Missing module/function configuration in node")

        try:
            logger.debug(
                f"Loading function '{function_name}' from module '{module_path}'"
            )
            module = importlib.import_module(module_path)
            return getattr(module, function_name)
        except ImportError as e:
            logger.error(f"Failed to import module {module_path}: {str(e)}")
            raise
        except AttributeError as e:
            logger.error(
                f"Function {function_name} not found in {module_path}: {str(e)}"
            )
            raise

    def _execute_command(self, command: Command) -> Any:
        """
        Execute a command and return its result.

        Args:
            command (Command): Command to execute

        Returns:
            Any: Result dataframe from command execution
        """
        logger.debug("Executing command")
        result_df = command.execute()

        # Log schema information
        logger.debug("Result dataframe schema:")
        result_df.printSchema()

        return result_df
