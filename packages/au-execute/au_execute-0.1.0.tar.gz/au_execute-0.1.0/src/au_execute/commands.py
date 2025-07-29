from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from loguru import logger


class Command(ABC):
    """
    Abstract base class for command pattern implementation.

    The Command pattern encapsulates a request as an object, allowing for
    parameterization of clients with different requests, queuing of requests,
    and logging of operations.
    """

    @abstractmethod
    def execute(self) -> Any:
        """
        Executes the command and returns the result.

        Returns:
            Any: The result of the command execution.
        """
        pass


class NodeCommand(Command):
    """
    Command implementation for executing a specific node in a data pipeline.

    This class handles the execution of a function with input dataframes and date range parameters.
    """

    def __init__(
        self, function: Callable, input_dfs: List[Any], start_date: str, end_date: str
    ):
        """
        Initialize a NodeCommand.

        Args:
            function (Callable): The function to execute.
            input_dfs (List[Any]): List of input dataframes or data objects.
            start_date (str): Start date for data processing.
            end_date (str): End date for data processing.
        """
        self.function = function
        self.input_dfs = input_dfs
        self.start_date = start_date
        self.end_date = end_date

    def execute(self) -> Any:
        """
        Executes the node function with the specified parameters.

        Returns:
            Any: The result of the function execution.
        """
        logger.info(
            f"Executing node with date range: {self.start_date} to {self.end_date}"
        )
        return self.function(*self.input_dfs, self.start_date, self.end_date)


class MLNodeCommand(NodeCommand):
    """
    Command implementation for executing a machine learning node in a pipeline.

    Extends NodeCommand with ML-specific functionality including model versioning
    and hyperparameter configuration.
    """

    def __init__(
        self,
        function: Callable,
        input_dfs: List[Any],
        start_date: str,
        end_date: str,
        model_version: str,
        hyperparams: Optional[Dict[str, Any]] = None,
        spark=None,
    ):
        """
        Initialize an MLNodeCommand.

        Args:
            function (Callable): The function to execute.
            input_dfs (List[Any]): List of input dataframes or data objects.
            start_date (str): Start date for data processing.
            end_date (str): End date for data processing.
            model_version (str): Version identifier of the ML model to use.
            hyperparams (Optional[Dict[str, Any]], optional): Hyperparameters for the ML model.
                                                             Defaults to None (empty dict).
            spark: Spark session object for distributed computing. Defaults to None.
        """
        super().__init__(function, input_dfs, start_date, end_date)
        self.model_version = model_version
        self.hyperparams = hyperparams or {}
        self.spark = spark

    def execute(self) -> Any:
        """
        Executes the ML node function with the specified parameters.

        Configures Spark with ML hyperparameters if a Spark session is available.

        Returns:
            Any: The result of the function execution.
        """
        # Configure ML parameters in Spark if available
        if self.spark:
            self._configure_spark_parameters()

        logger.info(f"Executing ML node with model version: {self.model_version}")
        if self.hyperparams:
            logger.debug(f"Using hyperparameters: {self.hyperparams}")

        return super().execute()

    def _configure_spark_parameters(self) -> None:
        """
        Configure ML-related parameters in the Spark session.

        Private helper method to set hyperparameters and model version in Spark configuration.
        """
        for param_name, param_value in self.hyperparams.items():
            self.spark.conf.set(f"ml.hyperparams.{param_name}", str(param_value))
        self.spark.conf.set("ml.model_version", self.model_version)
