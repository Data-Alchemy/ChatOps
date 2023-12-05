# Azure Function App

This is a Python Azure Function App that runs on a timer trigger. The function logs the current UTC timestamp every time it runs.

## Files

- `__init__.py`: This is the main Python file that contains the function code.
- `function.json`: This is the function configuration file. It defines the function bindings and other configuration settings.
- `host.json`: This is the host configuration file. It defines the version and other global configuration settings.
- `local.settings.json`: This is the local settings file. It contains all the app settings, connection strings, and settings for local development.
- `requirements.txt`: This is the requirements file. It lists all the Python dependencies that the function needs to run.

## How to run

1. Make sure you have the Azure Functions Core Tools installed.
2. Navigate to the function app directory.
3. Install the Python dependencies with `pip install -r requirements.txt`.
4. Start the function app with `func start`.