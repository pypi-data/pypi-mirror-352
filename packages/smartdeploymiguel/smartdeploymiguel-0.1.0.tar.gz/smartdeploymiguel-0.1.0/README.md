# SmartDeployMiguel

SmartDeployMiguel is a Python library designed to simplify data integrity validation and data drift detection in Machine Learning workflows. It integrates with popular tools like MLflow, Deepchecks, and Rich to provide structured validations and experiment tracking.

## 🚀 Features

- Validate data integrity using Deepchecks.
- Detect data drift between reference and production datasets.
- Log validation results directly to MLflow.
- Use decorators to block execution if data checks fail.
- CLI-friendly output using Rich tables.

## 🧰 Requirements

- Python >= 3.7
- mlflow
- pandas
- numpy
- deepchecks
- rich

## 📦 Installation

```bash
pip install smartdeploymiguel
