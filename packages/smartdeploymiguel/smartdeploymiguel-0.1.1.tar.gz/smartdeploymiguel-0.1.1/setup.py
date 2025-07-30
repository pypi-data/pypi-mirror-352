from setuptools import setup, find_packages

setup(
    name="smartdeploymiguel",
    version="0.1.1",
    description="Data integrity and drift validation for ML pipelines using Deepchecks and MLflow.",
    author="Miguel Angel",
    author_email="miguelsff@gmail.com",
    url="https://github.com/tuusuario/smartdeploymiguel",
    packages=find_packages(),
    install_requires=[
        "pandas==1.5.3",
        "scikit-learn==1.1.3",
        "mlflow==2.11.3",
        "joblib==1.3.2",
        "deepchecks==0.17.1",
        "fastapi==0.111.0",
        "uvicorn==0.19.0",
        "ray[default]==2.9.3",
        "python-multipart==0.0.9",
        "pydantic==1.10.13",
        "rich==13.7.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
