from setuptools import setup, find_packages

setup(
    name="smartdeploymiguel",
    version="0.1.0",
    description="Data integrity and drift validation for ML pipelines using Deepchecks and MLflow.",
    author="Miguel Angel",
    author_email="miguelsff@gmail.com",
    url="https://github.com/tuusuario/smartdeploymiguel",
    packages=find_packages(),
    install_requires=[
        "mlflow",
        "pandas",
        "numpy",
        "deepchecks",
        "rich"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
