import mlflow
import pandas as pd
import numpy as np
from deepchecks.tabular import Dataset
from deepchecks.tabular.suites import data_integrity, train_test_validation
from functools import wraps
from rich.console import Console
from rich.table import Table
import os

class SmartDeployMiguel:
    def __init__(self, reference_data: pd.DataFrame = None, model_name: str = None):
        """
        Initialize the monitor with reference data and configure MLflow.

        Args:
            reference_data (pd.DataFrame, optional): Reference dataset for drift validation.
            model_name (str): MLflow experiment name to log runs under.
        """
        if model_name is None:
            raise ValueError("You must specify a model name ('model_name') to correctly register experiments in MLflow. This improves tracking and analysis of model results.")

        self.reference_data = reference_data
        self.model_name = model_name
        mlflow.set_experiment(model_name)
        self.console = Console()

    def integrity(self, data: pd.DataFrame) -> dict:
        """
        Run data integrity validation using Deepchecks.

        Args:
            data (pd.DataFrame): Dataset to validate.

        Returns:
            dict: Structured validation results.
        """
        dataset = Dataset(data)
        suite = data_integrity()
        results = suite.run(dataset)
        self.save_integrity_flag(results.passed())
        return self.format_results_integrity(results)

    def format_results_integrity(self, results) -> dict:
        """
        Format and display integrity results using Rich.

        Args:
            results: Raw Deepchecks result object.

        Returns:
            dict: {check_name: (passed, details)}
        """
        formatted = {}
        table = Table(title="[bold green]Integrity Check Results[/bold green]", show_lines=True)
        table.add_column("Check", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Details", style="magenta")

        for check in results.results:
            check_name = check.check.name()
            status = check.passed()
            details = check.display[0] if check.display else "No issues"

            formatted[check_name] = (status, details)
            status_display = "[green]PASS[/green]" if status else "[red]FAIL[/red]"
            table.add_row(check_name, status_display, str(details))

        self.console.print(table)
        return formatted

    def infer_input(self, input_path: str) -> str:
        """
        Infer the input type (tabular/image) based on file extension.

        Args:
            input_path (str): Path to input file.

        Returns:
            str: Either 'tabular' or 'image'.
        """
        image_exts = ['.jpg', '.jpeg', '.png', '.bmp']
        ext = os.path.splitext(input_path)[1].lower()

        if ext in image_exts:
            return 'image'
        elif ext in ['.csv', '.parquet']:
            return 'tabular'
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def save_integrity_flag(self, passed: bool):
        """
        Log integrity result to MLflow.

        Args:
            passed (bool): Result of integrity validation.
        """
        mlflow.log_param("data_integrity_passed", str(passed))

    def pass_integrity_check(self) -> bool:
        """
        Check if the last integrity validation passed.

        Returns:
            bool: True if integrity passed.
        """
        run_id = mlflow.active_run().info.run_id if mlflow.active_run() else None
        if run_id:
            param = mlflow.get_run(run_id).data.params.get("data_integrity_passed", "False")
            return param.lower() == "true"
        return False

    def check_integrity(self, func):
        """
        Decorator to prevent function execution if integrity check failed.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.pass_integrity_check():
                self.console.print("[bold red]ERROR:[/bold red] Integrity check failed!")
                raise RuntimeError("Data integrity validation failed. Please review the results before proceeding.")
            return func(*args, **kwargs)
        return wrapper

    def drift(self, current_data: pd.DataFrame) -> dict:
        """
        Detect drift between current and reference dataset.

        Args:
            current_data (pd.DataFrame): Current production dataset.

        Returns:
            dict: Structured drift results.
        """
        if self.reference_data is None:
            raise ValueError("A reference dataset ('reference_data') is required to perform data drift validation. Please provide it when initializing the class.")

        ref_dataset = Dataset(self.reference_data)
        curr_dataset = Dataset(current_data)
        suite = train_test_validation()
        results = suite.run(ref_dataset, curr_dataset)
        self.save_drift_flag(results.passed())
        return self.format_results_integrity(results)

    def save_drift_flag(self, passed: bool):
        """
        Log data drift result to MLflow.

        Args:
            passed (bool): True if drift is within acceptable range.
        """
        mlflow.log_param("data_drift_passed", str(passed))

    def pass_drift_check(self) -> bool:
        """
        Check if the last drift validation passed.

        Returns:
            bool: True if no significant drift was detected.
        """
        run_id = mlflow.active_run().info.run_id if mlflow.active_run() else None
        if run_id:
            param = mlflow.get_run(run_id).data.params.get("data_drift_passed", "False")
            return param.lower() == "true"
        return False

    def check_drift(self, func):
        """
        Decorator to prevent function execution if drift was detected.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.pass_drift_check():
                self.console.print("[bold red]ALERT:[/bold red] Data drift detected!")
                raise RuntimeError("Significant data drift detected. Stop the process and investigate the differences with the reference dataset.")
            return func(*args, **kwargs)
        return wrapper
