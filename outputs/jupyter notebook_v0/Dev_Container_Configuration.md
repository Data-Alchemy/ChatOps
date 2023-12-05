# VS Code Dev Container for PySpark with Hive and Apache Derby

This project sets up a development environment in a Docker container for running PySpark with Hive and Apache Derby using a Jupyter notebook.

## Prerequisites

- Docker
- Visual Studio Code
- VS Code Remote - Containers extension

## Setup

1. Clone this repository.
2. Open the project in VS Code.
3. When prompted to "Reopen in Container", click "Reopen in Container". This will start building the Docker image. If not prompted, press `F1` and select `Remote-Containers: Reopen Folder in Container`.

## Structure

- `Dockerfile`: Defines the Docker image including all dependencies.
- `.devcontainer/devcontainer.json`: Configuration for the VS Code Remote - Containers extension.
- `notebooks/`: Directory for Jupyter notebooks.
- `data/`: Directory for data files.
- `scripts/`: Directory for scripts.
- `requirements.txt`: Python dependencies.

## Dockerfile

The Dockerfile defines a Docker image with all the necessary dependencies for running PySpark with Hive and Apache Derby.